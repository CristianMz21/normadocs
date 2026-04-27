"""Unit tests for APAVerifier orchestrator."""

import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

from normadocs.models import DocumentMetadata
from normadocs.verifier.apa_verifier import APAVerifier, VerificationContext


class TestAPAVerifier(unittest.TestCase):
    """Tests for APAVerifier orchestrator."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create test DOCX fixtures."""
        with NamedTemporaryFile(delete=False, suffix=".docx", mode="w") as f:
            cls.temp_dir = Path(f.name).parent
        cls.temp_dir.mkdir(exist_ok=True)

    def _create_simple_docx(self) -> Path:
        """Create a minimal DOCX."""
        from docx import Document
        from docx.shared import Inches

        path = self.temp_dir / "test_simple.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        doc.add_paragraph("First paragraph.")
        doc.add_paragraph("Second paragraph.")

        doc.save(str(path))
        return path

    def _create_mock_pdf_path(self) -> Path:
        """Create a mock PDF path that doesn't exist."""
        return self.temp_dir / "mock_output.pdf"

    def test_verification_context_creation(self) -> None:
        """Test VerificationContext can be created."""
        mock_pdf = MagicMock()
        mock_docx = MagicMock()
        meta = DocumentMetadata(title="Test Document")

        ctx = VerificationContext(pdf=mock_pdf, docx=mock_docx, meta=meta, strict=False)

        assert ctx.pdf is mock_pdf
        assert ctx.docx is mock_docx
        assert ctx.meta is meta
        assert ctx.strict is False

    def test_verification_context_strict_mode(self) -> None:
        """Test VerificationContext strict mode."""
        mock_pdf = MagicMock()
        mock_docx = MagicMock()
        meta = DocumentMetadata(title="Test Document")

        ctx = VerificationContext(pdf=mock_pdf, docx=mock_docx, meta=meta, strict=True)

        assert ctx.strict is True

    def test_verifier_initialization(self) -> None:
        """Test APAVerifier can be initialized."""
        docx_path = self._create_simple_docx()
        pdf_path = self._create_mock_pdf_path()

        try:
            verifier = APAVerifier(pdf_path=pdf_path, docx_path=docx_path)
            assert verifier.pdf_path == pdf_path
            assert verifier.docx_path == docx_path
        finally:
            docx_path.unlink(missing_ok=True)

    def test_verifier_initialization_with_metadata(self) -> None:
        """Test APAVerifier with metadata."""
        docx_path = self._create_simple_docx()
        pdf_path = self._create_mock_pdf_path()
        meta = DocumentMetadata(title="Test Document")

        try:
            verifier = APAVerifier(pdf_path=pdf_path, docx_path=docx_path, meta=meta)
            assert verifier.meta is meta
        finally:
            docx_path.unlink(missing_ok=True)

    def test_verifier_initialization_strict_mode(self) -> None:
        """Test APAVerifier with strict mode."""
        docx_path = self._create_simple_docx()
        pdf_path = self._create_mock_pdf_path()

        try:
            verifier = APAVerifier(pdf_path=pdf_path, docx_path=docx_path, strict=True)
            assert verifier.strict is True
        finally:
            docx_path.unlink(missing_ok=True)

    def test_init_checks_returns_checks(self) -> None:
        """Test that _init_checks returns all expected checks."""
        docx_path = self._create_simple_docx()
        pdf_path = self._create_mock_pdf_path()

        try:
            verifier = APAVerifier(pdf_path=pdf_path, docx_path=docx_path)
            checks = verifier._init_checks()

            assert len(checks) == 11
            check_categories = [c[0] for c in checks]
            assert "margins" in check_categories
            assert "fonts" in check_categories
            assert "spacing" in check_categories
            assert "headings" in check_categories
            assert "paragraphs" in check_categories
        finally:
            docx_path.unlink(missing_ok=True)


class TestVerificationResult(unittest.TestCase):
    """Tests for VerificationResult structure."""

    def test_result_structure(self) -> None:
        """Test that verification result has expected structure."""
        from normadocs.verifier import VerificationResult

        result = VerificationResult(
            passed=True,
            score=100.0,
            issues=[],
        )

        assert result.passed is True
        assert result.score == 100.0

    def test_result_with_issues(self) -> None:
        """Test verification result with issues."""
        from normadocs.verifier import CheckCategory, VerificationIssue, VerificationResult

        issue = VerificationIssue(
            check=f"{CheckCategory.MARGINS}.top",
            severity="error",
            expected="1.0 inches",
            actual="2.0 inches",
        )

        result = VerificationResult(
            passed=False,
            score=80.0,
            issues=[issue],
        )

        assert result.passed is False
        assert len(result.issues) == 1
        assert result.issues[0].check == "margins.top"


if __name__ == "__main__":
    unittest.main()

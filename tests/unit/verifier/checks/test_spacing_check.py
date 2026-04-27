"""Unit tests for SpacingCheck - APA 7th Edition line spacing verification."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from docx.shared import Inches, Pt

from normadocs.models import DocumentMetadata
from normadocs.verifier.apa_verifier import APAVerifier, VerificationContext
from normadocs.verifier.checks.spacing import SpacingCheck


class TestSpacingCheckCompliant(unittest.TestCase):
    """Tests for APA-compliant double spacing (should pass)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx_with_spacing(self, line_spacing: float) -> Path:
        path = self.temp_path / f"spacing_{line_spacing}.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(5):
            para = doc.add_paragraph()
            para.paragraph_format.line_spacing = line_spacing
            run = para.add_run(f"Paragraph {i + 1} with line spacing {line_spacing}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        doc.save(str(path))
        return path

    def _run_check(self, docx_path: Path) -> list:
        pdf_path = self.temp_path / "output.pdf"
        pdf_path.touch()
        meta = DocumentMetadata(title="Test Document")
        verifier = APAVerifier(pdf_path=pdf_path, docx_path=docx_path, meta=meta)
        ctx = VerificationContext(
            pdf=verifier.pdf,
            docx=verifier.docx,
            meta=meta,
            strict=False,
        )
        check = SpacingCheck()
        return check.run(ctx)

    def test_exact_double_spacing_passes(self) -> None:
        """Exactly 2.0 line spacing should pass with no errors."""
        docx_path = self._create_docx_with_spacing(2.0)
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        self.assertEqual(errors, [], f"Expected no errors for 2.0 spacing but got: {errors}")

    def test_double_spacing_within_tolerance_passes(self) -> None:
        """Line spacing within 0.2 of 2.0 should pass."""
        docx_path = self._create_docx_with_spacing(2.15)
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        self.assertEqual(errors, [], f"Expected no errors for 2.15 spacing but got: {errors}")


class TestSpacingCheckViolation(unittest.TestCase):
    """Tests for spacing violations (should fail with errors)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx_with_spacing(self, line_spacing: float) -> Path:
        path = self.temp_path / f"spacing_{line_spacing}.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(5):
            para = doc.add_paragraph()
            para.paragraph_format.line_spacing = line_spacing
            run = para.add_run(f"Paragraph {i + 1}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        doc.save(str(path))
        return path

    def _create_mixed_spacing_docx(self, correct_count: int, wrong_count: int) -> Path:
        """Create document with mixed spacing."""
        path = self.temp_path / "mixed_spacing.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(correct_count):
            para = doc.add_paragraph()
            para.paragraph_format.line_spacing = 2.0
            run = para.add_run(f"Correct spacing paragraph {i + 1}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        for i in range(wrong_count):
            para = doc.add_paragraph()
            para.paragraph_format.line_spacing = 1.0
            run = para.add_run(f"Wrong spacing paragraph {i + 1}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        doc.save(str(path))
        return path

    def _run_check(self, docx_path: Path) -> list:
        pdf_path = self.temp_path / "output.pdf"
        pdf_path.touch()
        meta = DocumentMetadata(title="Test Document")
        verifier = APAVerifier(pdf_path=pdf_path, docx_path=docx_path, meta=meta)
        ctx = VerificationContext(
            pdf=verifier.pdf,
            docx=verifier.docx,
            meta=meta,
            strict=False,
        )
        check = SpacingCheck()
        return check.run(ctx)

    def test_single_spacing_raises_error(self) -> None:
        """Single spacing (1.0) should raise error (>50% wrong)."""
        docx_path = self._create_docx_with_spacing(1.0)
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        self.assertGreater(len(errors), 0, f"Expected error for single spacing but got: {issues}")

    def test_1_5_spacing_raises_error(self) -> None:
        """1.5 spacing should raise error (outside tolerance of 2.0)."""
        docx_path = self._create_docx_with_spacing(1.5)
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        self.assertGreater(len(errors), 0, f"Expected error for 1.5 spacing but got: {issues}")

    def test_mixed_spacing_majority_wrong_raises_error(self) -> None:
        """3 wrong out of 5 should raise error (>50% wrong)."""
        docx_path = self._create_mixed_spacing_docx(correct_count=2, wrong_count=3)
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        self.assertGreater(len(errors), 0, f"Expected error when majority wrong but got: {issues}")

    def test_mixed_spacing_some_wrong_raises_warning(self) -> None:
        """1 wrong out of 5 should raise warning (not >50% wrong)."""
        docx_path = self._create_mixed_spacing_docx(correct_count=4, wrong_count=1)
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        self.assertEqual(errors, [], f"Expected no errors when <50% wrong but got: {errors}")
        self.assertGreater(len(warnings), 0, f"Expected warning when some wrong but got: {issues}")


if __name__ == "__main__":
    unittest.main()

"""Unit tests for ParagraphsCheck - APA 7th Edition paragraph formatting."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from normadocs.models import DocumentMetadata
from normadocs.verifier.apa_verifier import APAVerifier, VerificationContext
from normadocs.verifier.checks.paragraphs import ParagraphsCheck


class TestParagraphsCheckCompliant(unittest.TestCase):
    """Tests for APA-compliant paragraph formatting (should pass)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx(
        self,
        first_line_indent_inches: float = 0.5,
        alignment: str = "justify",
        paragraph_count: int = 5,
    ) -> Path:
        path = self.temp_path / f"para_{first_line_indent_inches}_{alignment}.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(paragraph_count):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = Inches(first_line_indent_inches)
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(f"Body paragraph {i + 1} with proper formatting.")
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
        check = ParagraphsCheck()
        return check.run(ctx)

    def test_exact_half_inch_indent_passes(self) -> None:
        """Exactly 0.5 inch first-line indent should pass."""
        docx_path = self._create_docx(first_line_indent_inches=0.5)
        issues = self._run_check(docx_path)
        indent_errors = [i for i in issues if "indent" in i.check and i.severity == "error"]
        self.assertEqual(indent_errors, [], f"Expected no indent errors but got: {indent_errors}")

    def test_indent_within_tolerance_passes(self) -> None:
        """0.55 inch indent (within 0.1 tolerance) should pass."""
        docx_path = self._create_docx(first_line_indent_inches=0.55)
        issues = self._run_check(docx_path)
        indent_errors = [i for i in issues if "indent" in i.check and i.severity == "error"]
        self.assertEqual(indent_errors, [], f"Expected no indent errors but got: {indent_errors}")


class TestParagraphsCheckIndentViolation(unittest.TestCase):
    """Tests for first-line indent violations."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx_no_indent(self, paragraph_count: int = 5) -> Path:
        path = self.temp_path / "no_indent.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(paragraph_count):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = None
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(f"Paragraph {i + 1} without indent.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        doc.save(str(path))
        return path

    def _create_mixed_indent_docx(self, with_indent: int, without_indent: int) -> Path:
        """Create document with mixed indent paragraphs."""
        path = self.temp_path / "mixed_indent.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(with_indent):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = Inches(0.5)
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(f"Indented paragraph {i + 1}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        for i in range(without_indent):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = None
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(f"Non-indented paragraph {i + 1}.")
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
        check = ParagraphsCheck()
        return check.run(ctx)

    def test_no_indent_all_paragraphs_raises_error(self) -> None:
        """All paragraphs without indent should raise error."""
        docx_path = self._create_docx_no_indent(paragraph_count=5)
        issues = self._run_check(docx_path)
        indent_errors = [i for i in issues if "indent" in i.check and i.severity == "error"]
        self.assertGreater(len(indent_errors), 0, f"Expected indent error but got: {issues}")

    def test_mixed_indent_majority_no_indent_raises_error(self) -> None:
        """4 without indent out of 5 should raise error (<50% indented, >3 lack indent)."""
        docx_path = self._create_mixed_indent_docx(with_indent=1, without_indent=4)
        issues = self._run_check(docx_path)
        indent_errors = [i for i in issues if "indent" in i.check and i.severity == "error"]
        self.assertGreater(
            len(indent_errors), 0, f"Expected error when majority lack indent but got: {issues}"
        )

    def test_mixed_indent_some_no_indent_raises_warning(self) -> None:
        """1 without indent out of 5 should raise warning (not >50%)."""
        docx_path = self._create_mixed_indent_docx(with_indent=4, without_indent=1)
        issues = self._run_check(docx_path)
        indent_errors = [i for i in issues if "indent" in i.check and i.severity == "error"]
        indent_warnings = [i for i in issues if "indent" in i.check and i.severity == "warning"]
        self.assertEqual(
            indent_errors, [], f"Expected no error when <50% wrong but got: {indent_errors}"
        )
        self.assertGreater(
            len(indent_warnings), 0, f"Expected warning when some lack indent but got: {issues}"
        )


class TestParagraphsCheckJustification(unittest.TestCase):
    """Tests for text justification."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx_justified(self, paragraph_count: int = 5) -> Path:
        path = self.temp_path / "justified.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(paragraph_count):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = Inches(0.5)
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(f"Justified paragraph {i + 1}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        doc.save(str(path))
        return path

    def _create_docx_left_aligned(self, paragraph_count: int = 5) -> Path:
        path = self.temp_path / "left_aligned.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(paragraph_count):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = Inches(0.5)
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = para.add_run(f"Left-aligned paragraph {i + 1}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        doc.save(str(path))
        return path

    def _create_mixed_alignment_docx(self, justified_count: int, left_count: int) -> Path:
        path = self.temp_path / "mixed_alignment.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        for i in range(justified_count):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = Inches(0.5)
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = para.add_run(f"Justified paragraph {i + 1}.")
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        for i in range(left_count):
            para = doc.add_paragraph()
            para.paragraph_format.first_line_indent = Inches(0.5)
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = para.add_run(f"Left-aligned paragraph {i + 1}.")
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
        check = ParagraphsCheck()
        return check.run(ctx)

    def test_all_justified_no_warning(self) -> None:
        """All paragraphs justified should not raise justification warning."""
        docx_path = self._create_docx_justified()
        issues = self._run_check(docx_path)
        just_warnings = [
            i for i in issues if "justification" in i.check and i.severity == "warning"
        ]
        self.assertEqual(
            just_warnings, [], f"Expected no justification warning but got: {just_warnings}"
        )

    def test_all_left_aligned_raises_warning(self) -> None:
        """All paragraphs left-aligned should raise justification warning."""
        docx_path = self._create_docx_left_aligned()
        issues = self._run_check(docx_path)
        just_warnings = [
            i for i in issues if "justification" in i.check and i.severity == "warning"
        ]
        self.assertGreater(
            len(just_warnings), 0, f"Expected justification warning but got: {issues}"
        )

    def test_mixed_majority_justified_no_warning(self) -> None:
        """3 justified out of 5 (>=50%) should not raise warning."""
        docx_path = self._create_mixed_alignment_docx(justified_count=3, left_count=2)
        issues = self._run_check(docx_path)
        just_warnings = [
            i for i in issues if "justification" in i.check and i.severity == "warning"
        ]
        self.assertEqual(
            just_warnings, [], f"Expected no warning when >=50% justified but got: {just_warnings}"
        )


if __name__ == "__main__":
    unittest.main()

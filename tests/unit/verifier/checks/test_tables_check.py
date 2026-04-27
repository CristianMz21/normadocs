"""Unit tests for TablesCheck - APA 7th Edition table verification."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from docx.shared import Inches

from normadocs.models import DocumentMetadata
from normadocs.verifier.apa_verifier import APAVerifier, VerificationContext
from normadocs.verifier.checks.tables import TablesCheck


class TestTablesCheckCompliant(unittest.TestCase):
    """Tests for APA-compliant tables (should pass)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx_with_apa_table(self) -> Path:
        path = self.temp_path / "apa_table.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        caption_para = doc.add_paragraph()
        run1 = caption_para.add_run("Table 1")
        run1.bold = True
        run2 = caption_para.add_run(". Title of the Table in Italic")
        run2.italic = True

        table = doc.add_table(rows=3, cols=3)
        table.style = "Table Grid"

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
        check = TablesCheck()
        return check.run(ctx)

    def test_apa_table_proper_caption_passes(self) -> None:
        """Table with proper APA caption (bold + italic) should pass."""
        docx_path = self._create_docx_with_apa_table()
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        self.assertEqual(errors, [], f"Expected no errors for APA table but got: {errors}")


class TestTablesCheckCaptionViolation(unittest.TestCase):
    """Tests for table caption violations."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx_table_caption_not_bold(self) -> Path:
        path = self.temp_path / "table_not_bold.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        caption_para = doc.add_paragraph()
        run = caption_para.add_run("Table 1. Title Not Bold")
        run.bold = False
        run.italic = True

        table = doc.add_table(rows=3, cols=3)
        table.style = "Table Grid"

        doc.save(str(path))
        return path

    def _create_docx_table_caption_not_italic(self) -> Path:
        path = self.temp_path / "table_not_italic.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        caption_para = doc.add_paragraph()
        run = caption_para.add_run("Table 1. Title Not Italic")
        run.bold = True
        run.italic = False

        table = doc.add_table(rows=3, cols=3)
        table.style = "Table Grid"

        doc.save(str(path))
        return path

    def _create_docx_table_no_caption(self) -> Path:
        path = self.temp_path / "table_no_caption.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        doc.add_paragraph("Just some text, no table caption.")

        table = doc.add_table(rows=3, cols=3)
        table.style = "Table Grid"

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
        check = TablesCheck()
        return check.run(ctx)

    def test_table_caption_not_bold_raises_error(self) -> None:
        """Table caption not bold should raise error."""
        docx_path = self._create_docx_table_caption_not_bold()
        issues = self._run_check(docx_path)
        bold_errors = [i for i in issues if "caption_bold" in i.check and i.severity == "error"]
        self.assertGreater(len(bold_errors), 0, f"Expected bold error but got: {issues}")

    def test_table_caption_not_italic_raises_warning(self) -> None:
        """Table caption title not italic should raise warning."""
        docx_path = self._create_docx_table_caption_not_italic()
        issues = self._run_check(docx_path)
        italic_warnings = [
            i for i in issues if "caption_italic" in i.check and i.severity == "warning"
        ]
        self.assertGreater(len(italic_warnings), 0, f"Expected italic warning but got: {issues}")

    def test_table_no_caption_raises_warning(self) -> None:
        """Table without caption should raise warning."""
        docx_path = self._create_docx_table_no_caption()
        issues = self._run_check(docx_path)
        caption_warnings = [
            i for i in issues if "caption_present" in i.check and i.severity == "warning"
        ]
        self.assertGreater(len(caption_warnings), 0, f"Expected caption warning but got: {issues}")


class TestTablesCheckMultipleTables(unittest.TestCase):
    """Tests for documents with multiple tables."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _create_docx_multiple_tables(self) -> Path:
        path = self.temp_path / "multiple_tables.docx"
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

        caption1 = doc.add_paragraph()
        run1 = caption1.add_run("Table 1")
        run1.bold = True
        run2 = caption1.add_run(". First Table")
        run2.italic = True
        doc.add_table(rows=2, cols=2)

        caption2 = doc.add_paragraph()
        run3 = caption2.add_run("Table 2")
        run3.bold = True
        run4 = caption2.add_run(". Second Table")
        run4.italic = True
        doc.add_table(rows=2, cols=2)

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
        check = TablesCheck()
        return check.run(ctx)

    def test_multiple_tables_all_proper_passes(self) -> None:
        """Document with multiple properly captioned tables should pass."""
        docx_path = self._create_docx_multiple_tables()
        issues = self._run_check(docx_path)
        errors = [i for i in issues if i.severity == "error"]
        self.assertEqual(errors, [], f"Expected no errors but got: {errors}")


if __name__ == "__main__":
    unittest.main()

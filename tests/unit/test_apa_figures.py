"""
Unit tests for APA formatter figure methods.

Tests cover:
- _make_figure_paragraph helper
- format_figures (image scaling)
- add_figure_captions (caption creation)
- Config getters
"""

import unittest
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

from normadocs.formatters.apa.apa_figures import APAFiguresHandler


class TestGetFigureConfig(unittest.TestCase):
    """Tests for _get_figure_config method."""

    def test_default_config(self):
        """Default config should have expected keys."""
        doc = Document()
        handler = APAFiguresHandler(doc)
        config = handler._get_figure_config()
        self.assertEqual(config["caption_prefix"], "Figura")
        self.assertTrue(config["title_above"])
        self.assertEqual(config["nota_prefix"], "Nota.")

    def test_custom_config(self):
        """Custom config should override defaults."""
        doc = Document()
        handler = APAFiguresHandler(doc, config={"figures": {"caption_prefix": "Image"}})
        config = handler._get_figure_config()
        self.assertEqual(config["caption_prefix"], "Image")


class TestGetBodyFont(unittest.TestCase):
    """Tests for _get_body_font method."""

    def test_default_font(self):
        """Default body font should be Times New Roman."""
        doc = Document()
        handler = APAFiguresHandler(doc)
        font = handler._get_body_font()
        self.assertEqual(font, "Times New Roman")

    def test_custom_font(self):
        """Custom config should override font."""
        doc = Document()
        handler = APAFiguresHandler(doc, config={"fonts": {"body": {"name": "Arial"}}})
        font = handler._get_body_font()
        self.assertEqual(font, "Arial")


class TestMakeFigureParagraph(unittest.TestCase):
    """Tests for _make_figure_paragraph helper."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path("tests/temp_figures")
        cls.temp_dir.mkdir(parents=True, exist_ok=True)
        cls.docx_path = cls.temp_dir / "test.docx"
        doc = Document()
        doc.save(str(cls.docx_path))
        cls.handler = APAFiguresHandler(doc)

    @classmethod
    def tearDownClass(cls):
        import shutil

        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)

    def test_figure_paragraph_returns_element(self):
        """_make_figure_paragraph returns an OxmlElement."""
        result = self.handler._make_figure_paragraph("Test caption")
        self.assertIsNotNone(result)
        self.assertEqual(result.tag, qn("w:p"))

    def test_figure_paragraph_with_bold(self):
        """Bold text creates run with w:b element."""
        p_el = self.handler._make_figure_paragraph("Bold text", bold=True)
        r_el = p_el.find(f".//{qn('w:r')}")
        self.assertIsNotNone(r_el)
        rPr = r_el.find(qn("w:rPr"))
        self.assertIsNotNone(rPr)
        b_el = rPr.find(qn("w:b"))
        self.assertIsNotNone(b_el)

    def test_figure_paragraph_with_italic(self):
        """Italic text creates run with w:i element."""
        p_el = self.handler._make_figure_paragraph("Italic text", italic=True)
        r_el = p_el.find(f".//{qn('w:r')}")
        rPr = r_el.find(qn("w:rPr"))
        i_el = rPr.find(qn("w:i"))
        self.assertIsNotNone(i_el)

    def test_figure_paragraph_text_content(self):
        """Paragraph contains the expected text."""
        p_el = self.handler._make_figure_paragraph("Caption text")
        t_el = p_el.find(f".//{qn('w:t')}")
        self.assertEqual(t_el.text, "Caption text")

    def test_figure_paragraph_space_after(self):
        """Paragraph spacing is set correctly."""
        p_el = self.handler._make_figure_paragraph("Test", space_after="120")
        p_pr = p_el.find(qn("w:pPr"))
        sp_el = p_pr.find(qn("w:spacing"))
        self.assertEqual(sp_el.get(qn("w:after")), "120")

    def test_figure_paragraph_no_style(self):
        """Paragraph with no bold/italic has no w:b or w:i."""
        p_el = self.handler._make_figure_paragraph("Plain text")
        r_el = p_el.find(f".//{qn('w:r')}")
        rPr = r_el.find(qn("w:rPr"))
        self.assertIsNone(rPr.find(qn("w:b")))
        self.assertIsNone(rPr.find(qn("w:i")))

    def test_figure_paragraph_bold_and_italic(self):
        """Both bold and italic creates both w:b and w:i."""
        p_el = self.handler._make_figure_paragraph("Both styles", bold=True, italic=True)
        r_el = p_el.find(f".//{qn('w:r')}")
        rPr = r_el.find(qn("w:rPr"))
        self.assertIsNotNone(rPr.find(qn("w:b")))
        self.assertIsNotNone(rPr.find(qn("w:i")))


class TestFormatFigures(unittest.TestCase):
    """Tests for format_figures method (image scaling)."""

    def test_format_figures_no_images(self):
        """format_figures should handle document with no images."""
        doc = Document()
        doc.add_paragraph("Just text")
        handler = APAFiguresHandler(doc)
        handler.format_figures()
        self.assertEqual(len(doc.paragraphs), 1)


class TestAddFigureCaptions(unittest.TestCase):
    """Tests for add_figure_captions method."""

    def test_add_figure_captions_empty_document(self):
        """add_figure_captions should handle empty document."""
        doc = Document()
        handler = APAFiguresHandler(doc)
        handler.add_figure_captions()
        self.assertEqual(len(doc.paragraphs), 0)

    def test_add_figure_captions_no_images(self):
        """add_figure_captions should handle document with no images."""
        doc = Document()
        doc.add_paragraph("Just text")
        handler = APAFiguresHandler(doc)
        handler.add_figure_captions()
        self.assertEqual(len(doc.paragraphs), 1)

    def test_caption_preserves_existing_paragraphs(self):
        """add_figure_captions should preserve existing non-image paragraphs."""
        doc = Document()
        doc.add_paragraph("Introduction")
        doc.add_paragraph("Some text")

        handler = APAFiguresHandler(doc)
        initial_count = len(doc.paragraphs)
        handler.add_figure_captions()

        self.assertGreaterEqual(len(doc.paragraphs), initial_count)


class TestApplyFontStyle(unittest.TestCase):
    """Tests for _apply_font_style method."""

    def test_apply_font_style_bold(self):
        """_apply_font_style should apply bold formatting."""
        doc = Document()
        handler = APAFiguresHandler(doc)
        p = doc.add_paragraph()
        run = p.add_run("Test")
        handler._apply_font_style(run, bold=True)
        self.assertTrue(run.bold)

    def test_apply_font_style_italic(self):
        """_apply_font_style should apply italic formatting."""
        doc = Document()
        handler = APAFiguresHandler(doc)
        p = doc.add_paragraph()
        run = p.add_run("Test")
        handler._apply_font_style(run, italic=True)
        self.assertTrue(run.italic)


if __name__ == "__main__":
    unittest.main()

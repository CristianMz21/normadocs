"""
Tests for PDF Generator.
"""

import unittest
import sys
from unittest.mock import patch, MagicMock
from normadocs.pdf_generator import PDFGenerator


class TestPDFGenerator(unittest.TestCase):
    @patch("subprocess.run")
    def test_libreoffice_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        success = PDFGenerator.convert_with_libreoffice("input.docx", "output_dir")
        self.assertTrue(success)

        args, _ = mock_run.call_args
        cmd = args[0]
        self.assertEqual(cmd[0], "libreoffice")
        self.assertIn("--convert-to", cmd)

    @patch("subprocess.run")
    def test_libreoffice_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        success = PDFGenerator.convert_with_libreoffice("input.docx", "output_dir")
        self.assertFalse(success)

    @patch("subprocess.run")
    def test_weasyprint_success(self, mock_run):
        # Mock pandoc conversion to HTML first
        mock_pandoc_res = MagicMock()
        mock_pandoc_res.returncode = 0
        mock_pandoc_res.stdout = "<html></html>"
        mock_run.return_value = mock_pandoc_res

        # Mock WeasyPrint module
        mock_weasyprint = MagicMock()
        mock_html_cls = MagicMock()
        mock_css_cls = MagicMock()
        mock_weasyprint.HTML = mock_html_cls
        mock_weasyprint.CSS = mock_css_cls

        # Setup the write_pdf mock
        mock_html_instance = MagicMock()
        mock_html_cls.return_value = mock_html_instance

        with patch.dict("sys.modules", {"weasyprint": mock_weasyprint}):
            success = PDFGenerator.convert_with_weasyprint("markdown content", "output.pdf")

            self.assertTrue(success)
            mock_html_instance.write_pdf.assert_called_once()
            mock_run.assert_called()


if __name__ == "__main__":
    unittest.main()

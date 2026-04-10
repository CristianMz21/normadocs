"""
Module for generating PDFs from DOCX or Markdown.
"""

import sys

from .utils.subprocess import CommandFailedError, get_command_path, run_command


class PDFGenerator:
    """Handles conversion to PDF."""

    @staticmethod
    def convert(docx_path: str, output_dir: str, md_content: str, output_path: str) -> bool:
        """Convert DOCX to PDF with automatic backend selection.

        Attempts conversion with LibreOffice first, falls back to WeasyPrint
        if LibreOffice is unavailable.

        Args:
            docx_path: Path to the source DOCX file.
            output_dir: Directory for the output PDF.
            md_content: Markdown content for styling reference.
            output_path: Path for the output PDF file.

        Returns:
            True if conversion succeeded, False otherwise.
        """
        if PDFGenerator.convert_with_libreoffice(docx_path, output_dir):
            return True
        return PDFGenerator.convert_with_weasyprint(md_content, output_path)

    @staticmethod
    def convert_with_libreoffice(docx_path: str, output_dir: str) -> bool:
        """Convert DOCX to PDF using LibreOffice.

        Args:
            docx_path: Path to the source DOCX file.
            output_dir: Directory for the output PDF.

        Returns:
            True if conversion succeeded, False otherwise.

        Raises:
            CommandFailedError: If LibreOffice fails.
            FileNotFoundError: If LibreOffice is not found.
        """
        try:
            libreoffice_path = get_command_path("libreoffice")
        except FileNotFoundError:
            print("  ✗ LibreOffice no encontrado.", file=sys.stderr)
            return False

        cmd = [
            libreoffice_path,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(docx_path),
        ]
        print("  ▸ Generando PDF con LibreOffice...")
        try:
            run_command(cmd)
            return True

        except CommandFailedError as e:
            print(f"  ✗ Error de LibreOffice:\n{e.stderr}", file=sys.stderr)
            return False

        except FileNotFoundError:
            print("  ✗ LibreOffice no encontrado.", file=sys.stderr)
            return False

    @staticmethod
    def convert_with_weasyprint(md_content: str, output_path: str) -> bool:
        """Convert Markdown to PDF using WeasyPrint.

        Converts Markdown to HTML first using Pandoc, then renders to PDF
        using WeasyPrint.

        Args:
            md_content: Markdown content to convert.
            output_path: Path for the output PDF file.

        Returns:
            True if conversion succeeded, False otherwise.

        Raises:
            WeasyPrintError: If WeasyPrint conversion fails.
        """
        try:
            from weasyprint import CSS, HTML
        except ImportError:
            print("  ✗ WeasyPrint no instalado.")
            return False

        pandoc_path = get_command_path("pandoc")
        cmd = [pandoc_path, "-f", "markdown", "-t", "html5", "--standalone"]
        try:
            result = run_command(
                cmd,
                input_data=md_content,
                encoding="utf-8",
            )
            html_content = result.stdout

            css = CSS(
                string="""
                @page { size: Letter; margin: 1in; }
                body { font-family: "Times New Roman"; font-size: 12pt; line-height: 2.0; }
            """
            )

            HTML(string=html_content).write_pdf(target=output_path, stylesheets=[css])
            return True

        except CommandFailedError:
            return False

        except FileNotFoundError:
            print("  ✗ Pandoc no encontrado para WeasyPrint.", file=sys.stderr)
            return False

        except Exception as e:
            print(f"  ✗ Error en WeasyPrint: {e}")
            return False

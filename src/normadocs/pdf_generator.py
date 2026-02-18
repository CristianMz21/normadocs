"""
Module for generating PDFs from DOCX or Markdown.
"""

import subprocess
import sys
from pathlib import Path


class PDFGenerator:
    """Handles conversion to PDF."""

    @staticmethod
    def convert_with_libreoffice(docx_path: str, output_dir: str) -> bool:
        """Convert DOCX to PDF using LibreOffice."""
        try:
            cmd = [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(docx_path),
            ]
            print(f"  ▸ Generando PDF con LibreOffice...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"  ✗ Error de LibreOffice:\n{result.stderr}", file=sys.stderr)
                return False
            return True

        except FileNotFoundError:
            print("  ✗ LibreOffice no encontrado.", file=sys.stderr)
            return False

    @staticmethod
    def convert_with_weasyprint(md_content: str, output_path: str) -> bool:
        """Fallback: Convert Markdown -> HTML -> PDF using WeasyPrint."""
        try:
            from weasyprint import CSS, HTML
        except ImportError:
            print("  ✗ WeasyPrint no instalado.")
            return False

        # Pandoc MD -> HTML
        cmd = ["pandoc", "-f", "markdown", "-t", "html5", "--standalone"]
        try:
            result = subprocess.run(
                cmd, input=md_content, capture_output=True, text=True, encoding="utf-8"
            )
            if result.returncode != 0:
                return False

            html_content = result.stdout

            # Simple APA CSS
            css = CSS(
                string="""
                @page { size: Letter; margin: 1in; }
                body { font-family: "Times New Roman"; font-size: 12pt; line-height: 2.0; }
            """
            )

            HTML(string=html_content).write_pdf(target=output_path, stylesheets=[css])
            return True

        except Exception as e:
            print(f"  ✗ Error en WeasyPrint: {e}")
            return False

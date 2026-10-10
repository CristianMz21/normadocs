"""
Module for generating PDFs from DOCX or Markdown.
"""

import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from .utils.subprocess import CommandFailedError, get_command_path, run_command


class PDFGenerator:
    """Handles conversion to PDF."""

    @staticmethod
    def convert(
        docx_path: str,
        output_dir: str,
        md_content: str,
        output_path: str,
        source_dir: str | None = None,
    ) -> bool:
        """Convert DOCX to PDF with automatic backend selection.

        Attempts conversion with LibreOffice first, falls back to WeasyPrint
        if LibreOffice is unavailable.

        Args:
            docx_path: Path to the source DOCX file.
            output_dir: Directory for the output PDF.
            md_content: Markdown content for styling reference.
            output_path: Path for the output PDF file.
            source_dir: Directory the Markdown was read from. Local files
                referenced by the document are only loaded from here (and
                the output directory) by the WeasyPrint fallback.

        Returns:
            True if conversion succeeded, False otherwise.
        """
        if PDFGenerator.convert_with_libreoffice(docx_path, output_dir):
            return True
        return PDFGenerator.convert_with_weasyprint(md_content, output_path, source_dir)

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
    def convert_with_weasyprint(
        md_content: str, output_path: str, source_dir: str | None = None
    ) -> bool:
        """Convert Markdown to PDF using WeasyPrint.

        Converts Markdown to HTML first using Pandoc, then renders to PDF
        using WeasyPrint.

        Security: the HTML is produced with raw HTML and raw attributes
        disabled, and WeasyPrint runs with a restricted URL fetcher that
        only allows ``data:`` URIs plus local files under ``source_dir``
        and the output directory. Anything else (``http(s)://``, absolute
        ``file://`` paths outside the allowlist) is blocked, so an
        untrusted document cannot exfiltrate local files or probe the
        network through ``<link>``/``<img>`` tags.

        Args:
            md_content: Markdown content to convert.
            output_path: Path for the output PDF file.
            source_dir: Directory the Markdown was read from. Local files
                referenced by the document are only loaded from here (and
                the output directory).

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

        class _RestrictedURLFetcher:
            """URL fetcher that blocks network and out-of-scope local files.

            Implements WeasyPrint's fetcher protocol (``fetcher(url)``):
            ``data:`` URIs and ``file://`` URLs under the allowed
            directories are delegated to the default fetcher; anything
            else raises ``ValueError``, which WeasyPrint turns into a
            skipped resource instead of aborting the render.
            """

            def __init__(self, allowed_dirs: list[Path]) -> None:
                from weasyprint.urls import URLFetcher

                self._allowed_dirs = [d.resolve() for d in allowed_dirs]
                self._delegate = URLFetcher()

            def _check(self, url: str) -> None:
                scheme = urlparse(url).scheme.lower()
                if scheme == "data":
                    return
                if scheme == "file":
                    raw_path = unquote(urlparse(url).path)
                    try:
                        resolved = Path(raw_path).resolve()
                    except OSError as e:
                        raise ValueError(f"Recurso local bloqueado: {url}") from e
                    if any(
                        resolved == allowed or allowed in resolved.parents
                        for allowed in self._allowed_dirs
                    ):
                        return
                    raise ValueError(f"Recurso local bloqueado: {url}")
                raise ValueError(f"Recurso externo bloqueado: {url}")

            def __call__(self, url: str) -> object:
                self._check(url)
                return self._delegate(url)

            def fetch(self, url: str, headers: dict[str, str] | None = None) -> object:
                self._check(url)
                return self._delegate.fetch(url, headers)

        pandoc_path = get_command_path("pandoc")
        cmd = [
            pandoc_path,
            "-f",
            "markdown-raw_html-raw_attribute",
            "-t",
            "html5",
            "--standalone",
        ]
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

            output_parent = Path(output_path).resolve().parent
            allowed_dirs = [output_parent]
            if source_dir:
                allowed_dirs.append(Path(source_dir))
            # Trailing slash: without it urljoin() would drop the last
            # path segment when resolving relative URLs.
            base_url = allowed_dirs[-1].as_uri() + "/"

            HTML(string=html_content, base_url=base_url).write_pdf(
                target=output_path,
                stylesheets=[css],
                url_fetcher=_RestrictedURLFetcher(allowed_dirs),
            )
            return True

        except CommandFailedError:
            return False

        except FileNotFoundError:
            print("  ✗ Pandoc no encontrado para WeasyPrint.", file=sys.stderr)
            return False

        except Exception as e:
            print(f"  ✗ Error en WeasyPrint: {e}")
            return False

"""
Security regression tests for the 2026-09-28 audit findings (F-01..F-09).

Each test pins the fixed behavior so the vulnerabilities cannot regress
silently. They run with ``-W error`` in CI: no warning may leak from the
security paths either.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from normadocs.cli_helpers import LANGUAGETOOL_IMAGE, _ensure_languagetool_server
from normadocs.codeimage_processor import CodeImageProcessor
from normadocs.models import DocumentMetadata
from normadocs.pdf_generator import PDFGenerator
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.utils import subprocess as subprocess_utils
from normadocs.verifier import CheckCategory, VerificationIssue, VerificationResult
from normadocs.verifier.apa_verifier import APAVerifier


def _capture_weasyprint_fetcher(md_content: str, source_dir: str | None = None):
    """Run convert_with_weasyprint with mocked HTML/CSS, return the fetcher."""
    with patch("weasyprint.HTML") as mock_html_cls, patch("weasyprint.CSS"):
        mock_html_instance = MagicMock()
        mock_html_cls.return_value = mock_html_instance
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "out.pdf")
            result = PDFGenerator.convert_with_weasyprint(md_content, output_path, source_dir)
            assert result is True
            _, write_kwargs = mock_html_instance.write_pdf.call_args
            return write_kwargs["url_fetcher"]


class TestWeasyPrintFetcherPolicy(unittest.TestCase):
    """F-01: the WeasyPrint fallback must not leak files nor reach the network."""

    def test_blocks_local_file_outside_allowlist(self):
        fetcher = _capture_weasyprint_fetcher("# Title\n")
        with self.assertRaises(ValueError):
            fetcher.fetch("file:///etc/hostname")

    def test_blocks_http_ssrf(self):
        fetcher = _capture_weasyprint_fetcher("# Title\n")
        with self.assertRaises(ValueError):
            fetcher.fetch("http://169.254.169.254/latest/meta-data/")
        with self.assertRaises(ValueError):
            fetcher.fetch("https://intranet.local/admin")

    def test_allows_data_uris(self):
        fetcher = _capture_weasyprint_fetcher("# Title\n")
        response = fetcher.fetch("data:text/plain,hello")
        try:
            self.assertIsNotNone(response)
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()

    def test_allows_files_under_source_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            asset = Path(tmpdir) / "fig.png"
            asset.write_bytes(b"\x89PNG\r\n\x1a\n")
            fetcher = _capture_weasyprint_fetcher("# Title\n", source_dir=tmpdir)
            response = fetcher.fetch(asset.as_uri())
            try:
                self.assertIsNotNone(response)
            finally:
                close = getattr(response, "close", None)
                if callable(close):
                    close()

    def test_call_protocol_matches_weasyprint(self):
        """WeasyPrint invokes fetcher(url); the __call__ path must enforce policy."""
        fetcher = _capture_weasyprint_fetcher("# Title\n")
        with self.assertRaises(ValueError):
            fetcher("http://169.254.169.254/latest/meta-data/")
        with self.assertRaises(ValueError):
            fetcher("file:///etc/hostname")

    def test_end_to_end_malicious_markdown_embeds_nothing(self):
        """A hostile .md must produce a PDF with no file attachments,
        while a legitimate scoped image still renders."""
        import fitz
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            secret = Path(tmpdir) / "secret.txt"
            secret.write_text("TOP-SECRET", encoding="utf-8")
            doc_dir = Path(tmpdir) / "doc"
            doc_dir.mkdir()
            Image.new("RGB", (10, 10), (200, 30, 30)).save(doc_dir / "fig.png")
            md = (
                "# Title\n\n"
                "![ok](fig.png)\n\n"
                '<link rel="attachment" href="file:///etc/hostname">\n\n'
                f'<link rel="attachment" href="{secret.as_uri()}">\n'
            )
            output_path = str(Path(tmpdir) / "out.pdf")
            result = PDFGenerator.convert_with_weasyprint(md, output_path, str(doc_dir))
            self.assertTrue(result)
            with fitz.open(output_path) as pdf:
                self.assertEqual(pdf.embfile_names(), [])
                images = [img for page in pdf for img in page.get_images()]
                self.assertGreaterEqual(len(images), 1)

    def test_title_page_metadata_is_escaped(self):
        """F-01 frontmatter vector: metadata must not inject markup."""
        meta = DocumentMetadata(
            title='<link rel="attachment" href="file:///etc/passwd">',
            author='<img src="http://evil/x">',
        )
        md = MarkdownPreprocessor.build_title_page_md(meta)
        self.assertNotIn('<link rel="attachment"', md)
        self.assertNotIn("<img src=", md)
        self.assertIn("&lt;link", md)


class TestRawAttributeSanitization(unittest.TestCase):
    """F-03: user {=...} markers must not reach Pandoc as raw attributes."""

    def test_fenced_openxml_block_is_neutralized(self):
        md = (
            "# Title\n\n"
            "```{=openxml}\n"
            '<w:p><w:fldSimple w:instr=" INCLUDEPICTURE "http://evil/x.png" ">\n'
            "</w:fldSimple></w:p>\n"
            "```\n"
        )
        clean_md, _ = MarkdownPreprocessor().process(md)
        self.assertNotIn("```{=openxml}", clean_md)
        self.assertIn("```\\{=openxml}", clean_md)

    def test_inline_raw_attribute_is_neutralized(self):
        md = "# Title\n\n`evil`{=openxml}\n"
        clean_md, _ = MarkdownPreprocessor().process(md)
        self.assertNotIn("`{=openxml}", clean_md)

    def test_code_block_content_is_preserved_verbatim(self):
        md = "# Title\n\n```python\nprint('{=not-an-attribute}')\n```\n"
        clean_md, _ = MarkdownPreprocessor().process(md)
        self.assertIn("print('{=not-an-attribute}')", clean_md)

    def test_tool_page_break_survives_sanitization(self):
        md = "# Title\n\n# Referencias\n\n- entry\n"
        clean_md, _ = MarkdownPreprocessor().process(md)
        self.assertIn("```{=openxml}", clean_md)


class TestSubprocessResolver(unittest.TestCase):
    """F-04: only the executable (cmd[0]) may be resolved via PATH."""

    def test_arguments_are_never_rewritten(self):
        with patch.object(subprocess_utils, "get_command_path", side_effect=lambda c: f"/bin/{c}"):
            resolved = subprocess_utils._resolve_command_paths(
                ["mycmd", "sh", "--convert-to", "pdf"]
            )
        self.assertEqual(resolved, ["/bin/mycmd", "sh", "--convert-to", "pdf"])

    def test_absolute_executable_is_untouched(self):
        resolved = subprocess_utils._resolve_command_paths(["/usr/bin/pandoc", "-f", "markdown"])
        self.assertEqual(resolved, ["/usr/bin/pandoc", "-f", "markdown"])

    def test_empty_command(self):
        self.assertEqual(subprocess_utils._resolve_command_paths([]), [])


class TestDockerImagePin(unittest.TestCase):
    """F-05: the LanguageTool image must be digest-pinned and ephemeral."""

    def test_image_is_digest_pinned(self):
        self.assertIn("@sha256:", LANGUAGETOOL_IMAGE)
        self.assertNotIn(":latest", LANGUAGETOOL_IMAGE)

    @patch("time.sleep")
    @patch("normadocs.cli_helpers.run_command")
    @patch("normadocs.cli_helpers.get_command_path", return_value="docker")
    def test_docker_run_uses_rm_and_pinned_image(self, _mock_path, mock_run, _mock_sleep):
        from unittest.mock import MagicMock as Mock

        mock_client = Mock()
        mock_client.is_server_running.side_effect = [False, True]
        mock_run.return_value = MagicMock(returncode=0)

        _ensure_languagetool_server(mock_client, lt_docker=True, lt_port=8081)

        cmd = mock_run.call_args[0][0]
        self.assertIn("--rm", cmd)
        self.assertIn(LANGUAGETOOL_IMAGE, cmd)


class TestHtmlReportEscaping(unittest.TestCase):
    """F-08: verifier HTML must escape document-controlled text."""

    def _report(self) -> str:
        issue = VerificationIssue(
            check="headings.evil<script>alert(1)</script>",
            severity="error",
            expected="<b>expected</b>",
            actual='<img src="x" onerror="alert(1)">',
            evidence="Evidence '<script>alert(1)</script>' here",
        )
        result = VerificationResult(
            passed=False,
            score=50.0,
            issues=[issue],
            errors=[issue],
            warnings=[],
            infos=[],
            pdf_path=Path("report.pdf"),
        )
        verifier = APAVerifier(pdf_path="report.pdf", docx_path="report.docx")
        try:
            return verifier.generate_report(result, format="html")
        finally:
            verifier.close()

    def test_no_raw_script_in_html_report(self):
        report = self._report()
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)
        self.assertIn("&lt;img", report)


class TestCodeImageOptions(unittest.TestCase):
    """F-09: the image renderer must not enable local file access."""

    def test_no_enable_local_file_access(self):
        processor = CodeImageProcessor(output_dir="code_images")
        captured = {}

        fake_imgkit = MagicMock()

        def fake_from_string(html_content, path, options=None):
            captured["options"] = options
            Path(path).write_bytes(b"fake")
            return True

        fake_imgkit.from_string.side_effect = fake_from_string
        with (
            patch.dict("sys.modules", {"imgkit": fake_imgkit}),
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            processor._generate_image("<html></html>", Path(tmpdir) / "out.png")

        self.assertNotIn("enable-local-file-access", captured["options"])


class TestCheckCategoryImport(unittest.TestCase):
    """Guard: the security tests import the real CheckCategory."""

    def test_category_exists(self):
        self.assertTrue(hasattr(CheckCategory, "MARGINS"))


if __name__ == "__main__":
    unittest.main()

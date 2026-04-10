"""
Tests for CLI helper functions.
"""

import unittest
from unittest.mock import MagicMock, patch

from normadocs.cli_helpers import (
    LanguageToolResult,
    _ensure_languagetool_server,
    _setup_languagetool_client,
)
from normadocs.languagetool_client import LanguageToolClient
from normadocs.utils.subprocess import CommandFailedError


class TestSetupLanguageToolClient(unittest.TestCase):
    """Tests for _setup_languagetool_client function."""

    def test_returns_none_when_no_language(self):
        """Should return None when language_tool is None."""
        result = _setup_languagetool_client(
            language_tool=None,
            lt_host="localhost",
            lt_port=8081,
            lt_enabled_rules=None,
            lt_disabled_rules=None,
            lt_ignore_words=None,
            lt_no_spelling=False,
            default_ignore_words=[],
        )
        self.assertIsNone(result)

    def test_creates_client_with_defaults(self):
        """Should create client with default ignore words."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            _setup_languagetool_client(
                language_tool="es",
                lt_host="localhost",
                lt_port=8081,
                lt_enabled_rules=None,
                lt_disabled_rules=None,
                lt_ignore_words=None,
                lt_no_spelling=False,
                default_ignore_words=["word1", "word2"],
            )
            mock_init.assert_called_once()

    def test_creates_client_with_custom_enabled_rules(self):
        """Should create client with enabled rules split from comma string."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            _setup_languagetool_client(
                language_tool="es",
                lt_host="localhost",
                lt_port=8081,
                lt_enabled_rules="RULE1,RULE2",
                lt_disabled_rules=None,
                lt_ignore_words=None,
                lt_no_spelling=False,
                default_ignore_words=[],
            )
            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args[1]
            self.assertEqual(call_kwargs["enabled_rules"], ["RULE1", "RULE2"])

    def test_creates_client_with_custom_disabled_rules(self):
        """Should create client with disabled rules split from comma string."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            _setup_languagetool_client(
                language_tool="es",
                lt_host="localhost",
                lt_port=8081,
                lt_enabled_rules=None,
                lt_disabled_rules="RULE3,RULE4",
                lt_ignore_words=None,
                lt_no_spelling=False,
                default_ignore_words=[],
            )
            call_kwargs = mock_init.call_args[1]
            self.assertEqual(call_kwargs["disabled_rules"], ["RULE3", "RULE4"])

    def test_creates_client_with_empty_ignore_words(self):
        """Should create client with empty ignore words when lt_ignore_words is empty."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            _setup_languagetool_client(
                language_tool="es",
                lt_host="localhost",
                lt_port=8081,
                lt_enabled_rules=None,
                lt_disabled_rules=None,
                lt_ignore_words="",
                lt_no_spelling=False,
                default_ignore_words=["default"],
            )
            call_kwargs = mock_init.call_args[1]
            self.assertEqual(call_kwargs["ignore_words"], [])

    def test_creates_client_with_custom_ignore_words(self):
        """Should create client with custom ignore words split from comma string."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            _setup_languagetool_client(
                language_tool="es",
                lt_host="localhost",
                lt_port=8081,
                lt_enabled_rules=None,
                lt_disabled_rules=None,
                lt_ignore_words="custom1,custom2",
                lt_no_spelling=False,
                default_ignore_words=["default"],
            )
            call_kwargs = mock_init.call_args[1]
            self.assertEqual(call_kwargs["ignore_words"], ["custom1", "custom2"])

    def test_disables_spelling_when_flag_true(self):
        """Should disable spelling when lt_no_spelling is True."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            _setup_languagetool_client(
                language_tool="es",
                lt_host="localhost",
                lt_port=8081,
                lt_enabled_rules=None,
                lt_disabled_rules=None,
                lt_ignore_words=None,
                lt_no_spelling=True,
                default_ignore_words=[],
            )
            call_kwargs = mock_init.call_args[1]
            self.assertTrue(call_kwargs["disable_spelling"])


class TestEnsureLanguageToolServer(unittest.TestCase):
    """Tests for _ensure_languagetool_server function."""

    def test_returns_none_when_server_running(self):
        """Should return None immediately when server is already running."""
        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.is_server_running.return_value = True

        result = _ensure_languagetool_server(mock_client, lt_docker=False, lt_port=8081)
        self.assertIsNone(result)

    def test_raises_exit_when_no_docker_and_not_running(self):
        """Should raise typer.Exit when not running and lt_docker is False."""
        import typer

        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.is_server_running.return_value = False
        mock_client.base_url = "http://localhost:8081"

        with self.assertRaises(typer.Exit):
            _ensure_languagetool_server(mock_client, lt_docker=False, lt_port=8081)

    @patch("time.sleep")
    @patch("subprocess.run")
    def test_starts_docker_container_when_server_starts_running(self, mock_run, mock_sleep):
        """Should start Docker container and return name when server becomes running."""
        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.is_server_running.side_effect = [False, False, False, True]

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _ensure_languagetool_server(mock_client, lt_docker=True, lt_port=8081)

        self.assertEqual(result, "normadocs-lt")
        mock_run.assert_called_once()

    @patch("normadocs.utils.subprocess.run_command")
    def test_raises_exit_on_subprocess_error(self, mock_run):
        """Should raise typer.Exit when subprocess fails."""
        import typer

        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.is_server_running.return_value = False

        error = CommandFailedError(returncode=1, cmd=["docker"], stderr="Docker error")
        mock_run.side_effect = error

        with self.assertRaises(typer.Exit):
            _ensure_languagetool_server(mock_client, lt_docker=True, lt_port=8081)


class TestRunLanguageToolPrecheck(unittest.TestCase):
    """Tests for _run_languagetool_precheck function."""

    def test_precheck_returns_true_when_no_errors(self):
        """Should return True when no errors found."""
        from normadocs.cli_helpers import _run_languagetool_precheck

        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.check.return_value = []
        mock_client.language = "es"

        result = _run_languagetool_precheck(mock_client, "clean text", True, [])

        self.assertTrue(result)

    def test_precheck_returns_true_when_continue_on_error(self):
        """Should return True when errors found but lt_stop_on_error is False."""
        from normadocs.cli_helpers import _run_languagetool_precheck

        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.check.return_value = [
            MagicMock(message="Error", context="ctx", replacements=["fix"])
        ]
        mock_client.language = "es"

        result = _run_languagetool_precheck(mock_client, "text with erro", False, [])

        self.assertTrue(result)

    def test_precheck_returns_false_when_stop_on_error(self):
        """Should return False when errors found and lt_stop_on_error is True."""
        from normadocs.cli_helpers import _run_languagetool_precheck

        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.check.return_value = [
            MagicMock(message="Error", context="ctx", replacements=["fix"])
        ]
        mock_client.language = "es"

        result = _run_languagetool_precheck(mock_client, "text with erro", True, [])

        self.assertFalse(result)


class TestRunPandoc(unittest.TestCase):
    """Tests for _run_pandoc function."""

    def test_run_pandoc_returns_true_on_success(self):
        """Should return True when pandoc succeeds."""
        from pathlib import Path

        from normadocs.cli_helpers import _run_pandoc
        from normadocs.pandoc_client import PandocRunner

        with patch.object(PandocRunner, "run", return_value=True) as mock_run:
            result = _run_pandoc("markdown", Path("out.docx"), None, None, Path("in.md"))

            self.assertTrue(result)
            mock_run.assert_called_once()

    def test_run_pandoc_returns_false_on_failure(self):
        """Should return False when pandoc fails."""
        from pathlib import Path

        from normadocs.cli_helpers import _run_pandoc
        from normadocs.pandoc_client import PandocRunner

        with patch.object(PandocRunner, "run", return_value=False):
            result = _run_pandoc("markdown", Path("out.docx"), None, None, Path("in.md"))

            self.assertFalse(result)


class TestGeneratePDF(unittest.TestCase):
    """Tests for _generate_pdf function."""

    def test_generate_pdf_returns_true_when_format_not_pdf(self):
        """Should return True immediately when format is not pdf/all."""
        from pathlib import Path

        from normadocs.cli_helpers import _generate_pdf

        result = _generate_pdf("docx", Path("out.docx"), Path("dir"), "md", Path("out.pdf"))

        self.assertTrue(result)

    def test_generate_pdf_returns_true_on_success(self):
        """Should return True when PDFGenerator succeeds."""
        from pathlib import Path

        from normadocs.cli_helpers import _generate_pdf
        from normadocs.pdf_generator import PDFGenerator

        with patch.object(PDFGenerator, "convert", return_value=True):
            result = _generate_pdf("pdf", Path("out.docx"), Path("dir"), "md", Path("out.pdf"))

            self.assertTrue(result)

    def test_generate_pdf_returns_false_on_failure(self):
        """Should return False when PDFGenerator fails."""
        from pathlib import Path

        from normadocs.cli_helpers import _generate_pdf
        from normadocs.pdf_generator import PDFGenerator

        with patch.object(PDFGenerator, "convert", return_value=False):
            result = _generate_pdf("pdf", Path("out.docx"), Path("dir"), "md", Path("out.pdf"))

            self.assertFalse(result)


class TestCleanupDocker(unittest.TestCase):
    """Tests for _cleanup_docker function."""

    def test_cleanup_docker_returns_early_when_no_container(self):
        """Should return early when docker_container is None."""
        from normadocs.cli_helpers import _cleanup_docker

        _cleanup_docker(None, False, 8081)

    def test_cleanup_docker_keeps_container_when_keep_alive(self):
        """Should not call run_command when lt_keep_alive is True."""
        from unittest.mock import patch

        from normadocs.cli_helpers import _cleanup_docker

        with patch("normadocs.cli_helpers.run_command") as mock_run:
            _cleanup_docker("normadocs-lt", True, 8081)

            mock_run.assert_not_called()

    def test_cleanup_docker_removes_container_when_not_keep_alive(self):
        """Should call run_command to remove container when lt_keep_alive is False."""
        from normadocs.cli_helpers import _cleanup_docker

        with (
            patch("normadocs.cli_helpers.get_command_path", return_value="docker"),
            patch("normadocs.cli_helpers.run_command") as mock_run,
        ):
            _cleanup_docker("normadocs-lt", False, 8081)

            mock_run.assert_called_once()


class TestProcessMarkdown(unittest.TestCase):
    """Tests for process_markdown function."""

    def test_process_markdown_raises_exit_on_exception(self):
        """Should raise typer.Exit when processing fails."""
        from pathlib import Path

        import typer

        from normadocs.cli_helpers import process_markdown
        from normadocs.preprocessor import MarkdownPreprocessor

        mock_preprocessor = MagicMock(spec=MarkdownPreprocessor)
        mock_preprocessor.process.side_effect = Exception("Parse error")

        with (
            patch.object(MarkdownPreprocessor, "__init__", return_value=None),
            patch.object(MarkdownPreprocessor, "process", side_effect=Exception("Parse error")),
            self.assertRaises(typer.Exit),
        ):
            process_markdown(Path("test.md"))


class TestLanguageToolResult(unittest.TestCase):
    """Tests for LanguageToolResult NamedTuple."""

    def test_language_tool_result_creation(self):
        """Should create LanguageToolResult with correct fields."""
        result = LanguageToolResult(
            errors=[{"message": "Test error"}],
            all_errors=[("rule1", [{"message": "Error"}])],
        )
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.all_errors), 1)

    def test_language_tool_result_access(self):
        """Should access fields by name."""
        result = LanguageToolResult(
            errors=[{"message": "Error 1"}],
            all_errors=[("RULE", [{"message": "Error"}])],
        )
        self.assertEqual(result.errors[0]["message"], "Error 1")
        self.assertEqual(result.all_errors[0][0], "RULE")


if __name__ == "__main__":
    unittest.main()

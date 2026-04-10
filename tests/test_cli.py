"""
Tests for CLI.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from normadocs.cli import app

runner = CliRunner()


class TestCLI(unittest.TestCase):
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli.logger")
    def test_convert_command_success(self, mock_logger, mock_pre, mock_get_fmt, mock_pandoc):
        # Mock file operations
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            result = runner.invoke(app, ["test.md"])

            self.assertEqual(result.exit_code, 0)

            # Verify logger calls instead of stdout
            self.assertTrue(mock_logger.info.called)
            # Check logic that logs were actually made
            # We can inspect the calls if needed, but existence is enough for basic verification
            # that we aren't crashing and are reaching the log points.

    def test_convert_command_file_not_found(self):
        result = runner.invoke(app, ["non_existent.md"])
        self.assertNotEqual(result.exit_code, 0)
        # Typer/Click handles file validation; error may appear in output or as exception
        error_output = (result.output or "").lower()
        has_error_msg = (
            "does not exist" in error_output
            or "invalid" in error_output
            or "error" in error_output
            or "no such file" in error_output
            or result.exception is not None
        )
        self.assertTrue(has_error_msg, f"Expected error message, got: {result.output}")


class TestCLILanguageTool(unittest.TestCase):
    """Tests for LanguageTool CLI options."""

    @patch("subprocess.run")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_language_tool_option_exists(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Test that --language-tool option is accepted."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            # Mock LanguageTool client
            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            mock_lt_instance.check.return_value = []
            mock_lt_class.return_value = mock_lt_instance

            # Mock Document
            mock_doc.return_value = MagicMock(paragraphs=[])

            result = runner.invoke(app, ["test.md", "--language-tool", "es"])

            # Should not fail due to unknown option
            self.assertEqual(result.exit_code, 0)

    @patch("subprocess.run")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_language_tool_custom_port(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Test that --lt-port option is accepted."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            # Mock LanguageTool client
            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            mock_lt_instance.check.return_value = []
            mock_lt_class.return_value = mock_lt_instance

            # Mock Document
            mock_doc.return_value = MagicMock(paragraphs=[])

            result = runner.invoke(app, ["test.md", "--language-tool", "es", "--lt-port", "9000"])

            # Should complete without error
            self.assertEqual(result.exit_code, 0)

    @patch("subprocess.run")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_language_tool_keep_alive_option(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Test that --lt-keep-alive option is accepted."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            # Mock LanguageTool client
            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            mock_lt_instance.check.return_value = []
            mock_lt_class.return_value = mock_lt_instance

            # Mock Document
            mock_doc.return_value = MagicMock(paragraphs=[])

            result = runner.invoke(app, ["test.md", "--language-tool", "es", "--lt-keep-alive"])

            # Should complete without error
            self.assertEqual(result.exit_code, 0)

    @patch("subprocess.run")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_language_tool_report_option(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Test that --lt-report option saves a report file."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent with erro")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            # Mock LanguageTool client
            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            mock_lt_instance.check.return_value = [
                MagicMock(message="Error", context="ctx", replacements=["fix"])
            ]
            mock_lt_class.return_value = mock_lt_instance

            # Mock Document
            mock_doc.return_value = MagicMock(paragraphs=[])

            # Use --lt-continue-on-error so conversion completes and report is saved
            runner.invoke(
                app,
                [
                    "test.md",
                    "--language-tool",
                    "es",
                    "--lt-report",
                    "report.md",
                    "--lt-continue-on-error",
                ],
            )

            # Should create report file
            self.assertTrue(Path("report.md").exists())


class TestCLILanguageToolErrors(unittest.TestCase):
    """Tests for LanguageTool error handling in CLI."""

    @patch("subprocess.run")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_language_tool_error_stops_conversion(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Test that errors stop conversion when --lt-stop-on-error (default)."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent with erro")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            # Mock LanguageTool client with error
            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            mock_lt_instance.check.return_value = [
                MagicMock(message="Spelling error", context="erro", replacements=["error"])
            ]
            mock_lt_class.return_value = mock_lt_instance

            result = runner.invoke(app, ["test.md", "--language-tool", "es"])

            # Should fail due to error
            self.assertNotEqual(result.exit_code, 0)

    @patch("subprocess.run")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_language_tool_continue_on_error(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Test that errors don't stop conversion with --lt-continue-on-error."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent with erro")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            # Mock LanguageTool client with error
            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            mock_lt_instance.check.return_value = [
                MagicMock(message="Spelling error", context="erro", replacements=["error"])
            ]
            mock_lt_class.return_value = mock_lt_instance

            # Mock Document
            mock_doc.return_value = MagicMock(paragraphs=[])

            result = runner.invoke(
                app, ["test.md", "--language-tool", "es", "--lt-continue-on-error"]
            )

            # Should complete successfully despite error
            self.assertEqual(result.exit_code, 0)


class TestCLILanguageToolDocker(unittest.TestCase):
    """Tests for LanguageTool Docker integration in CLI."""

    @patch("subprocess.run")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_language_tool_docker_option(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Test that --lt-docker option is accepted."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            # Setup mocks
            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            # Mock LanguageTool client
            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            mock_lt_instance.check.return_value = []
            mock_lt_class.return_value = mock_lt_instance

            # Mock Document
            mock_doc.return_value = MagicMock(paragraphs=[])

            result = runner.invoke(app, ["test.md", "--language-tool", "es", "--lt-docker"])

            # Should complete without error
            self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()

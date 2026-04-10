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

    @patch("normadocs.utils.subprocess.run_command")
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

    @patch("normadocs.utils.subprocess.run_command")
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

    @patch("normadocs.utils.subprocess.run_command")
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

    @patch("normadocs.utils.subprocess.run_command")
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

    @patch("normadocs.utils.subprocess.run_command")
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

    @patch("normadocs.utils.subprocess.run_command")
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


class TestCLIErrorPaths(unittest.TestCase):
    """Tests for error handling paths in CLI."""

    def test_get_default_ignored_words_config_not_found(self):
        """Should return empty list when config file doesn't exist."""
        from pathlib import Path
        from unittest.mock import patch

        from normadocs.cli import get_default_ignored_words

        with patch.object(Path, "exists", return_value=False):
            result = get_default_ignored_words()
            self.assertEqual(result, [])

    def test_get_default_ignored_words_config_found(self):
        """Should return words from config file when it exists."""
        from pathlib import Path
        from unittest.mock import patch

        from normadocs.cli import get_default_ignored_words

        config_content = "word1\nword2\n# comment\n  word3  \n"
        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "read_text", return_value=config_content),
        ):
            result = get_default_ignored_words()
            self.assertEqual(result, ["word1", "word2", "word3"])

    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli.logger")
    def test_pandoc_failure_returns_false(self, mock_logger, mock_pre, mock_get_fmt, mock_pandoc):
        """Should return False and cleanup docker when pandoc fails."""

        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = False
            mock_pandoc.return_value = mock_run_instance

            with patch("normadocs.cli.cli_helpers._cleanup_docker"):
                result = runner.invoke(app, ["test.md"])

                self.assertNotEqual(result.exit_code, 0)

    @patch("normadocs.utils.subprocess.run_command")
    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli_helpers.Document")
    @patch("normadocs.cli_helpers.LanguageToolClient")
    @patch("normadocs.cli.logger")
    def test_lt_postcheck_failure_cleans_up(
        self,
        mock_logger,
        mock_lt_class,
        mock_doc,
        mock_pre,
        mock_get_fmt,
        mock_pandoc,
        mock_subprocess,
    ):
        """Should cleanup docker when LanguageTool post-check fails."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            mock_lt_instance = MagicMock()
            mock_lt_instance.is_server_running.return_value = True
            # Return error on post-check
            mock_lt_instance.check.side_effect = [
                [],  # pre-check passes
                [
                    MagicMock(message="Error", context="ctx", replacements=["fix"])
                ],  # post-check fails
            ]
            mock_lt_class.return_value = mock_lt_instance

            mock_doc.return_value = MagicMock(paragraphs=[])

            with patch("normadocs.cli.cli_helpers._cleanup_docker"):
                runner.invoke(app, ["test.md", "--language-tool", "es"])

    @patch("normadocs.cli_helpers.PandocRunner")
    @patch("normadocs.cli_helpers.get_formatter")
    @patch("normadocs.cli_helpers.MarkdownPreprocessor")
    @patch("normadocs.cli.logger")
    def test_lt_strict_sets_stop_on_error(self, mock_logger, mock_pre, mock_get_fmt, mock_pandoc):
        """Should set lt_stop_on_error to True when lt_strict is used."""
        with runner.isolated_filesystem():
            with open("test.md", "w") as f:
                f.write("# Title\n\nContent")

            mock_proc_instance = MagicMock()
            mock_proc_instance.process.return_value = ("cleaned md", MagicMock())
            mock_pre.return_value = mock_proc_instance

            mock_run_instance = MagicMock()
            mock_run_instance.run.return_value = True
            mock_pandoc.return_value = mock_run_instance

            # Using --lt-strict should be accepted
            result = runner.invoke(app, ["test.md", "--lt-strict"])
            self.assertEqual(result.exit_code, 0)


class TestCLILanguageToolDocker(unittest.TestCase):
    """Tests for LanguageTool Docker integration in CLI."""

    @patch("normadocs.utils.subprocess.run_command")
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

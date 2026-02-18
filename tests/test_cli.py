"""
Tests for CLI.
"""

import unittest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from normadocs.cli import app

runner = CliRunner()


class TestCLI(unittest.TestCase):
    @patch("normadocs.cli.PandocRunner")
    @patch("normadocs.cli.APADocxFormatter")
    @patch("normadocs.cli.MarkdownPreprocessor")
    @patch("normadocs.cli.logger")
    def test_convert_command_success(self, mock_logger, mock_pre, mock_fmt, mock_pandoc):
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
        # Typer handles this argument validation
        self.assertIn("does not", result.stdout.lower())
        self.assertIn("exist", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()

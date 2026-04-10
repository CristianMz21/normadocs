"""
Tests for Pandoc Client.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from normadocs.pandoc_client import PandocRunner
from normadocs.utils.subprocess import CommandFailedError


class TestPandocClient(unittest.TestCase):
    @patch("normadocs.pandoc_client.run_command")
    def test_run_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        runner = PandocRunner()
        success = runner.run("# Title", "output.docx")

        self.assertTrue(success)
        mock_run.assert_called_once()

        args, _ = mock_run.call_args
        cmd = args[0]
        self.assertIn("pandoc", cmd[0])
        self.assertIn("-o", cmd)
        self.assertIn(str(Path("output.docx").absolute()), cmd)

    @patch("normadocs.pandoc_client.run_command")
    def test_run_failure_pandoc_error(self, mock_run):
        def raise_error(*args, **kwargs):
            raise CommandFailedError(
                returncode=1, cmd=["pandoc"], stdout="", stderr="Error converting"
            )

        mock_run.side_effect = raise_error

        runner = PandocRunner()
        success = runner.run("# Title", "output.docx")

        self.assertFalse(success)

    @patch("normadocs.pandoc_client.get_command_path")
    def test_run_pandoc_not_found(self, mock_get_path):
        mock_get_path.side_effect = FileNotFoundError

        runner = PandocRunner()
        success = runner.run("# Title", "output.docx")

        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()

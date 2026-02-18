"""
Tests for Pandoc Client.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from normadocs.pandoc_client import PandocRunner


class TestPandocClient(unittest.TestCase):
    @patch("subprocess.run")
    def test_run_success(self, mock_run):
        # Setup mock to return success
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        runner = PandocRunner()
        success = runner.run("# Title", "output.docx")

        self.assertTrue(success)
        mock_run.assert_called_once()

        # Verify args
        args, _ = mock_run.call_args
        cmd = args[0]
        self.assertEqual(cmd[0], "pandoc")
        self.assertIn("-o", cmd)
        self.assertIn(str(Path("output.docx").absolute()), cmd)

    @patch("subprocess.run")
    def test_run_failure_pandoc_error(self, mock_run):
        # Setup mock to return error code
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error converting"
        mock_run.return_value = mock_result

        runner = PandocRunner()
        success = runner.run("# Title", "output.docx")

        self.assertFalse(success)

    @patch("subprocess.run")
    def test_run_pandoc_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError

        runner = PandocRunner()
        success = runner.run("# Title", "output.docx")

        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()

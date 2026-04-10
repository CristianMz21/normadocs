"""
Tests for CLI helper functions.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from docx import Document

from normadocs.cli_helpers import (
    LanguageToolResult,
    _setup_languagetool_client,
    _ensure_languagetool_server,
)
from normadocs.languagetool_client import LanguageToolClient


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
            result = _setup_languagetool_client(
                language_tool="es",
                lt_host="localhost",
                lt_port=8081,
                lt_enabled_rules=None,
                lt_disabled_rules=None,
                lt_ignore_words=None,
                lt_no_spelling=False,
                default_ignore_words=["word1", "word2"],
            )
            self.assertIsInstance(result, LanguageToolClient)
            mock_init.assert_called_once()

    def test_creates_client_with_custom_enabled_rules(self):
        """Should create client with enabled rules split from comma string."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            result = _setup_languagetool_client(
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
            result = _setup_languagetool_client(
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
        """Should create client with empty ignore words list when lt_ignore_words is empty string."""
        with patch.object(LanguageToolClient, "__init__", return_value=None) as mock_init:
            result = _setup_languagetool_client(
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
            result = _setup_languagetool_client(
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
            result = _setup_languagetool_client(
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

    @patch("subprocess.run")
    def test_raises_exit_on_subprocess_error(self, mock_run):
        """Should raise typer.Exit when subprocess fails with CalledProcessError."""
        import typer

        mock_client = MagicMock(spec=LanguageToolClient)
        mock_client.is_server_running.return_value = False

        error = subprocess.CalledProcessError(1, "docker")
        error.stderr = b"Docker error"
        mock_run.side_effect = error

        with self.assertRaises(typer.Exit):
            _ensure_languagetool_server(mock_client, lt_docker=True, lt_port=8081)


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

"""
Tests for LanguageTool client module.
"""

import unittest
from unittest.mock import MagicMock, patch

from normadocs.languagetool_client import (
    LanguageToolClient,
    LanguageToolError,
    format_errors,
)


class TestLanguageToolError(unittest.TestCase):
    """Tests for LanguageToolError dataclass."""

    def test_language_tool_error_creation(self):
        """Test creating a LanguageToolError instance."""
        error = LanguageToolError(
            message="Spelling error",
            context="test context",
            rule_id="MISC_SPELLING",
            offset=5,
            length=10,
            replacements=["test", "best"],
        )
        self.assertEqual(error.message, "Spelling error")
        self.assertEqual(error.context, "test context")
        self.assertEqual(error.rule_id, "MISC_SPELLING")
        self.assertEqual(error.offset, 5)
        self.assertEqual(error.length, 10)
        self.assertEqual(error.replacements, ["test", "best"])


class TestLanguageToolClient(unittest.TestCase):
    """Tests for LanguageToolClient class."""

    def test_client_initialization(self):
        """Test client initialization with default values."""
        client = LanguageToolClient()
        self.assertEqual(client.base_url, "http://localhost:8081")
        self.assertEqual(client.language, "es")
        self.assertIsNone(client._server_process)

    def test_client_initialization_custom(self):
        """Test client initialization with custom values."""
        client = LanguageToolClient(host="192.168.1.1", port=9000, language="en")
        self.assertEqual(client.base_url, "http://192.168.1.1:9000")
        self.assertEqual(client.language, "en")

    @patch("normadocs.languagetool_client.requests")
    def test_is_server_running_true(self, mock_requests):
        """Test is_server_running returns True when server responds."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        client = LanguageToolClient()
        self.assertTrue(client.is_server_running())

    @patch("normadocs.languagetool_client.requests")
    def test_is_server_running_exception(self, mock_requests):
        """Test is_server_running returns False when exception occurs."""
        # Setup mock with exceptions attribute
        mock_requests.exceptions = MagicMock()
        mock_requests.exceptions.RequestException = Exception
        mock_requests.get.side_effect = Exception("Connection refused")

        client = LanguageToolClient()
        self.assertFalse(client.is_server_running())

    @patch("normadocs.languagetool_client.requests")
    def test_is_server_running_non_200(self, mock_requests):
        """Test is_server_running returns False for non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests.get.return_value = mock_response

        client = LanguageToolClient()
        self.assertFalse(client.is_server_running())

    def test_check_empty_text(self):
        """Test check returns empty list for empty text."""
        client = LanguageToolClient()
        result = client.check("")
        self.assertEqual(result, [])

    def test_check_whitespace_only(self):
        """Test check returns empty list for whitespace only."""
        client = LanguageToolClient()
        result = client.check("   \n\t   ")
        self.assertEqual(result, [])

    @patch("normadocs.languagetool_client.requests")
    def test_check_success(self, mock_requests):
        """Test successful check returns parsed errors."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "matches": [
                {
                    "message": "Spelling error",
                    "context": {"text": "test context"},
                    "rule": {"id": "MISC_SPELLING"},
                    "offset": 5,
                    "length": 10,
                    "replacements": [{"value": "test"}, {"value": "best"}],
                }
            ]
        }
        mock_requests.post.return_value = mock_response

        client = LanguageToolClient(language="es")
        result = client.check("This has a erro")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].message, "Spelling error")
        self.assertEqual(result[0].context, "test context")
        self.assertEqual(result[0].rule_id, "MISC_SPELLING")
        self.assertEqual(result[0].replacements, ["test", "best"])

    @patch("normadocs.languagetool_client.requests")
    def test_check_no_errors(self, mock_requests):
        """Test check returns empty list when no errors found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"matches": []}
        mock_requests.post.return_value = mock_response

        client = LanguageToolClient()
        result = client.check("This is correct text")

        self.assertEqual(result, [])

    @patch("normadocs.languagetool_client.requests")
    def test_check_request_exception(self, mock_requests):
        """Test check raises RuntimeError on request failure."""
        # Setup mock with exceptions attribute
        mock_requests.exceptions = MagicMock()
        mock_requests.exceptions.RequestException = Exception
        mock_requests.post.side_effect = Exception("Connection refused")

        client = LanguageToolClient()
        with self.assertRaises(RuntimeError) as ctx:
            client.check("Some text")

        self.assertIn("LanguageTool request failed", str(ctx.exception))

    def test_parse_errors_multiple(self):
        """Test _parse_errors handles multiple matches."""
        client = LanguageToolClient()
        data = {
            "matches": [
                {
                    "message": "Error 1",
                    "context": {"text": "context 1"},
                    "rule": {"id": "RULE_1"},
                    "offset": 0,
                    "length": 5,
                    "replacements": [{"value": "fix1"}],
                },
                {
                    "message": "Error 2",
                    "context": {"text": "context 2"},
                    "rule": {"id": "RULE_2"},
                    "offset": 10,
                    "length": 8,
                    "replacements": [{"value": "fix2"}],
                },
            ]
        }

        result = client._parse_errors(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].message, "Error 1")
        self.assertEqual(result[1].message, "Error 2")

    def test_parse_errors_missing_fields(self):
        """Test _parse_errors handles missing fields gracefully."""
        client = LanguageToolClient()
        data = {
            "matches": [
                {
                    "message": "Error without context",
                }
            ]
        }

        result = client._parse_errors(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].message, "Error without context")
        self.assertEqual(result[0].context, "")
        self.assertEqual(result[0].rule_id, "")
        self.assertEqual(result[0].replacements, [])

    def test_get_port_from_url(self):
        """Test _get_port_from_url extracts correct port."""
        client = LanguageToolClient(port=8081)
        self.assertEqual(client._get_port_from_url(), 8081)

        client = LanguageToolClient(port=9000)
        self.assertEqual(client._get_port_from_url(), 9000)

    def test_stop_server(self):
        """Test stop_server terminates the process."""
        client = LanguageToolClient()
        mock_process = MagicMock()
        client._server_process = mock_process

        client.stop_server()

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=10)
        self.assertIsNone(client._server_process)

    def test_stop_server_no_process(self):
        """Test stop_server does nothing when no process."""
        client = LanguageToolClient()
        client._server_process = None

        # Should not raise
        client.stop_server()


class TestFormatErrors(unittest.TestCase):
    """Tests for format_errors function."""

    def test_format_errors_empty(self):
        """Test format_errors returns empty string for empty list."""
        result = format_errors([])
        self.assertEqual(result, "")

    def test_format_errors_single(self):
        """Test format_errors formats single error correctly."""
        errors = [
            LanguageToolError(
                message="Spelling error",
                context="test context",
                rule_id="MISC",
                offset=5,
                length=10,
                replacements=["test", "best"],
            )
        ]

        result = format_errors(errors)

        self.assertIn("1 error(es)", result)
        self.assertIn("Spelling error", result)
        self.assertIn("test context", result)
        self.assertIn("test, best", result)

    def test_format_errors_multiple(self):
        """Test format_errors formats multiple errors correctly."""
        errors = [
            LanguageToolError(
                message="Error 1", context="", rule_id="", offset=0, length=0, replacements=[]
            ),
            LanguageToolError(
                message="Error 2", context="", rule_id="", offset=0, length=0, replacements=[]
            ),
        ]

        result = format_errors(errors)

        self.assertIn("2 error(es)", result)
        self.assertIn("1. Error 1", result)
        self.assertIn("2. Error 2", result)

    def test_format_errors_no_context(self):
        """Test format_errors handles missing context."""
        errors = [
            LanguageToolError(
                message="Error", context="", rule_id="", offset=0, length=0, replacements=[]
            )
        ]

        result = format_errors(errors)

        self.assertIn("Error", result)
        self.assertNotIn("Contexto", result)

    def test_format_errors_no_replacements(self):
        """Test format_errors handles missing replacements."""
        errors = [
            LanguageToolError(
                message="Error", context="ctx", rule_id="", offset=0, length=0, replacements=[]
            )
        ]

        result = format_errors(errors)

        self.assertIn("ctx", result)
        self.assertNotIn("Sugerencias", result)

    def test_format_errors_limited_replacements(self):
        """Test format_errors limits replacements to 3."""
        errors = [
            LanguageToolError(
                message="Error",
                context="",
                rule_id="",
                offset=0,
                length=0,
                replacements=["a", "b", "c", "d", "e"],
            )
        ]

        result = format_errors(errors)

        self.assertIn("a, b, c", result)
        self.assertNotIn("d", result)


if __name__ == "__main__":
    unittest.main()

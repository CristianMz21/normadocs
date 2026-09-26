"""
Tests for normadocs.sql_formatter module.
"""

import unittest
from unittest.mock import patch


class TestIsSqlLang(unittest.TestCase):
    """Tests for is_sql_lang language detection."""

    def test_lowercase_sql_is_sql(self):
        """Lowercase sql is detected as SQL."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertTrue(is_sql_lang("sql"))

    def test_uppercase_sql_is_sql(self):
        """Uppercase SQL is detected as SQL."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertTrue(is_sql_lang("SQL"))

    def test_mixed_case_sql_is_sql(self):
        """Mixed-case Sql is detected as SQL."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertTrue(is_sql_lang("Sql"))

    def test_padded_sql_is_sql(self):
        """Surrounding whitespace does not affect detection."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertTrue(is_sql_lang("  sql  "))

    def test_python_is_not_sql(self):
        """Python blocks are not SQL."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertFalse(is_sql_lang("python"))

    def test_mysql_alias_is_not_sql(self):
        """Dialect aliases stay out of scope for v1."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertFalse(is_sql_lang("mysql"))

    def test_empty_lang_is_not_sql(self):
        """Empty language is not SQL."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertFalse(is_sql_lang(""))

    def test_plain_text_is_not_sql(self):
        """Plain text language is not SQL."""
        from normadocs.sql_formatter import is_sql_lang

        self.assertFalse(is_sql_lang("text"))


class TestFormatSql(unittest.TestCase):
    """Tests for format_sql formatting behavior."""

    def test_lowercase_keywords_uppercased(self):
        """Lowercase keywords are uppercased."""
        from normadocs.sql_formatter import format_sql

        result = format_sql("select a from t where a > 1")

        self.assertIn("SELECT", result)
        self.assertIn("FROM", result)
        self.assertIn("WHERE", result)

    def test_multiline_query_reindented(self):
        """Single-line multi-clause query is split across lines."""
        from normadocs.sql_formatter import format_sql

        result = format_sql("select a, b from t where a > 1 order by b")

        self.assertIn("\n", result)
        self.assertIn("SELECT", result)
        self.assertIn("FROM", result)

    def test_empty_input_passthrough(self):
        """Empty code is returned unchanged."""
        from normadocs.sql_formatter import format_sql

        self.assertEqual(format_sql(""), "")

    def test_whitespace_input_passthrough(self):
        """Whitespace-only code is returned unchanged."""
        from normadocs.sql_formatter import format_sql

        self.assertEqual(format_sql("   \n  "), "   \n  ")

    def test_comments_preserved(self):
        """Inline comments survive formatting."""
        from normadocs.sql_formatter import format_sql

        result = format_sql("select a from t -- fetch all rows\nwhere a > 1")

        self.assertIn("-- fetch all rows", result)

    def test_missing_dependency_fallback(self):
        """Without sqlparse the original code is returned unchanged."""
        from normadocs.sql_formatter import format_sql

        code = "select a from t where a > 1"
        with patch("importlib.util.find_spec", return_value=None):
            self.assertEqual(format_sql(code), code)

    def test_malformed_sql_fallback(self):
        """Formatter exceptions degrade to the original code."""
        from normadocs.sql_formatter import format_sql

        code = "select a from t where a > 1"
        with patch("sqlparse.format", side_effect=Exception("boom")):
            self.assertEqual(format_sql(code), code)

    def test_idempotent_formatting(self):
        """Formatting twice yields byte-identical output."""
        from normadocs.sql_formatter import format_sql

        once = format_sql("select a from t where a > 1")
        twice = format_sql(once)

        self.assertEqual(once, twice)

    def test_returns_str(self):
        """Formatter always returns a string."""
        from normadocs.sql_formatter import format_sql

        self.assertIsInstance(format_sql("select 1"), str)


if __name__ == "__main__":
    unittest.main()

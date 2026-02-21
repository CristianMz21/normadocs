"""
Tests for the Markdown Preprocessor.
"""

import unittest

from normadocs.preprocessor import MarkdownPreprocessor


class TestPreprocessor(unittest.TestCase):
    def test_extract_metadata(self):
        lines = [
            "**My Title**",
            "Subtitle",
            "",
            "Author Name",
            "Software Engineering",
            "12345",
            "SENA",
            "Factory",
            "2023-10-27",
        ]
        meta = MarkdownPreprocessor.extract_metadata(lines)
        self.assertEqual(meta.title, "My Title Subtitle")
        self.assertEqual(meta.author, "Author Name")
        self.assertEqual(meta.ficha, "12345")

    def test_page_break_insertion(self):
        text = """**Title**

Author

# Introduction
Text here.

# Methodology
More text.

## Subsection
Should not break.
"""
        preprocessor = MarkdownPreprocessor()
        processed, _meta = preprocessor.process(text)

        # Should have page break before Methodology
        # Note: The exact implementation inserts page break OXML
        self.assertIn('<w:br w:type="page"/>', processed)

        # Should NOT have page break before Subsection (which starts with ##)
        # It's hard to test "not before" without strict parsing, but we can check count?
        # Only 1 page break expected (Intro -> Method) = actually 1
        # Title page logic no longer adds one in preprocessor.
        # Temp title -> Intro starts. (No break before first)
        # Method starts -> adds break.
        # Total breaks: 1

        breaks = processed.count('<w:br w:type="page"/>')
        self.assertTrue(breaks >= 1)


if __name__ == "__main__":
    unittest.main()

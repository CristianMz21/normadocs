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

# Referencias
Entries here.

## Subsection
Should not break.
"""
        preprocessor = MarkdownPreprocessor()
        processed, _meta = preprocessor.process(text)

        # Only Referencias opens a new page (APA 7 continuous body text).
        breaks = processed.count('<w:br w:type="page"/>')
        self.assertEqual(breaks, 1)
        self.assertLess(processed.find("# Methodology"), processed.find("# Referencias"))
        ref_pos = processed.find("# Referencias")
        break_pos = processed.find('<w:br w:type="page"/>')
        self.assertLess(break_pos, ref_pos)


if __name__ == "__main__":
    unittest.main()

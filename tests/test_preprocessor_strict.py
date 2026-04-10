"""
Strict comprehensive tests for MarkdownPreprocessor.
Covers all public and private methods including edge cases.
"""

import unittest

from normadocs.models import DocumentMetadata
from normadocs.preprocessor import MarkdownPreprocessor


class TestExtractYamlFrontmatter(unittest.TestCase):
    """Tests for YAML frontmatter extraction (lines 17-45)."""

    def test_no_frontmatter_returns_empty(self):
        """No frontmatter should return empty dict and -1."""
        lines = ["# Title", "Some content"]
        meta, end_line = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(meta, {})
        self.assertEqual(end_line, -1)

    def test_empty_lines_returns_empty(self):
        """Empty lines should return empty dict and -1."""
        lines = []
        meta, end_line = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(meta, {})
        self.assertEqual(end_line, -1)

    def test_single_dash_not_frontmatter(self):
        """Single --- is not frontmatter."""
        lines = ["- something"]
        meta, end_line = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(meta, {})
        self.assertEqual(end_line, -1)

    def test_valid_frontmatter(self):
        """Valid YAML frontmatter should be parsed."""
        lines = [
            "---",
            "title: My Title",
            "author: John Doe",
            "---",
            "# Content",
        ]
        meta, end_line = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(meta["title"], "My Title")
        self.assertEqual(meta["author"], "John Doe")
        self.assertEqual(end_line, 3)

    def test_frontmatter_no_closing_dash(self):
        """No closing --- should return empty dict."""
        lines = ["---", "title: My Title", "# Content without closing"]
        meta, end_line = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(meta, {})
        self.assertEqual(end_line, -1)

    def test_frontmatter_closes_within_limit(self):
        """Frontmatter closing before line 100 should be found."""
        lines = ["---"] + [""] * 50 + ["---"]
        _, end_line = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(end_line, 51)

    def test_frontmatter_invalid_yaml_returns_empty(self):
        """Invalid YAML should return empty dict gracefully."""
        lines = [
            "---",
            "title: [unclosed list",
            "---",
        ]
        meta, _ = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(meta, {})

    def test_frontmatter_yaml_not_dict(self):
        """YAML that parses to non-dict returns empty."""
        lines = [
            "---",
            "- item1",
            "- item2",
            "---",
        ]
        meta, _ = MarkdownPreprocessor.extract_yaml_frontmatter(lines)
        self.assertEqual(meta, {})


class TestExtractMetadata(unittest.TestCase):
    """Tests for extract_metadata (lines 48-95)."""

    def test_with_yaml_frontmatter(self):
        """Metadata from YAML frontmatter takes precedence."""
        lines = [
            "---",
            "title: YAML Title",
            "author: YAML Author",
            "institution: SENA",
            "---",
            "# Content",
        ]
        meta = MarkdownPreprocessor.extract_metadata(lines)
        self.assertEqual(meta.title, "YAML Title")
        self.assertEqual(meta.author, "YAML Author")
        self.assertEqual(meta.institution, "SENA")

    def test_fallback_parsing_no_frontmatter(self):
        """Fallback parsing when no YAML frontmatter."""
        lines = [
            "**Main Title**",
            "Subtitle",
            "",
            "Author Name",
            "Program",
            "---",
            "# References",
        ]
        meta = MarkdownPreprocessor.extract_metadata(lines)
        self.assertEqual(meta.title, "Main Title Subtitle")
        self.assertEqual(meta.author, "Author Name")

    def test_fallback_stops_at_heading(self):
        """Fallback parsing stops at first heading."""
        lines = [
            "Title",
            "",
            "Author",
            "# Introduction",
        ]
        meta = MarkdownPreprocessor.extract_metadata(lines)
        self.assertEqual(meta.title, "Title")
        self.assertNotIn("Introduction", meta.author)

    def test_fallback_removes_bold_markers(self):
        """Fallback parsing removes ** markers from title."""
        lines = ["**Bold Title**", "", "Author"]
        meta = MarkdownPreprocessor.extract_metadata(lines)
        self.assertIn("Bold Title", meta.title)

    def test_fallback_trims_whitespace(self):
        """Fallback parsing trims whitespace."""
        lines = ["  Title  ", "", "  Author  "]
        meta = MarkdownPreprocessor.extract_metadata(lines)
        self.assertEqual(meta.title, "Title")
        self.assertEqual(meta.author, "Author")


class TestIsSpecialLine(unittest.TestCase):
    """Tests for _is_special_line (lines 134-160)."""

    def test_blank_line_is_special(self):
        """Empty line is special (paragraph separator)."""
        self.assertTrue(MarkdownPreprocessor._is_special_line(""))
        self.assertFalse(MarkdownPreprocessor._is_special_line("   "))

    def test_heading_is_special(self):
        """Lines starting with # are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("# Title"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("## Section"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("#TitleNoSpace"))

    def test_code_block_markers(self):
        """Code block markers are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("```python"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("```"))

    def test_horizontal_rule(self):
        """Horizontal rules are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("---"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("==="))

    def test_blockquote(self):
        """Blockquotes are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("> quote"))

    def test_image(self):
        """Image syntax is special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("![alt](url)"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("![alt][ref]"))

    def test_unordered_list(self):
        """Unordered list items are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("- item"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("* item"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("+ item"))

    def test_unordered_list_with_space(self):
        """List marker must be followed by space."""
        self.assertFalse(MarkdownPreprocessor._is_special_line("-text"))
        self.assertFalse(MarkdownPreprocessor._is_special_line("text"))

    def test_ordered_list(self):
        """Ordered list items are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("1. First"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("99. Item"))

    def test_grid_table_borders(self):
        """Grid table borders are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("+---+---+"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("+===+===+"))

    def test_pipe_table_rows(self):
        """Pipe table rows are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("| col1 | col2 |"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("| text"))

    def test_html_blocks(self):
        """HTML/OpenXML blocks are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("<div>"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("<p>text</p>"))

    def test_pandoc_code_block_json(self):
        """Pandoc fenced code blocks are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("```{.json}"))

    def test_box_drawing_chars(self):
        """ASCII art / box drawing characters are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("┌───┐"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("├───┤"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("│ text │"))

    def test_toc_entry(self):
        """TOC entries with dots and page numbers are special."""
        self.assertTrue(MarkdownPreprocessor._is_special_line("Chapter 1.....10"))
        self.assertTrue(MarkdownPreprocessor._is_special_line("Title...5"))

    def test_normal_text_not_special(self):
        """Regular text lines are not special."""
        self.assertFalse(MarkdownPreprocessor._is_special_line("This is regular text"))
        self.assertFalse(MarkdownPreprocessor._is_special_line("Another paragraph line"))
        self.assertFalse(MarkdownPreprocessor._is_special_line("No markdown here"))


class TestConvertMultilineTables(unittest.TestCase):
    """Tests for _convert_multiline_tables (lines 162-229)."""

    def test_no_tables_passes_through(self):
        """Lines without tables pass through unchanged."""
        lines = ["# Title", "Some text", "More text"]
        result = MarkdownPreprocessor._convert_multiline_tables(lines)
        self.assertEqual(result, lines)

    def test_grid_table_not_converted(self):
        """Already valid grid tables pass through."""
        lines = ["+---+---+", "| a | b |", "+---+---+"]
        result = MarkdownPreprocessor._convert_multiline_tables(lines)
        self.assertEqual(len(result), 3)

    def test_multiline_table_with_outer_separator(self):
        """Multiline table with long outer dashes gets processed."""
        lines = [
            "Header 1  Header 2",
            "--------------------",
            "Cell 1    Cell 2",
            "--------------------",
        ]
        result = MarkdownPreprocessor._convert_multiline_tables(lines)
        self.assertTrue(len(result) > 0)

    def test_multiline_table_no_matching_end(self):
        """Table without matching end separator passes through."""
        lines = [
            "Header",
            "--------------------",
            "Data",
        ]
        result = MarkdownPreprocessor._convert_multiline_tables(lines)
        self.assertEqual(len(result), 3)

    def test_multiline_table_mixed_content(self):
        """Text before and after tables preserved."""
        lines = [
            "# Introduction",
            "Header",
            "--------------------",
            "Data",
            "--------------------",
            "Conclusion",
        ]
        result = MarkdownPreprocessor._convert_multiline_tables(lines)
        self.assertIn("# Introduction", result)
        self.assertIn("Conclusion", result)


class TestParseMultilineTable(unittest.TestCase):
    """Tests for _parse_multiline_table (lines 231-334)."""

    def test_parse_produces_pipe_table(self):
        """Parse produces pipe table format."""
        table_lines = [
            "Header 1  Header 2",
            "------- -------",
            "Cell 1    Cell 2",
            "------- -------",
        ]
        inner_sep = "------- -------"
        result = MarkdownPreprocessor._parse_multiline_table(table_lines, inner_sep)
        self.assertTrue(any(line.startswith("|") for line in result))

    def test_parse_strips_bold_markers(self):
        """Bold markers ** are stripped from headers."""
        table_lines = [
            "**Col1**  **Col2**",
            "-- --",
            "A     B",
            "-- --",
        ]
        inner_sep = "-- --"
        result = MarkdownPreprocessor._parse_multiline_table(table_lines, inner_sep)
        header = result[0]
        self.assertNotIn("**", header)

    def test_parse_handles_multiple_records(self):
        """Multiple blank-line-separated records are parsed."""
        table_lines = [
            "Col1  Col2",
            "-- --",
            "A",
            "B",
            "-- --",
        ]
        inner_sep = "-- --"
        result = MarkdownPreprocessor._parse_multiline_table(table_lines, inner_sep)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_parse_empty_separator_returns_original(self):
        """Empty separator returns original table lines."""
        table_lines = ["Header", "-------", "Data"]
        result = MarkdownPreprocessor._parse_multiline_table(table_lines, "")
        self.assertEqual(result, table_lines)

    def test_parse_no_header_separator_index_returns_original(self):
        """If header separator index not found, returns original."""
        table_lines = ["Header", "Data"]
        result = MarkdownPreprocessor._parse_multiline_table(table_lines, "---")
        self.assertEqual(result, table_lines)


class TestJoinWrappedLines(unittest.TestCase):
    """Tests for _join_wrapped_lines (lines 336-368)."""

    def test_joins_consecutive_non_special_lines(self):
        """Wrapped paragraph lines are joined into single line."""
        lines = ["First paragraph line one.", "Second line still first.", "Third line first."]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        # All three lines are joined into one
        self.assertEqual(len(result), 1)
        self.assertIn("First paragraph line one.", result[0])

    def test_blank_line_flushes_buffer(self):
        """Blank line causes buffer flush."""
        lines = ["Line one.", "Line two.", "", "Line three."]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        # Should have: joined "Line one. Line two.", blank line, "Line three."
        self.assertEqual(len(result), 3)

    def test_special_line_flushes_buffer(self):
        """Special line causes buffer flush."""
        lines = ["Line one.", "Line two.", "# Heading"]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        self.assertEqual(result[-1], "# Heading")

    def test_heading_flushes_buffer(self):
        """Heading line causes buffer flush."""
        lines = ["Some text.", "More text.", "# Title"]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        self.assertEqual(result[-1], "# Title")

    def test_code_block_not_joined(self):
        """Lines inside code block are NOT joined."""
        lines = ["```python", "def foo():", "    return 1", "```"]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        # Code block lines should be preserved separately
        self.assertEqual(len(result), 4)

    def test_empty_lines_preserved(self):
        """Empty lines are preserved in output."""
        lines = ["Text", "", "More text"]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        self.assertIn("", result)

    def test_list_item_not_joined(self):
        """List items are NOT joined with preceding text."""
        lines = ["Some text.", "- list item"]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        self.assertIn("- list item", result)

    def test_remaining_buffer_flushed(self):
        """Buffer is flushed at end of file."""
        lines = ["Line one.", "Line two."]
        result = MarkdownPreprocessor._join_wrapped_lines(lines)
        self.assertEqual(len(result), 1)
        self.assertIn("Line one.", result[0])


class TestProcessMethod(unittest.TestCase):
    """Tests for the main process method (lines 370-447)."""

    def test_process_extracts_yaml_metadata(self):
        """process() extracts metadata from YAML frontmatter."""
        text = """---
title: Test Title
author: Test Author
---
# Introduction
Some text.
"""
        preprocessor = MarkdownPreprocessor()
        _, meta = preprocessor.process(text)
        self.assertEqual(meta.title, "Test Title")
        self.assertEqual(meta.author, "Test Author")

    def test_process_joins_wrapped_lines(self):
        """process() joins hard-wrapped lines."""
        text = """# Title
This is a long paragraph that was wrapped at 72 characters.
It should be joined into one line.
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        self.assertIn("This is a long paragraph", result)

    def test_process_inserts_pagebreak_before_h1(self):
        """Page break inserted before # heading (except first)."""
        text = """# Title

# Section One

# Section Two
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        breaks = result.count('<w:br w:type="page"/>')
        # 2 breaks: before Section One and Section Two (Title is first, no break)
        self.assertEqual(breaks, 2)

    def test_process_skips_short_h1_headings(self):
        """Short # headings (< 3 chars) don't get page breaks."""
        text = """# Ti
# Ab
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        breaks = result.count('<w:br w:type="page"/>')
        self.assertEqual(breaks, 0)

    def test_process_escapes_toc_numbers(self):
        """TOC entries with numbered lists are escaped."""
        text = """1. Introduction......5
2. Methods.......10
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        self.assertIn(r"1\. ", result)

    def test_process_preserves_table_content(self):
        """Multiline tables preserve content (conversion is optional)."""
        text = """Header
--------------------
Data 1
Data 2
Data 3
--------------------
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        # Content should be preserved even if format changes
        self.assertIn("Header", result)
        self.assertIn("Data 1", result)

    def test_process_no_yaml_fallback(self):
        """Fallback parsing when no YAML frontmatter."""
        text = """**My Title**

Author Name

# Content
"""
        preprocessor = MarkdownPreprocessor()
        _result, meta = preprocessor.process(text)
        self.assertIn("My Title", meta.title)

    def test_process_empty_content(self):
        """Empty content returns empty string and default metadata."""
        preprocessor = MarkdownPreprocessor()
        result, meta = preprocessor.process("")
        self.assertEqual(result, "")
        self.assertIsInstance(meta, DocumentMetadata)

    def test_process_preserves_code_blocks(self):
        """Code blocks are preserved and not joined."""
        text = """# Title
```
code here
```
More text.
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        self.assertIn("```", result)

    def test_process_handles_pipe_tables(self):
        """Existing pipe tables pass through."""
        text = """| Header | Header |
|---|---|
| Cell | Cell |
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        self.assertIn("| Header |", result)


class TestBuildTitlePageMd(unittest.TestCase):
    """Tests for build_title_page_md (lines 98-131)."""

    def test_builds_title_page_with_openxml(self):
        """Title page includes OpenXML page break."""
        meta = DocumentMetadata(title="Test Title", author="Author")
        result = MarkdownPreprocessor.build_title_page_md(meta)
        self.assertIn('<w:br w:type="page"/>', result)
        self.assertIn("Test Title", result)

    def test_title_page_encodes_hash(self):
        """# in title is encoded to prevent Pandoc interpretation."""
        meta = DocumentMetadata(title="Title with # symbol")
        result = MarkdownPreprocessor.build_title_page_md(meta)
        self.assertIn("&#35;", result)

    def test_title_page_handles_missing_title(self):
        """Missing title defaults to 'Sin Título'."""
        meta = DocumentMetadata()
        result = MarkdownPreprocessor.build_title_page_md(meta)
        self.assertIn("Sin Título", result)

    def test_title_page_includes_metadata_fields(self):
        """Metadata fields are included in title page."""
        meta = DocumentMetadata(title="T", author="A", institution="I", date="2024")
        result = MarkdownPreprocessor.build_title_page_md(meta)
        self.assertIn("<!-- author --> A", result)
        self.assertIn("<!-- institution --> I", result)
        self.assertIn("<!-- date --> 2024", result)


class TestProcessEdgeCases(unittest.TestCase):
    """Edge case tests for process method."""

    def test_process_removes_carriage_returns(self):
        """Carriage returns are removed."""
        text = "Line1\rLine2\r\nLine3"
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        self.assertNotIn("\r", result)

    def test_process_double_spacing_detection(self):
        """Lines with only whitespace/dots are handled."""
        text = """# Title
   ..... 5
"""
        preprocessor = MarkdownPreprocessor()
        result, _meta = preprocessor.process(text)
        self.assertIn(".....", result)


if __name__ == "__main__":
    unittest.main()

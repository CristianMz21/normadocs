"""
Module for preprocessing Markdown content before Pandoc conversion.
"""

import re

import yaml

from .config import METADATA_FIELDS, PAGEBREAK_OPENXML
from .models import DocumentMetadata


class MarkdownPreprocessor:
    """Handles the preparation of Markdown content for APA conversion."""

    @staticmethod
    def extract_yaml_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
        """
        Extract YAML frontmatter if present.
        Returns (metadata_dict, end_line_index) where end_line_index is the line
        containing the closing '---' (or -1 if no YAML frontmatter).
        """
        if not lines or lines[0].strip() != "---":
            return {}, -1

        # Find the closing ---
        end_line = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_line = i
                break

        if end_line == -1:
            return {}, -1

        # Parse YAML content (lines between the --- delimiters)
        yaml_content = "\n".join(lines[1:end_line])
        try:
            metadata = yaml.safe_load(yaml_content) or {}
            if not isinstance(metadata, dict):
                metadata = {}
        except yaml.YAMLError:
            metadata = {}

        return metadata, end_line

    @staticmethod
    def extract_metadata(lines: list[str]) -> DocumentMetadata:
        """Extract title, author, etc. from YAML frontmatter or fallback parsing."""
        data: dict[str, str] = {}

        # Try to extract YAML frontmatter first
        yaml_data, _yaml_end = MarkdownPreprocessor.extract_yaml_frontmatter(lines)

        if yaml_data:
            # Use YAML frontmatter data directly
            for key in [
                "title",
                "subtitle",
                "author",
                "affiliation",
                "program",
                "ficha",
                "institution",
                "center",
                "instructor",
                "date",
                "short_title",
            ]:
                if yaml_data.get(key):
                    data[key] = str(yaml_data[key])

            return DocumentMetadata.from_dict(data)

        # Fallback: legacy parsing for documents without YAML frontmatter
        # Lines 0-1: Title
        title_parts = []
        for i in range(2):
            if i < len(lines):
                title_parts.append(lines[i].strip().replace("\r", "").replace("**", ""))

        data["title"] = " ".join(filter(None, title_parts)).strip()

        # Remaining metadata
        idx = 0
        # Check lines 2-15 for other metadata, skipping empty lines and stopping at ---
        for i in range(2, 16):
            if i < len(lines):
                val = lines[i].strip().replace("\r", "")
                # Stop at --- or # heading (start of content)
                if val in ("---", "--") or val.startswith("#"):
                    break
                if val and idx < len(METADATA_FIELDS):
                    data[METADATA_FIELDS[idx]] = val
                    idx += 1

        return DocumentMetadata.from_dict(data)

    @staticmethod
    def build_title_page_md(meta: DocumentMetadata) -> str:
        """Build a Markdown title page that Pandoc will render.

        Uses raw OpenXML to ensure Pandoc doesn't interpret this as title metadata.
        """
        parts: list[str] = []

        # Use raw OpenXML for the title page to prevent Pandoc from interpreting content
        # as title metadata. We use a centered div but avoid using Pandoc's title features.
        parts.append('<div style="text-align:center">\n')

        # Title - use HTML entity encoding to prevent Pandoc extraction
        title = meta.title or "Sin Título"
        # Replace # with HTML entity to prevent Pandoc from treating as heading
        title_encoded = title.replace("#", "&#35;")
        parts.append(f"**{title_encoded}**\n")
        parts.append("")  # Blank line between title and author (APA)
        parts.append("&nbsp;\n")  # Extra visual spacing
        parts.append("")

        # Metadata fields - each wrapped to prevent interpretation
        fields = ["author", "program", "ficha", "institution", "center", "instructor", "date"]
        for field in fields:
            val = getattr(meta, field, None)
            if val:
                # Wrap in HTML comment-like structure to prevent extraction
                parts.append(f"<!-- {field} --> {val}\n")

        parts.append("\n</div>\n\n")

        # Page break after title page
        parts.append(PAGEBREAK_OPENXML)

        return "\n".join(parts)

    @staticmethod
    def _is_special_line(stripped: str) -> bool:
        """Return True if this line is a Markdown structural element that must NOT be joined."""
        if not stripped:
            return True  # blank line = paragraph separator
        if stripped.startswith(("#", "```", "---", "===", ">", "![", "![")):
            return True
        if stripped.startswith(("-", "*", "+")) and len(stripped) > 1 and stripped[1] == " ":
            return True  # unordered list
        if re.match(r"^\d+\.\s", stripped):
            return True  # ordered list
        # Grid table borders: +---+---+
        if re.match(r"^\+[-=+]+\+$", stripped):
            return True
        # Pipe table rows: | ... |
        if stripped.startswith("|") and stripped.endswith("|"):
            return True
        # Pandoc grid table text rows that start with |
        if stripped.startswith("|"):
            return True
        # Raw OpenXML / HTML blocks
        if stripped.startswith(("<", "```{")):
            return True
        # ASCII art / box-drawing characters at start of line
        if re.match(r"^[┌┐└┘├┤┬┴┼─│]+", stripped):
            return True
        # TOC-like entry: text followed by dots and a page number
        return bool(re.match(r"^.*\.{3,}\s*\d+\s*$", stripped))

    @staticmethod
    def _convert_multiline_tables(lines: list[str]) -> list[str]:
        """
        Convert Pandoc multiline tables (dashed-line format) to pipe tables.
        Detects outer separators (single continuous dashes) and inner separators
        (dash groups separated by spaces).
        """
        # Pattern for a long continuous dash line (outer separator)
        outer_re = re.compile(r"^\s*-{20,}\s*$")
        # Pattern for inner separator with column groups
        inner_re = re.compile(r"^\s*-{3,}(\s+-{3,})+\s*$")

        result: list[str] = []
        i = 0
        while i < len(lines):
            stripped = lines[i].strip().replace("\r", "")

            # Determine if this is a table start (outer or inner)
            started_with_outer = outer_re.match(stripped)
            started_with_inner = inner_re.match(stripped) if not started_with_outer else False

            if started_with_outer or started_with_inner:
                # Found potential start of a multiline table
                table_lines = [lines[i]]
                i += 1

                # Collect all lines until the matching end separator (SAME type)
                end_found = False
                while i < len(lines):
                    s = lines[i].strip().replace("\r", "")
                    table_lines.append(lines[i])
                    # End must match the SAME separator type as start
                    is_end = (
                        (started_with_outer and outer_re.match(s))
                        or (started_with_inner and inner_re.match(s))
                    ) and len(table_lines) > 2
                    if is_end:
                        end_found = True
                        i += 1
                        break
                    i += 1

                if not end_found or len(table_lines) < 4:
                    result.extend(table_lines)
                    continue

                # Find the inner separator to determine column boundaries
                inner_sep_line = None
                for tl in table_lines[1:-1]:
                    ts = tl.strip()
                    if inner_re.match(ts):
                        inner_sep_line = tl
                        break

                if inner_sep_line is None:
                    result.extend(table_lines)
                    continue

                # Parse columns from the inner separator
                pipe_lines = MarkdownPreprocessor._parse_multiline_table(
                    table_lines, inner_sep_line
                )
                result.extend(pipe_lines)
            else:
                result.append(lines[i])
                i += 1

        return result

    @staticmethod
    def _parse_multiline_table(table_lines: list[str], inner_sep_line: str) -> list[str]:
        """
        Given the raw lines of a multiline table (including outer separators),
        parse column boundaries from the inner separator and produce a pipe table.
        """
        # Parse column boundaries from the inner separator (has dash groups)
        col_boundaries = []
        in_dash = False
        start = 0
        for j, ch in enumerate(inner_sep_line):
            if ch == "-":
                if not in_dash:
                    start = j
                    in_dash = True
            else:
                if in_dash:
                    col_boundaries.append((start, j))
                    in_dash = False
        if in_dash:
            col_boundaries.append((start, len(inner_sep_line)))

        if not col_boundaries:
            return table_lines  # fallback

        # Find the header separator index within table_lines
        header_sep_idx = -1
        inner_stripped = inner_sep_line.strip()
        for k in range(1, len(table_lines) - 1):
            s = table_lines[k].strip()
            if s == inner_stripped:
                header_sep_idx = k
                break

        if header_sep_idx < 0:
            return table_lines  # fallback

        # Extract header rows (between top sep and header sep)
        header_rows = table_lines[1:header_sep_idx]
        # Extract data rows (between header sep and bottom sep)
        data_rows = table_lines[header_sep_idx + 1 : -1]

        def extract_cells(raw_lines: list[str]) -> list[list[str]]:
            """Group raw_lines by blank-line-separated records, extract cells."""
            records: list[list[str]] = []
            current_record: list[str] = []

            for ln in raw_lines:
                s = ln.strip()
                if not s:
                    if current_record:
                        records.append(current_record)
                        current_record = []
                else:
                    current_record.append(ln)
            if current_record:
                records.append(current_record)

            result_cells: list[list[str]] = []
            for record in records:
                cells = []
                for col_start, col_end in col_boundaries:
                    col_parts = []
                    for rl in record:
                        # Pad line to ensure we can slice
                        padded = rl.ljust(col_end)
                        part = padded[col_start:col_end].strip()
                        if part:
                            col_parts.append(part)
                    cells.append(" ".join(col_parts))
                result_cells.append(cells)

            return result_cells

        header_cells = extract_cells(header_rows)
        data_cells = extract_cells(data_rows)

        # Build pipe table
        result: list[str] = []

        # Header row (merge multi-row headers)
        if header_cells:
            merged_header = []
            for col_idx in range(len(col_boundaries)):
                parts = []
                for row_cells in header_cells:
                    if col_idx < len(row_cells) and row_cells[col_idx]:
                        parts.append(row_cells[col_idx])
                merged_header.append(" ".join(parts))
            # Strip ** bold markers
            merged_header = [h.replace("**", "") for h in merged_header]
            result.append("| " + " | ".join(merged_header) + " |")
            result.append("| " + " | ".join("---" for _ in merged_header) + " |")

        # Data rows
        for row_cells in data_cells:
            # Clean cells
            cleaned = []
            for c in row_cells:
                c = c.replace("**", "").replace("*", "")
                cleaned.append(c)
            result.append("| " + " | ".join(cleaned) + " |")

        return result

    @staticmethod
    def _join_wrapped_lines(lines: list[str]) -> list[str]:
        """
        Join consecutive non-special lines into single paragraphs.
        This fixes the 'hard return' problem where text is wrapped at ~72 chars.
        """
        result: list[str] = []
        buffer: list[str] = []
        in_code_block = False

        for line in lines:
            stripped = line.strip().replace("\r", "")

            # Track code block boundaries
            if stripped.startswith("```"):
                in_code_block = not in_code_block

            # Inside code block: treat every line as special (don't join)
            if in_code_block or MarkdownPreprocessor._is_special_line(stripped):
                # Flush any buffered continuation text
                if buffer:
                    result.append(" ".join(buffer))
                    buffer = []
                result.append(line)
            else:
                # This is a continuation line — accumulate it
                buffer.append(stripped)

        # Flush remaining
        if buffer:
            result.append(" ".join(buffer))

        return result

    def process(self, text: str) -> tuple[str, DocumentMetadata]:
        """
        Pre-process the Markdown:
          1. Extract metadata from YAML frontmatter
          2. Skip YAML frontmatter in content
          3. Join hard-wrapped lines into proper paragraphs
          4. Insert page breaks before every # heading (level 1)
          5. Skip ## and ### headings (they stay in the same page)
        """
        lines = text.split("\n")
        meta = self.extract_metadata(lines)

        # Find where content starts
        yaml_data, yaml_end = self.extract_yaml_frontmatter(lines)

        if yaml_data:
            # YAML frontmatter detected - skip the entire YAML block (including closing ---)
            # Content starts after the closing ---
            content_start = yaml_end + 1
            # Skip any empty lines after YAML block
            while content_start < len(lines) and not lines[content_start].strip():
                content_start += 1
        else:
            # No YAML frontmatter - check for legacy metadata block (--- at line 0)
            metadata_end = 0
            for i, line in enumerate(lines):
                stripped = line.strip().replace("\r", "")
                if stripped in ("---", "--"):
                    metadata_end = i
                    break

            # Then find first # heading after metadata
            content_start = metadata_end
            for i in range(metadata_end, len(lines)):
                stripped = lines[i].strip().replace("\r", "")
                if stripped.startswith("# "):
                    content_start = i
                    break

            # Fallback: if no --- found but there's a # heading, use it
            if metadata_end == 0 and content_start == 0 and len(lines) > 60:
                content_start = 60  # fallback legacy behavior

        # Extract only content lines (skip YAML/metadata header)
        # Start from first # heading and include everything after
        content_lines = lines[content_start:] if content_start > 0 else lines

        # Convert multiline dashed tables to pipe tables
        content_lines = self._convert_multiline_tables(content_lines)

        # Join hard-wrapped lines into proper paragraphs
        joined_lines = self._join_wrapped_lines(content_lines)

        # Don't build title page here - let the APA formatter handle it
        # This prevents Pandoc from creating duplicate title pages

        # Build the new markdown
        output_parts: list[str] = []
        found_first_heading = False  # First # heading after title page doesn't need page break

        for line in joined_lines:
            stripped = line.strip().replace("\r", "")

            # Check for level 1 heading
            if re.match(r"^#\s+", stripped) and not re.match(r"^##", stripped):
                heading_text = stripped[2:].strip()
                if len(heading_text) > 2:
                    if found_first_heading:
                        output_parts.append(PAGEBREAK_OPENXML)
                    found_first_heading = True

            # Escape TOC numbered lines to prevent Pandoc from converting them to ordered lists
            if re.match(r"^\s*\d+\.\s+.*\.{3,}\s*\d+\s*$", stripped):
                line = re.sub(r"^(\s*\d+)\.\s+", r"\1\\. ", line)

            output_parts.append(line)

        return "\n".join(output_parts), meta

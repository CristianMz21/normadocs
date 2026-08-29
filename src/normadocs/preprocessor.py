"""
Module for preprocessing Markdown content before Pandoc conversion.
"""

import re

import yaml

from .config import METADATA_FIELDS, PAGEBREAK_OPENXML
from .models import DocumentMetadata

_OUTER_RE = re.compile(r"^\s*-{20,}\s*$")
_INNER_RE = re.compile(r"^\s*-{3,}(\s+-{3,})+\s*$")
_TOC_SUFFIX_RE = re.compile(r"\.{3,}\s*\d+\s*$")
_NUMBERED_TOC_PREFIX_RE = re.compile(r"^\s*\d+\.\s+")
_GRID_TABLE_RE = re.compile(r"^\+[-=+]+\+$")
_ORDERED_LIST_RE = re.compile(r"^\d+\.\s")
_BOX_DRAWING_RE = re.compile(r"^[┌┐└┘├┤┬┴┼─│]+")
_FENCE_RE = re.compile(r"^```\s*\{?math\}?\s*$")
_HEADING_PREFIX = "#"


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

        end_line = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_line = i
                break

        if end_line == -1:
            return {}, -1

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

        yaml_data, _yaml_end = MarkdownPreprocessor.extract_yaml_frontmatter(lines)

        if yaml_data:
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
                "subject",
                "location",
                "date",
                "short_title",
            ]:
                if yaml_data.get(key):
                    data[key] = str(yaml_data[key])

            return DocumentMetadata.from_dict(data)

        title_parts = []
        for i in range(2):
            if i < len(lines):
                title_parts.append(lines[i].strip().replace("\r", "").replace("**", ""))

        data["title"] = " ".join(filter(None, title_parts)).strip()

        idx = 0
        for i in range(2, 16):
            if i >= len(lines):
                break
            val = lines[i].strip().replace("\r", "")
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

        parts.append('<div style="text-align:center">\n')

        title = meta.title or "Sin Título"
        title_encoded = title.replace("#", "&#35;")
        parts.append(f"**{title_encoded}**\n")
        parts.append("")
        parts.append("&nbsp;\n")
        parts.append("")

        fields = ["author", "program", "ficha", "institution", "center", "instructor", "date"]
        for field in fields:
            val = getattr(meta, field, None)
            if val:
                parts.append(f"<!-- {field} --> {val}\n")

        parts.append("\n</div>\n\n")

        parts.append(PAGEBREAK_OPENXML)

        return "\n".join(parts)

    @staticmethod
    def _is_toc_like_line(stripped: str) -> bool:
        """Linear two-pass TOC check (S5852)."""
        if "..." not in stripped:
            return False
        return bool(_TOC_SUFFIX_RE.search(stripped))

    @staticmethod
    def _is_numbered_toc_line(stripped: str) -> bool:
        """Check numbered TOC line with linear regexes."""
        if not _NUMBERED_TOC_PREFIX_RE.match(stripped):
            return False
        if "..." not in stripped:
            return False
        return bool(_TOC_SUFFIX_RE.search(stripped))

    @staticmethod
    def _is_special_line(stripped: str) -> bool:
        """Return True if this line is a Markdown structural element that must NOT be joined."""
        if not stripped:
            return True
        if stripped.startswith(("#", "```", "---", "===", ">", "![", "![")):
            return True
        if stripped.startswith(("-", "*", "+")) and len(stripped) > 1 and stripped[1] == " ":
            return True
        if _ORDERED_LIST_RE.match(stripped):
            return True
        if _GRID_TABLE_RE.match(stripped):
            return True
        if stripped.startswith("|") and stripped.endswith("|"):
            return True
        if stripped.startswith("|"):
            return True
        if stripped.startswith(("<", "```{")):
            return True
        if _BOX_DRAWING_RE.match(stripped):
            return True
        return MarkdownPreprocessor._is_toc_like_line(stripped)

    @staticmethod
    def _is_outer_separator(line: str) -> bool:
        return bool(_OUTER_RE.match(line.strip().replace("\r", "")))

    @staticmethod
    def _is_inner_separator(line: str) -> bool:
        return bool(_INNER_RE.match(line.strip().replace("\r", "")))

    @staticmethod
    def _detect_table_start(stripped: str) -> tuple[bool, bool]:
        """Return (is_outer, is_inner) for table start detection."""
        is_outer = bool(_OUTER_RE.match(stripped))
        is_inner = False
        if not is_outer:
            is_inner = bool(_INNER_RE.match(stripped))
        return is_outer, is_inner

    @staticmethod
    def _collect_table_block(
        lines: list[str], start_idx: int, is_outer: bool, is_inner: bool
    ) -> tuple[list[str], bool, int]:
        """Collect lines until matching end separator (same type)."""
        table_lines = [lines[start_idx]]
        i = start_idx + 1
        end_found = False
        while i < len(lines):
            s = lines[i].strip().replace("\r", "")
            table_lines.append(lines[i])
            is_end = (
                (is_outer and bool(_OUTER_RE.match(s))) or (is_inner and bool(_INNER_RE.match(s)))
            ) and len(table_lines) > 2
            if is_end:
                end_found = True
                i += 1
                break
            i += 1
        return table_lines, end_found, i

    @staticmethod
    def _find_inner_separator(table_lines: list[str]) -> str | None:
        """Find inner separator line inside table block."""
        for tl in table_lines[1:-1]:
            ts = tl.strip()
            if _INNER_RE.match(ts):
                return tl
        return None

    @staticmethod
    def _convert_multiline_tables(lines: list[str]) -> list[str]:
        """
        Convert Pandoc multiline tables (dashed-line format) to pipe tables.
        Detects outer separators (single continuous dashes) and inner separators
        (dash groups separated by spaces).
        """
        result: list[str] = []
        i = 0
        while i < len(lines):
            stripped = lines[i].strip().replace("\r", "")
            is_outer, is_inner = MarkdownPreprocessor._detect_table_start(stripped)

            if is_outer or is_inner:
                table_lines, end_found, next_i = MarkdownPreprocessor._collect_table_block(
                    lines, i, is_outer, is_inner
                )

                if not end_found or len(table_lines) < 4:
                    result.extend(table_lines)
                    i = next_i
                    continue

                inner_sep_line = MarkdownPreprocessor._find_inner_separator(table_lines)

                if inner_sep_line is None:
                    result.extend(table_lines)
                    i = next_i
                    continue

                pipe_lines = MarkdownPreprocessor._parse_multiline_table(
                    table_lines, inner_sep_line
                )
                result.extend(pipe_lines)
                i = next_i
            else:
                result.append(lines[i])
                i += 1

        return result

    @staticmethod
    def _parse_col_boundaries(inner_sep_line: str) -> list[tuple[int, int]]:
        """Parse column boundaries from inner separator dash groups."""
        col_boundaries: list[tuple[int, int]] = []
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
        return col_boundaries

    @staticmethod
    def _find_header_sep_index(table_lines: list[str], inner_stripped: str) -> int:
        """Find header separator index within table lines."""
        for k in range(1, len(table_lines) - 1):
            s = table_lines[k].strip()
            if s == inner_stripped:
                return k
        return -1

    @staticmethod
    def _extract_cells(
        raw_lines: list[str], col_boundaries: list[tuple[int, int]]
    ) -> list[list[str]]:
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
            cells: list[str] = []
            for col_start, col_end in col_boundaries:
                col_parts: list[str] = []
                for rl in record:
                    padded = rl.ljust(col_end)
                    part = padded[col_start:col_end].strip()
                    if part:
                        col_parts.append(part)
                cells.append(" ".join(col_parts))
            result_cells.append(cells)

        return result_cells

    @staticmethod
    def _build_pipe_table(
        header_cells: list[list[str]],
        data_cells: list[list[str]],
        col_boundaries: list[tuple[int, int]],
    ) -> list[str]:
        """Build pipe table from header and data cells."""
        result: list[str] = []

        if header_cells:
            merged_header: list[str] = []
            for col_idx in range(len(col_boundaries)):
                parts: list[str] = []
                for row_cells in header_cells:
                    if col_idx < len(row_cells) and row_cells[col_idx]:
                        parts.append(row_cells[col_idx])
                merged_header.append(" ".join(parts))
            merged_header = [h.replace("**", "") for h in merged_header]
            result.append("| " + " | ".join(merged_header) + " |")
            result.append("| " + " | ".join("---" for _ in merged_header) + " |")

        for row_cells in data_cells:
            cleaned: list[str] = []
            for c in row_cells:
                c = c.replace("**", "").replace("*", "")
                cleaned.append(c)
            result.append("| " + " | ".join(cleaned) + " |")

        return result

    @staticmethod
    def _parse_multiline_table(table_lines: list[str], inner_sep_line: str) -> list[str]:
        """
        Given the raw lines of a multiline table (including outer separators),
        parse column boundaries from the inner separator and produce a pipe table.
        """
        col_boundaries = MarkdownPreprocessor._parse_col_boundaries(inner_sep_line)

        if not col_boundaries:
            return table_lines

        header_sep_idx = MarkdownPreprocessor._find_header_sep_index(
            table_lines, inner_sep_line.strip()
        )

        if header_sep_idx < 0:
            return table_lines

        header_rows = table_lines[1:header_sep_idx]
        data_rows = table_lines[header_sep_idx + 1 : -1]

        header_cells = MarkdownPreprocessor._extract_cells(header_rows, col_boundaries)
        data_cells = MarkdownPreprocessor._extract_cells(data_rows, col_boundaries)

        return MarkdownPreprocessor._build_pipe_table(header_cells, data_cells, col_boundaries)

    @staticmethod
    def _has_hard_line_break(line: str) -> bool:
        """Return whether a source line ends with an intentional Markdown hard break."""
        raw = line.rstrip("\r")
        if raw.endswith("  "):
            return True
        trailing_backslashes = len(raw) - len(raw.rstrip("\\"))
        return trailing_backslashes % 2 == 1

    @staticmethod
    def _convert_math_fences(lines: list[str]) -> list[str]:
        """Convert GitHub-style ```math fenced blocks to Pandoc $$ display math."""
        result: list[str] = []
        in_math_fence = False

        for line in lines:
            stripped = line.strip().replace("\r", "")
            if not in_math_fence and _FENCE_RE.match(stripped):
                in_math_fence = True
                result.append("$$")
                continue
            if in_math_fence and stripped.startswith("```"):
                in_math_fence = False
                result.append("$$")
                continue
            result.append(line)

        return result

    _TAG_RE = re.compile(r"\\tag\{[^}]*\}")

    @staticmethod
    def _is_math_delim(stripped: str) -> bool:
        return stripped == "$$"

    @staticmethod
    def _is_single_line_math(stripped: str) -> bool:
        return stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4

    @staticmethod
    def _is_code_fence(stripped: str) -> bool:
        return stripped.startswith("```")

    @staticmethod
    def _flush_buffer(buffer: list[str], result: list[str]) -> None:
        if buffer:
            result.append(" ".join(buffer))
            buffer.clear()

    @staticmethod
    def _normalize_hard_break(line: str) -> str:
        normalized = line.rstrip("\r").rstrip(" \t")
        if not normalized.endswith("\\"):
            normalized += "\\"
        return normalized

    @staticmethod
    def _handle_math_content(
        line: str,
        stripped: str,
        is_delim: bool,
        in_math_block: bool,
        single_line_math: bool,
        opens_math: bool,
        buffer: list[str],
        result: list[str],
    ) -> bool:
        """Handle math block lines; return True if handled."""
        if is_delim or in_math_block or single_line_math:
            if (opens_math or single_line_math) and buffer:
                MarkdownPreprocessor._flush_buffer(buffer, result)
            result.append(MarkdownPreprocessor._TAG_RE.sub("", line))
            return True
        return False

    @staticmethod
    def _handle_special_content(
        line: str, stripped: str, in_code_block: bool, buffer: list[str], result: list[str]
    ) -> bool:
        """Handle special/code lines; return True if handled."""
        if in_code_block or MarkdownPreprocessor._is_special_line(stripped):
            MarkdownPreprocessor._flush_buffer(buffer, result)
            result.append(line)
            return True
        return False

    @staticmethod
    def _handle_hard_break_content(line: str, buffer: list[str], result: list[str]) -> bool:
        """Handle hard break lines; return True if handled."""
        if MarkdownPreprocessor._has_hard_line_break(line):
            MarkdownPreprocessor._flush_buffer(buffer, result)
            result.append(MarkdownPreprocessor._normalize_hard_break(line))
            return True
        return False

    @staticmethod
    def _join_wrapped_lines(lines: list[str]) -> list[str]:
        """
        Join consecutive non-special lines into single paragraphs.

        This fixes the 'hard return' problem where text is wrapped at ~72 chars,
        while preserving intentional structure.
        """
        result: list[str] = []
        buffer: list[str] = []
        in_code_block = False
        in_math_block = False

        for line in lines:
            stripped = line.strip().replace("\r", "")
            is_delim = MarkdownPreprocessor._is_math_delim(stripped)
            single_line_math = MarkdownPreprocessor._is_single_line_math(stripped)
            opens_math = is_delim and not in_math_block

            if MarkdownPreprocessor._is_code_fence(stripped):
                in_code_block = not in_code_block
            elif is_delim:
                in_math_block = not in_math_block
            elif not in_math_block and stripped.startswith("$$"):
                in_math_block = True

            if MarkdownPreprocessor._handle_math_content(
                line,
                stripped,
                is_delim,
                in_math_block,
                single_line_math,
                opens_math,
                buffer,
                result,
            ):
                continue

            if MarkdownPreprocessor._handle_special_content(
                line, stripped, in_code_block, buffer, result
            ):
                continue

            if MarkdownPreprocessor._handle_hard_break_content(line, buffer, result):
                continue

            buffer.append(stripped)

        MarkdownPreprocessor._flush_buffer(buffer, result)
        return result

    @staticmethod
    def _determine_content_start(lines: list[str], yaml_data: dict[str, str], yaml_end: int) -> int:
        """Determine where content starts after frontmatter/metadata."""
        if yaml_data:
            content_start = yaml_end + 1
            while content_start < len(lines) and not lines[content_start].strip():
                content_start += 1
            return content_start

        metadata_end = 0
        for i, line in enumerate(lines):
            stripped = line.strip().replace("\r", "")
            if stripped in ("---", "--"):
                metadata_end = i
                break

        content_start = metadata_end
        for i in range(metadata_end, len(lines)):
            stripped = lines[i].strip().replace("\r", "")
            if stripped.startswith("# "):
                content_start = i
                break

        if metadata_end == 0 and content_start == 0 and len(lines) > 60:
            content_start = 60

        return content_start

    @staticmethod
    def _is_heading_level_1(stripped: str) -> bool:
        """Check if line is a level-1 heading with enough text."""
        if not stripped.startswith(_HEADING_PREFIX):
            return False
        if stripped.startswith("##"):
            return False
        if not stripped.startswith("# "):
            return False
        heading_text = stripped[2:].strip()
        return len(heading_text) > 2

    @staticmethod
    def _build_output_parts(joined_lines: list[str]) -> list[str]:
        """Add page breaks before H1 and escape numbered TOC lines."""
        output_parts: list[str] = []
        found_first_heading = False

        for line in joined_lines:
            stripped = line.strip().replace("\r", "")

            if stripped in ("\\newpage", "\\pagebreak"):
                output_parts.append(PAGEBREAK_OPENXML)
                continue

            if MarkdownPreprocessor._is_heading_level_1(stripped):
                if found_first_heading:
                    output_parts.append(PAGEBREAK_OPENXML)
                found_first_heading = True

            if MarkdownPreprocessor._is_numbered_toc_line(stripped):
                line = re.sub(r"^(\s*\d+)\.\s+", r"\1\\. ", line)

            output_parts.append(line)

        return output_parts

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

        yaml_data, yaml_end = self.extract_yaml_frontmatter(lines)
        content_start = self._determine_content_start(lines, yaml_data, yaml_end)

        content_lines = lines[content_start:] if content_start > 0 else lines

        content_lines = self._convert_multiline_tables(content_lines)

        content_lines = self._convert_math_fences(content_lines)

        joined_lines = self._join_wrapped_lines(content_lines)

        output_parts = self._build_output_parts(joined_lines)

        return "\n".join(output_parts), meta

"""
Module for preprocessing Markdown content before Pandoc conversion.
"""

import re
from typing import List, Dict, Tuple
from .models import DocumentMetadata
from .config import PAGEBREAK_OPENXML, METADATA_FIELDS


class MarkdownPreprocessor:
    """Handles the preparation of Markdown content for APA conversion."""

    @staticmethod
    def extract_metadata(lines: List[str]) -> DocumentMetadata:
        """Extract title, author, etc. from the first ~14 lines."""
        data: Dict[str, str] = {}

        # Lines 0-1: Title
        title_parts = []
        for i in range(2):
            if i < len(lines):
                title_parts.append(lines[i].strip().replace("\r", "").replace("**", ""))

        data["title"] = " ".join(filter(None, title_parts)).strip()

        # Remaining metadata
        idx = 0
        # Check lines 3-13 for other metadata
        for i in range(3, 14):
            if i < len(lines):
                val = lines[i].strip().replace("\r", "")
                if val:
                    if idx < len(METADATA_FIELDS):
                        data[METADATA_FIELDS[idx]] = val
                        idx += 1

        return DocumentMetadata.from_dict(data)

    @staticmethod
    def build_title_page_md(meta: DocumentMetadata) -> str:
        """Build a Markdown title page that Pandoc will render."""
        parts: List[str] = []

        # Empty lines for vertical centering (~6 empty lines to push down)
        parts.append("&nbsp;\n" * 6)
        parts.append("")

        # Title (centered bold)
        title = meta.title or "Sin Título"
        parts.append('<div style="text-align:center">\n')
        parts.append(f"**{title}**\n")
        parts.append("")  # Blank line between title and author (APA)
        parts.append("&nbsp;\n")  # Extra visual spacing
        parts.append("")

        # Metadata fields
        # Note: Order matches the extraction order logic for simplicity in reconstruction
        # but ideally we use the specific fields from the dataclass
        fields = ["author", "program", "ficha", "institution", "center", "date"]
        for field in fields:
            val = getattr(meta, field, None)
            if val:
                parts.append(val + "\n")

        parts.append("</div>\n")

        # Page break after title page
        parts.append(PAGEBREAK_OPENXML)

        return "\n".join(parts)

    def process(self, text: str) -> Tuple[str, DocumentMetadata]:
        """
        Pre-process the Markdown:
          1. Extract metadata
          2. Replace original metadata + title lines with APA title page
          3. Insert page breaks before every # heading (level 1)
          4. Skip ## and ### headings (they stay in the same page)
        """
        lines = text.split("\n")
        meta = self.extract_metadata(lines)

        # Find where content starts (# Resumen or # Contenido or first #)
        content_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip().replace("\r", "")
            if stripped.startswith("# "):
                content_start = i
                break

        if content_start == 0 and len(lines) > 60:
            content_start = 60  # fallback legacy behavior

        # Build the new markdown
        output_parts: List[str] = []

        # 1. Title page
        output_parts.append(self.build_title_page_md(meta))

        # 2. Process content lines
        found_first_heading = False
        # We start looking for content from the detected start
        # If content_start is 0 (e.g. no metadata found), we process everything,
        # but we might be duplicating the title page if we are not careful.
        # The original script assumes metadata is at the top.

        start_index = content_start if content_start > 0 else 0

        for i in range(start_index, len(lines)):
            line = lines[i]
            stripped = line.strip().replace("\r", "")

            # Check for level 1 heading
            if re.match(r"^#\s+", stripped) and not re.match(r"^##", stripped):
                if found_first_heading:
                    # Insert page break BEFORE this heading (except the very first one)
                    output_parts.append(PAGEBREAK_OPENXML)
                found_first_heading = True

            output_parts.append(line)

        return "\n".join(output_parts), meta

"""APA cover page handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING

from ...models import DocumentMetadata

if TYPE_CHECKING:
    from docx.document import Document as DocType


class APACoverHandler:
    """Handles creation of APA 7th Edition cover page."""

    def __init__(self, doc: DocType, config: dict[str, Any] | None = None) -> None:
        """Initialize APACoverHandler.

        Args:
            doc: The python-docx Document object.
            config: Optional configuration dictionary.
        """
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_cover_config(self) -> dict[str, Any]:
        """Get cover configuration from config with defaults."""
        cover_config: dict[str, Any] = {"title_align": "center", "author_align": "center"}
        return cast(dict[str, Any], self.config.get("cover", cover_config))

    def _get_spacing_line(self) -> str:
        """Get line spacing from config with default."""
        spacing_config: dict[str, str] = {"line": "double"}
        return cast(str, self.config.get("spacing", spacing_config).get("line", "double"))

    def add_cover_page(self, meta: DocumentMetadata) -> None:
        """
        Insert a cover page at the beginning of the document.

        APA 7 Cover Page format:
        - Title (bold, centered) in upper half of page
        - Subtitle (centered) below title
        - Author name (centered)
        - Institutional affiliation (centered) - company/department
        - Date (centered)
        """
        self.doc.add_paragraph()
        if self.doc.paragraphs:
            self.doc.paragraphs[0].insert_paragraph_before("")

        content_lines: list[tuple[str, bool]] = [
            (meta.title, True),  # Title: bold, centered
        ]

        # Add subtitle if present
        subtitle = getattr(meta, "subtitle", None) or meta.extra.get("subtitle", "")
        if subtitle:
            content_lines.append(("", False))  # Blank line
            content_lines.append((subtitle, False))  # Subtitle (not bold in APA 7)

        content_lines.append(("", False))  # Blank line
        content_lines.append((meta.author or "", False))  # Author name

        # Add affiliation (combine with center if present)
        center = getattr(meta, "center", None) or ""
        affiliation = getattr(meta, "affiliation", None) or ""
        if center and affiliation:
            affiliation = f"{affiliation}\n{center}"
        elif center:
            affiliation = center
        if affiliation:
            content_lines.append((affiliation, False))

        # Add institution if different from affiliation
        institution = getattr(meta, "institution", None) or ""
        if institution and institution != affiliation:
            content_lines.append((institution, False))

        # Add program and ficha (for SENA format)
        program = getattr(meta, "program", None) or ""
        ficha = getattr(meta, "ficha", None) or ""
        if program:
            content_lines.append(("", False))
            content_lines.append((program, False))
        if ficha:
            content_lines.append((ficha, False))

        # Add date
        date = getattr(meta, "date", None) or ""
        if date:
            content_lines.append(("", False))  # Blank line before date
            content_lines.append((date, False))

        # Add spacers to position title in upper third of page
        n_spacers = 6
        elements: list[tuple[str, bool]] = [("", False)] * n_spacers
        elements.extend(content_lines)

        ref_p = self.doc.paragraphs[0]

        for text, is_bold in elements:
            p = ref_p.insert_paragraph_before(text)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.style = self.doc.styles["Normal"]
            spacing_line = self._get_spacing_line()
            if spacing_line == "double":
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            elif spacing_line == "1.5":
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            else:
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

            if is_bold and text.strip() and p.runs:
                p.runs[0].bold = True

        # Remove leftover reference paragraph
        ref_p._element.getparent().remove(ref_p._element)

        # Remove trailing empty paragraph
        last_p = self.doc.paragraphs[-1]
        if not last_p.text.strip():
            last_p._element.getparent().remove(last_p._element)

        # Add page break after cover page
        for p in self.doc.paragraphs:
            style_name = p.style.name if p.style else ""
            if style_name.startswith("Heading"):
                p.paragraph_format.page_break_before = True
                break
            if p.alignment != WD_ALIGN_PARAGRAPH.CENTER and p.text.strip():
                p.paragraph_format.page_break_before = True
                break

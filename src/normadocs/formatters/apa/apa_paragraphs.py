"""APA paragraph processing, formatting, and cleanup."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, cast

from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_LINE_SPACING,
    WD_TAB_ALIGNMENT,
    WD_TAB_LEADER,
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from ...config import DEFAULT_BODY_FONT
from ...utils.docx_helpers import paragraph_style_name
from .apa_citations import REFERENCE_HEADINGS

if TYPE_CHECKING:
    from docx.document import Document as DocType
    from docx.text.paragraph import Paragraph as ParagraphType

_HEADING_1 = "Heading 1"
_HEADING_5 = "Heading 5"
_RUN_IN_HEADINGS = ("Heading 4", _HEADING_5)


def _is_references_heading(stripped_lower: str) -> bool:
    """Return whether a stripped, lowercased heading title starts the references."""
    return stripped_lower in REFERENCE_HEADINGS or stripped_lower.startswith(
        ("referencias ", "references ", "lista de referencias")
    )


def _clear_paragraph(p: ParagraphType) -> ParagraphType:
    """Clear a paragraph's content while preserving formatting."""
    cast(Any, p._p).clear_content()
    return p


class APAParagraphsHandler:
    """Handles paragraph processing, formatting, and cleanup per APA 7th Edition."""

    def __init__(self, doc: DocType, config: dict[str, Any] | None = None) -> None:
        """Initialize APAParagraphsHandler.

        Args:
            doc: The python-docx Document object.
            config: Optional configuration dictionary.
        """
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_spacing_line(self) -> str:
        """Get line spacing from config with default."""
        spacing: dict[str, str] = {"line": "double"}
        return cast(str, self.config.get("spacing", spacing).get("line", "double"))

    def _get_body_font(self) -> str:
        """Get body font name from config."""
        fonts: dict[str, Any] = {}
        return cast(
            str, self.config.get("fonts", fonts).get("body", {}).get("name", DEFAULT_BODY_FONT)
        )

    @staticmethod
    def _has_page_break_before(paragraph: ParagraphType) -> bool:
        """Return whether the nearest preceding body content is a page break."""
        previous = paragraph._element.getprevious()
        while previous is not None:
            if any(br.get(qn("w:type")) == "page" for br in previous.iter(qn("w:br"))):
                return True
            # Raw OpenXML page breaks can be followed by empty paragraphs.
            # Skip only those empty paragraphs; any real content ends the search.
            if previous.tag == qn("w:p") and not "".join(previous.itertext()).strip():
                previous = previous.getprevious()
                continue
            return False
        return False

    def _set_page_break_before(self, paragraph: ParagraphType) -> None:
        """Add a page break only when one is not already immediately before it.

        The Markdown preprocessor emits explicit OpenXML page breaks before
        level-1 headings. Adding ``page_break_before`` again creates blank
        pages in LibreOffice, so the formatter deduplicates the two paths per
        heading rather than using a document-wide flag.
        """
        if not self._has_page_break_before(paragraph):
            paragraph.paragraph_format.page_break_before = True

    def process(self) -> None:
        """Iterate through paragraphs to apply APA 7 formatting.

        APA 7 requires:
        - RESUMEN (Abstract): Title centered, bold, text without indent
        - Body text paragraphs: First line indent of 0.5 inches
        - First paragraph after any heading: No indent
        - References: Hanging indent (0.5 inches)
        """
        from .apa_styles import APAStylesHandler

        styles_handler = APAStylesHandler(self.doc)

        in_references = False
        in_toc = False
        in_abstract = False
        just_left_abstract = False
        first_paragraph_after_heading = False  # APA 7: first paragraph has no indent
        first_heading_seen = False
        heading_levels = self._build_heading_level_map()

        for p in self.doc.paragraphs:
            style_name = paragraph_style_name(p)
            styles_handler._apply_font_to_paragraph(p)

            text_lower = p.text.lower()

            # Detect sections
            if style_name.startswith("Heading"):
                # Strict detection: only a heading that IS the references
                # section (exact title or starts with it) enables reference
                # mode. A heading merely containing the word "references"
                # (e.g. "Slide 4 — Well-being, teamwork and references")
                # must NOT trigger it.
                heading_stripped = text_lower.strip().rstrip(".")
                is_references_heading = _is_references_heading(heading_stripped)
                if is_references_heading:
                    in_references = True
                    in_toc = False
                    in_abstract = False
                    self._set_page_break_before(p)
                    first_paragraph_after_heading = True
                elif "resumen" in text_lower or "abstract" in text_lower:
                    # APA 7: RESUMEN title is centered and bold
                    in_abstract = True
                    in_toc = False
                    in_references = False
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.bold = True
                    p.paragraph_format.first_line_indent = Inches(0)
                elif "contenido" in text_lower or "index" in text_lower:
                    in_toc = True
                    in_references = False
                    self._set_page_break_before(p)
                else:
                    # APA 7 does not require every Level 1 heading to start a
                    # new page. The cover handler and explicit section breaks
                    # handle pages that must be separated; ordinary headings
                    # should flow with their following content.
                    if style_name == _HEADING_1:
                        # Clear stale page-break formatting inherited from a
                        # previously formatted DOCX, except for the first
                        # content heading used to separate the cover page.
                        if first_heading_seen:
                            p.paragraph_format.page_break_before = False
                        else:
                            first_heading_seen = True
                        first_paragraph_after_heading = True
                    # If leaving abstract section, force page break on any heading
                    if in_abstract or just_left_abstract:
                        self._set_page_break_before(p)
                        just_left_abstract = False
                    # Leaving the references section: reset the flag
                    in_references = False
                    in_abstract = False
                    in_toc = False

                # Explicit APA heading alignment and emphasis on every heading
                if style_name == _HEADING_1:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.bold = True
                elif style_name == "Heading 2":
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.bold = True
                        run.italic = False
                elif style_name == "Heading 3":
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.bold = True
                        run.italic = True
                elif style_name in _RUN_IN_HEADINGS:
                    self._format_run_in_heading(p, italic=(style_name == _HEADING_5))

                # Strip numbering property from headings (APA 7 doesn't use numbered headings)
                p_pr = p._element.find(qn("w:pPr"))
                if p_pr is not None:
                    num_pr = p_pr.find(qn("w:numPr"))
                    if num_pr is not None:
                        p_pr.remove(num_pr)
                # Levels 4-5 keep their 0.5" run-in indent (APA 7)
                if style_name not in _RUN_IN_HEADINGS:
                    p.paragraph_format.first_line_indent = Inches(0)

            # Line spacing
            spacing_line = self._get_spacing_line()
            if spacing_line == "double":
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            elif spacing_line == "1.5":
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            else:
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)

            # APA 7: Widow/orphan control (minimum 2 lines together)
            # and keep paragraph lines together
            self._apply_paragraph_spacing_control(p)

            # APA 7: Keep heading with next paragraph
            if style_name.startswith("Heading"):
                self._apply_keep_with_next(p)

            # Special section handling
            if in_toc and not style_name.startswith("Heading"):
                self._format_toc_entry(p, heading_levels)
                continue

            # Indentation logic
            if (
                not style_name.startswith("Heading")
                and "List" not in style_name
                and "Caption" not in style_name
            ):
                text_strip = p.text.strip()

                # Remove purely numeric paragraphs (Pandoc page numbers injected as text)
                if text_strip.isdigit():
                    p._element.getparent().remove(p._element)
                    continue

                if in_references:
                    if text_strip:
                        p.paragraph_format.left_indent = Inches(0.5)
                        p.paragraph_format.first_line_indent = Inches(-0.5)
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        # Force XML tag to prevent tag dropping
                        p_pr = p._element.get_or_add_pPr()
                        jc = p_pr.get_or_add_jc()
                        jc.set(qn("w:val"), "left")
                elif in_abstract:
                    if p.text.strip():
                        # Abstract block format (no indent per APA 7)
                        p.paragraph_format.first_line_indent = Inches(0)
                    # End abstract after keywords paragraph
                    if text_strip.lower().startswith(("palabras clave", "keywords")):
                        in_abstract = False
                        just_left_abstract = True
                elif (
                    style_name in ("Body Text", "Normal", "First Paragraph", "Compact")
                    and text_strip
                    and p.paragraph_format.alignment != WD_ALIGN_PARAGRAPH.CENTER
                ):
                    # Force page break on first paragraph after abstract/keywords
                    if just_left_abstract:
                        self._set_page_break_before(p)
                        just_left_abstract = False
                    # APA 8.27: quotations of 40+ words become block quotes
                    if self._is_block_quote(text_strip):
                        self._convert_block_quote(p, text_strip)
                    elif first_paragraph_after_heading:
                        p.paragraph_format.first_line_indent = Inches(0)
                        first_paragraph_after_heading = False
                    else:
                        p.paragraph_format.first_line_indent = Inches(0.5)
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    # Force XML tag to prevent tag dropping
                    p_pr = p._element.get_or_add_pPr()
                    jc = p_pr.get_or_add_jc()
                    jc.set(qn("w:val"), "left")

            # Fix citations (y -> &)
            self._fix_citations(p)

    def _apply_paragraph_spacing_control(self, p: ParagraphType) -> None:
        """Apply widow/orphan control per APA 7.

        APA 7 requires widow/orphan control to prevent single lines
        at the top or bottom of a page.
        """
        p_pr = p._element.get_or_add_pPr()
        widow_orphan = OxmlElement("w:widowControl")
        p_pr.append(widow_orphan)
        # Set adjustment for document grid (ensures consistent line height)
        doc_grid = OxmlElement("w:docGrid")
        doc_grid.set(qn("w:type"), "lines")
        doc_grid.set(qn("w:linePitch"), "360")
        p_pr.append(doc_grid)

    def _apply_keep_with_next(self, p: ParagraphType) -> None:
        """Apply keep-with-next to heading paragraphs per APA 7.

        Headings should stay on the same page as the following paragraph.
        """
        p_pr = p._element.get_or_add_pPr()
        keep_next = OxmlElement("w:keepNext")
        p_pr.append(keep_next)

    def _format_run_in_heading(self, p: ParagraphType, italic: bool) -> None:
        """Format a Level 4/5 heading as an APA 7 run-in heading.

        Level 4: indented, bold, ends with a period, text begins on the
        same line. Level 5 adds italics to the heading portion. The first
        body paragraph after the heading is merged onto the heading line so
        the text truly runs in, with explicit non-bold runs so the bold
        heading style does not bleed into the body text.
        """
        from docx.text.paragraph import Paragraph

        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Inches(0.5)
        for run in p.runs:
            run.bold = True
            run.italic = italic

        if not p.text.strip().endswith("."):
            if p.runs:
                p.runs[-1].text = f"{p.runs[-1].text.rstrip()}."
            else:
                p.add_run(".")

        next_el = p._element.getnext()
        if next_el is None or next_el.tag != qn("w:p"):
            return
        if next_el.findall(f".//{qn('w:drawing')}") or next_el.findall(f".//{qn('w:hyperlink')}"):
            return

        next_p = Paragraph(next_el, p._parent)
        next_style = next_p.style.name if next_p.style else ""
        if next_style not in ("Body Text", "Normal", "First Paragraph"):
            return
        if not next_p.text.strip():
            return

        runs = list(next_p.runs)
        if runs:
            runs[0].text = f" {runs[0].text.lstrip()}"
        for run in runs:
            run.bold = False
            if italic and run.italic is None:
                run.italic = False
            p._element.append(run._element)
        next_el.getparent().remove(next_el)

    def _get_block_quote_config(self) -> dict[str, Any]:
        """Get block-quote configuration with APA defaults."""
        default_config: dict[str, Any] = {"min_words": 40, "indent_inches": 0.5}
        return cast(dict[str, Any], self.config.get("block_quote", default_config))

    def _is_block_quote(self, text: str) -> bool:
        """Return whether a quoted paragraph qualifies as an APA block quote.

        APA 8.27: quotations of 40+ words are formatted as a freestanding
        block without quotation marks.
        """
        if not text or text[:1] not in ('"', "\u201c", "\u00ab"):
            return False
        min_words = cast(int, self._get_block_quote_config().get("min_words", 40))
        return len(text.split()) >= min_words

    def _convert_block_quote(self, p: ParagraphType, text: str) -> None:
        """Convert a long quotation into an APA 8.27 block quote.

        Removes the surrounding quotation marks, indents the whole block
        0.5" from the left (no first-line indent), and moves the final
        punctuation before the closing citation parenthesis.
        """
        indent = cast(float, self._get_block_quote_config().get("indent_inches", 0.5))
        p.paragraph_format.left_indent = Inches(indent)
        p.paragraph_format.first_line_indent = Inches(0)

        stripped = text.strip()
        quote_chars = ('"', "\u201c", "\u201d", "\u00ab", "\u00bb")
        if stripped[:1] in quote_chars:
            stripped = stripped[1:].lstrip()

        # Closing quote may sit before the trailing citation, e.g.
        # '…texto," (García, 2020).'
        closing_re = rf"([{re.escape(''.join(quote_chars))}])\s*(\([^()]*\))?\.?\s*$"
        closing = re.search(closing_re, stripped)
        if closing is not None:
            citation = closing.group(2)
            body = stripped[: closing.start()].rstrip()
            if body.endswith((",", ";", ":")):
                body = f"{body[:-1]}."
            if not body.endswith((".", "!", "?")):
                body = f"{body}."
            stripped = f"{body} {citation}" if citation else body

        if stripped and stripped != text.strip():
            self._replace_paragraph_text(p, stripped)

    def _replace_paragraph_text(self, p: ParagraphType, text: str) -> None:
        """Replace paragraph text with a single run, keeping the first run's font."""
        keep_font = None
        keep_size = None
        for run in p.runs:
            if run.text.strip():
                keep_font = run.font.name
                keep_size = run.font.size
                break
        for run in p.runs:
            run._element.getparent().remove(run._element)
        new_run = p.add_run(text)
        if keep_font is not None:
            new_run.font.name = keep_font
        if keep_size is not None:
            new_run.font.size = keep_size

    def _fix_citations(self, p: ParagraphType) -> None:
        """Replace 'y' citations with '&' per APA 7.

        Converts Spanish-style 'y' conjunctions in citations to '&'.

        Args:
            p: The paragraph to process.
        """
        citation_re = re.compile(
            r"\(([A-ZÁ-Ú][a-záéíóúñ]+(?:\s+et\s+al\.)?)\s+y\s+([A-ZÁ-Ú][a-záéíóúñ]+),\s*(\d{4})\)"
        )
        for run in p.runs:
            if " y " in run.text and "(" in run.text:
                run.text = citation_re.sub(r"(\1 & \2, \3)", run.text)

    def _format_toc_entry(self, p: ParagraphType, heading_levels: dict[str, int]) -> None:
        """Format Table of Contents entries with correct indentation."""
        from .apa_styles import APAStylesHandler

        styles_handler = APAStylesHandler(self.doc)

        text = p.text.strip()
        if not text:
            return

        # Parse TOC entry: "Title\tPageNum" or "Title ... PageNum"
        title = None
        page_num = None

        # Try tab-separated first (Pandoc default)
        if "\t" in text:
            parts = text.rsplit("\t", 1)
            if len(parts) == 2 and parts[1].strip().isdigit():
                title = parts[0].strip()
                page_num = parts[1].strip()

        # Fallback: dot-separated
        if title is None:
            normalized = text.replace("\u2026", "...")
            match = re.match(r"^(.*?)\s*\.{3,}\s*(\d+)\s*$", normalized)
            if match:
                title = match.group(1).strip()
                page_num = match.group(2)

        # Fallback: space + trailing digits
        if title is None:
            match = re.match(r"^(.*?)\s{2,}(\d+)\s*$", text)
            if match:
                title = match.group(1).strip()
                page_num = match.group(2)

        if not title or not page_num:
            return

        # Determine heading level from the map
        title_lower = title.lower().strip()
        level = heading_levels.get(title_lower, 1)

        # Indentation: H1=0in, H2=0.5in, H3=1.0in
        indent_map = {1: 0, 2: 0.5, 3: 1.0}
        left_indent = indent_map.get(level, 0)

        _clear_paragraph(p)
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.left_indent = Inches(left_indent)

        # Tab stop at fixed 6.5in (right margin) for all entries,
        # ensuring page numbers are perfectly vertically aligned.
        # Dotted leader, right-aligned at the stop position.
        tab_stops = p.paragraph_format.tab_stops
        tab_stops.add_tab_stop(
            Inches(6.5), alignment=WD_TAB_ALIGNMENT.RIGHT, leader=WD_TAB_LEADER.DOTS
        )

        run = p.add_run(title)
        styles_handler._apply_font_style(run)

        # Prevent Word/LibreOffice from auto-formatting "1. " as a numbered list
        # which breaks the tab leader layout during PDF conversion
        if title and title[:1].isdigit():
            run.text = "\u200b" + run.text

        run = p.add_run("\t")
        styles_handler._apply_font_style(run)

        run = p.add_run(page_num)
        styles_handler._apply_font_style(run)

    def _build_heading_level_map(self) -> dict[str, int]:
        """Build a map of heading text -> heading level from the document."""
        levels = {}
        for p in self.doc.paragraphs:
            style_name = paragraph_style_name(p)
            if style_name.startswith("Heading"):
                parts = style_name.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    level = int(parts[-1])
                    text = p.text.strip().lower()
                    if text:
                        levels[text] = level
        return levels

    def format_lists(self) -> None:
        """Apply APA 7 list formatting.

        Regular bullet lists: bullet at 0.5in, text at 0.75in, hanging indent.
        Reference entries: no bullet, hanging indent at 0.5in (APA 7 standard).
        """
        from .apa_styles import APAStylesHandler

        styles_handler = APAStylesHandler(self.doc)
        in_references = False

        for p in self.doc.paragraphs:
            # Track sections via headings
            style_name = paragraph_style_name(p)
            if style_name == _HEADING_1:
                text_lower = p.text.lower().strip().rstrip(".")
                in_references = _is_references_heading(text_lower)
                continue

            p_pr = p._element.find(qn("w:pPr"))
            if p_pr is None:
                continue

            num_pr = p_pr.find(qn("w:numPr"))
            if num_pr is None:
                continue

            # Remove Pandoc's numbering reference
            p_pr.remove(num_pr)

            if in_references:
                # APA 7 reference: hanging indent, NO bullet
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.first_line_indent = Inches(-0.5)
            else:
                # APA 7 bullet list: bullet at 0.5in, text at 0.75in
                p.paragraph_format.left_indent = Inches(0.75)
                p.paragraph_format.first_line_indent = Inches(-0.25)

                # Tab stop so tab after bullet snaps text into position
                tab_stops = p.paragraph_format.tab_stops
                tab_stops.add_tab_stop(Inches(0.75), alignment=WD_TAB_ALIGNMENT.LEFT)

                # Prepend bullet character
                text = p.text
                if not text.startswith("\u2022") and not text.startswith("-"):
                    first_run = p.runs[0] if p.runs else None
                    if first_run:
                        first_run.text = "\u2022\t" + first_run.text
                    else:
                        run = p.add_run("\u2022\t")
                        styles_handler._apply_font_style(run)

    def apply_body_indent(self) -> None:
        """Final pass: apply first-line indent to all body paragraphs.

        Runs after _format_tables so that newly-created paragraphs (table
        descriptions, etc.) are also covered.
        """
        in_references = False
        in_toc = False
        in_abstract = False
        for p in self.doc.paragraphs:
            style_name = paragraph_style_name(p)
            text = p.text.strip()

            # Track References, TOC, and Abstract sections
            if style_name.startswith("Heading"):
                text_lower = text.lower().strip().rstrip(".")
                if _is_references_heading(text_lower):
                    in_references = True
                    in_toc = False
                    in_abstract = False
                elif "contenido" in text_lower or "index" in text_lower:
                    in_toc = True
                    in_references = False
                    in_abstract = False
                elif "resumen" in text_lower or "abstract" in text_lower:
                    in_abstract = True
                    in_toc = False
                    in_references = False
                else:
                    in_references = False
                    in_toc = False
                    in_abstract = False
                continue  # Skip headings

            if not text or len(text) < 5:
                continue  # Skip empty or very short labels

            # Skip TOC entries
            if in_toc:
                continue

            # Skip abstract paragraphs (block format, no indent per APA 7)
            if in_abstract:
                # End abstract section after keywords paragraph
                if text.lower().startswith(("palabras clave", "keywords")):
                    in_abstract = False
                continue

            # Skip if already indented (positive or negative)
            fli = p.paragraph_format.first_line_indent
            if fli is not None and fli != 0:
                continue

            # Skip centered paragraphs (cover page)
            align = p.paragraph_format.alignment
            if align == WD_ALIGN_PARAGRAPH.CENTER:
                continue

            # Skip block quotes: their 0.5" left indent replaces the
            # first-line indent (APA 8.27)
            left_indent = p.paragraph_format.left_indent
            if left_indent is not None and left_indent >= Inches(0.25):
                continue

            # Skip lists, captions, compact (Pandoc lists), and other special styles
            if "List" in style_name or "Caption" in style_name or "Compact" in style_name:
                continue

            # Skip table/figure caption labels and Nota paragraphs
            if text.startswith(("Tabla ", "Figura ")) and len(text.split()) <= 2:
                continue
            if text.startswith("Nota."):
                continue

            # Skip short all-italic paragraphs (table caption titles)
            # Long italic paragraphs are body text that should be indented
            if len(text) < 80 and p.runs and all(r.italic for r in p.runs if r.text.strip()):
                continue

            # Skip references section (handled with hanging indent)
            if in_references:
                continue

            # Apply APA first-line indent (0.5 inches / 1.27 cm)
            p.paragraph_format.first_line_indent = Inches(0.5)

    def fix_text_spacing_global(self) -> None:
        """Run merge_and_clean on all paragraphs."""
        for p in self.doc.paragraphs:
            if not paragraph_style_name(p).startswith("Heading"):
                self._merge_and_clean_paragraph(p)
                # Enforce left align
                if p.paragraph_format.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def _merge_and_clean_paragraph(self, p: ParagraphType) -> None:
        """Consolidate runs while preserving inline formatting boundaries.

        Groups consecutive runs by their (bold, italic) attributes and merges
        only within each group, so italic titles in references and the
        "Nota." italic split are kept intact.

        Skips paragraphs containing embedded images (w:drawing) to avoid
        destroying their XML structure.
        Skips Source Code paragraphs to preserve ASCII art and code formatting.
        """
        from docx.shared import Pt

        if not p.runs:
            return

        # Skip paragraphs with embedded images — clearing runs would destroy them
        if p._element.findall(f".//{qn('w:drawing')}"):
            return

        # Skip Source Code paragraphs — newlines are meaningful in code blocks
        style_name = p.style.name if p.style else ""
        if style_name in ("Source Code", "Source", "Code", "Preformatted", "HTMLPre"):
            return

        # Build groups of consecutive runs with the same formatting
        groups: list[tuple[bool, bool, str, str | None, Any]] = []
        for run in p.runs:
            t = run.text or ""
            t = t.replace("\r", " ")
            # Clean grid-table artifacts
            t = re.sub(r"[+|][-=]{3,}[+|]?", "", t)
            t = re.sub(r"={3,}", "", t)
            t = t.strip("|")

            is_bold = bool(run.bold)
            is_italic = bool(run.italic)
            font_name = run.font.name
            font_size = run.font.size

            if groups and groups[-1][0] == is_bold and groups[-1][1] == is_italic:
                # Same formatting — append text to the current group
                groups[-1] = (
                    is_bold,
                    is_italic,
                    groups[-1][2] + t,
                    font_name or groups[-1][3],
                    font_size or groups[-1][4],
                )
            else:
                groups.append((is_bold, is_italic, t, font_name, font_size))

        # Clear all existing runs
        for run in p.runs:
            run._r.getparent().remove(run._r)

        # Re-create one clean run per formatting group, preserving boundary spaces
        for idx, (is_bold, is_italic, text, font_name, font_size) in enumerate(groups):
            # Collapse multiple internal spaces but keep single boundary spaces
            text = re.sub(r"\s{2,}", " ", text)

            # Only strip leading space on the very first group
            if idx == 0:
                text = text.lstrip()
            # Only strip trailing space on the very last group
            if idx == len(groups) - 1:
                text = text.rstrip()

            if not text:
                continue

            new_run = p.add_run(text)
            new_run.font.name = font_name or DEFAULT_BODY_FONT
            new_run.font.size = font_size or Pt(12)
            if is_bold:
                new_run.bold = True
            if is_italic:
                new_run.italic = True

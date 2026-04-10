"""APA paragraph processing, formatting, and cleanup."""

import re
from typing import Any

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


class APAParagraphsHandler:
    """Handles paragraph processing, formatting, and cleanup per APA 7th Edition."""

    def __init__(self, doc, config: dict[str, Any] | None = None):
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_spacing_line(self) -> str:
        """Get line spacing from config with default."""
        return self.config.get("spacing", {}).get("line", "double")

    def _get_body_font(self) -> str:
        """Get body font name from config."""
        return self.config.get("fonts", {}).get("body", {}).get("name", "Times New Roman")

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
        heading_levels = self._build_heading_level_map()

        for p in self.doc.paragraphs:
            style_name = p.style.name if p.style else ""
            styles_handler._apply_font_to_paragraph(p)

            text_lower = p.text.lower()

            # Detect sections
            if style_name.startswith("Heading"):
                if "referencia" in text_lower or "reference" in text_lower:
                    in_references = True
                    in_toc = False
                    in_abstract = False
                    p.paragraph_format.page_break_before = True
                    first_paragraph_after_heading = True
                elif "resumen" in text_lower or "abstract" in text_lower:
                    # APA 7: RESUMEN title is centered and bold
                    in_abstract = True
                    in_toc = False
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.bold = True
                    p.paragraph_format.first_line_indent = Inches(0)
                elif "contenido" in text_lower or "index" in text_lower:
                    in_toc = True
                    p.paragraph_format.page_break_before = True
                else:
                    # Every Level 1 heading starts a new page in APA 7
                    if style_name == "Heading 1":
                        p.paragraph_format.page_break_before = True
                        first_paragraph_after_heading = True
                    # If leaving abstract section, force page break on any heading
                    if in_abstract or just_left_abstract:
                        p.paragraph_format.page_break_before = True
                        just_left_abstract = False
                    in_abstract = False
                    in_toc = False

                # Explicit APA heading alignment and bold on every heading
                if style_name == "Heading 1":
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
                elif style_name in ("Heading 2", "Heading 3"):
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.bold = True

                # Strip numbering property from headings (APA 7 doesn't use numbered headings)
                try:
                    p_pr = p._element.find(qn("w:pPr"))
                    if p_pr is not None:
                        num_pr = p_pr.find(qn("w:numPr"))
                        if num_pr is not None:
                            p_pr.remove(num_pr)
                except Exception:
                    pass
                p.paragraph_format.first_line_indent = Inches(0)

            # Line spacing
            spacing_line = self._get_spacing_line()
            if spacing_line == "double":
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            elif spacing_line == 1.5:
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
                    if text_strip.lower().startswith(
                        "palabras clave"
                    ) or text_strip.lower().startswith("keywords"):
                        in_abstract = False
                        just_left_abstract = True
                elif (
                    style_name in ("Body Text", "Normal", "First Paragraph", "Compact")
                    and text_strip
                    and p.paragraph_format.alignment != WD_ALIGN_PARAGRAPH.CENTER
                ):
                    # Force page break on first paragraph after abstract/keywords
                    if just_left_abstract:
                        p.paragraph_format.page_break_before = True
                        just_left_abstract = False
                    # APA 7: First paragraph after heading has NO indent
                    # Subsequent paragraphs have 0.5 inch first-line indent
                    if first_paragraph_after_heading:
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

    def _apply_paragraph_spacing_control(self, p) -> None:
        """Apply widow/orphan control per APA 7.

        APA 7 requires widow/orphan control to prevent single lines
        at the top or bottom of a page.
        """
        pPr = p._element.get_or_add_pPr()
        widowOrphan = OxmlElement("w:widowControl")
        pPr.append(widowOrphan)
        # Set adjustment for document grid (ensures consistent line height)
        docGrid = OxmlElement("w:docGrid")
        docGrid.set(qn("w:type"), "lines")
        docGrid.set(qn("w:linePitch"), "360")
        pPr.append(docGrid)

    def _apply_keep_with_next(self, p) -> None:
        """Apply keep-with-next to heading paragraphs per APA 7.

        Headings should stay on the same page as the following paragraph.
        """
        pPr = p._element.get_or_add_pPr()
        keepNext = OxmlElement("w:keepNext")
        pPr.append(keepNext)

    def _fix_citations(self, p) -> None:
        """Replace ' (Author y Author, YEAR)' with '&'."""
        citation_re = re.compile(
            r"\(([A-ZÁ-Ú][a-záéíóúñ]+(?:\s+(?:et\s+al\.))?)\s+y\s+([A-ZÁ-Ú][a-záéíóúñ]+),\s*(\d{4})\)"
        )
        for run in p.runs:
            if " y " in run.text and "(" in run.text:
                run.text = citation_re.sub(r"(\1 & \2, \3)", run.text)

    def _format_toc_entry(self, p, heading_levels) -> None:
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

        p.clear()
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.left_indent = Inches(left_indent)

        # Tab stop at fixed 6.5in (right margin) for all entries,
        # ensuring page numbers are perfectly vertically aligned.
        # leader=1 = DOTS (......), alignment=2 = RIGHT
        tab_stops = p.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Inches(6.5), alignment=2, leader=1)

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
            style_name = p.style.name if p.style else ""
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
            style_name = p.style.name if p.style else ""
            if style_name == "Heading 1":
                text_lower = p.text.lower().strip()
                in_references = "referencia" in text_lower or "reference" in text_lower
                continue

            pPr = p._element.find(qn("w:pPr"))
            if pPr is None:
                continue

            numPr = pPr.find(qn("w:numPr"))
            if numPr is None:
                continue

            # Remove Pandoc's numbering reference
            pPr.remove(numPr)

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
                tab_stops.add_tab_stop(Inches(0.75), alignment=0)

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
            style_name = p.style.name if p.style else ""
            text = p.text.strip()

            # Track References, TOC, and Abstract sections
            if style_name.startswith("Heading"):
                text_lower = text.lower()
                if "referencia" in text_lower or "reference" in text_lower:
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
                if text.lower().startswith("palabras clave") or text.lower().startswith("keywords"):
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

            # Skip lists, captions, compact (Pandoc lists), and other special styles
            if "List" in style_name or "Caption" in style_name or "Compact" in style_name:
                continue

            # Skip table/figure caption labels and Nota paragraphs
            if (text.startswith("Tabla ") or text.startswith("Figura ")) and len(text.split()) <= 2:
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
            if not p.style or not p.style.name.startswith("Heading"):
                self._merge_and_clean_paragraph(p)
                # Enforce left align
                if p.paragraph_format.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def _merge_and_clean_paragraph(self, p) -> None:
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
        groups: list[tuple[bool, bool, str, str | None, object | None]] = []
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
        for run in list(p.runs):
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
            new_run.font.name = font_name or "Times New Roman"
            new_run.font.size = font_size or Pt(12)
            if is_bold:
                new_run.bold = True
            if is_italic:
                new_run.italic = True

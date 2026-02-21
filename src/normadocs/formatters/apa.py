import re

from docx import Document
from docx.document import Document as DocumentObject
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from ..models import DocumentMetadata
from .base import DocumentFormatter


class APADocxFormatter(DocumentFormatter):
    """
    Applies APA 7th Edition formatting to a DOCX file.
    """

    def __init__(self, doc_path: str):
        super().__init__(doc_path)
        self.doc: DocumentObject = Document(doc_path)

    def process(self, meta: DocumentMetadata):
        """Run the full formatting pipeline."""
        self._setup_page_layout()
        self._create_styles()
        self._add_cover_page(meta)
        self._process_paragraphs()
        self._format_tables()
        self._format_figures()
        self._apply_body_indent()
        self._format_keywords(meta)
        self._fix_text_spacing_global()

    def _make_figure_paragraph(self, text, bold=False, italic=False, space_after="0"):
        """Helper: create a Times New Roman 12pt paragraph for figure captions."""
        p_el = OxmlElement("w:p")
        p_pr = OxmlElement("w:pPr")
        p_sp = OxmlElement("w:spacing")
        p_sp.set(qn("w:after"), space_after)
        p_sp.set(qn("w:line"), "480")
        p_sp.set(qn("w:lineRule"), "auto")
        p_pr.append(p_sp)
        p_el.append(p_pr)

        run = OxmlElement("w:r")
        rPr = OxmlElement("w:rPr")
        if bold:
            rPr.append(OxmlElement("w:b"))
        if italic:
            rPr.append(OxmlElement("w:i"))
        rn = OxmlElement("w:rFonts")
        rn.set(qn("w:ascii"), "Times New Roman")
        rn.set(qn("w:hAnsi"), "Times New Roman")
        rPr.append(rn)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "24")
        rPr.append(sz)
        run.append(rPr)
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        t.text = text
        run.append(t)
        p_el.append(run)
        return p_el

    def _format_figures(self):
        """Add APA 7 figure captions: Label + Title ABOVE, Nota BELOW.

        APA 7 figure order:
          Figura N        (bold, left-aligned)
          Italic title    (italic, left-aligned, no trailing period)
          [image]         (centered)
          Nota. context   (italic "Nota.", then regular text)
        """
        ns_wp = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
        image_paragraphs = []

        for p in self.doc.paragraphs:
            drawings = p._element.findall(f".//{qn('w:drawing')}")
            if drawings:
                alt_text = ""
                for drawing in drawings:
                    for docPr in drawing.iter(f"{{{ns_wp}}}docPr"):
                        alt_text = docPr.get("descr", "") or docPr.get("name", "")
                        break
                    if not alt_text:
                        ns_pic = "http://schemas.openxmlformats.org/drawingml/2006/picture"
                        for cNvPr in drawing.iter(f"{{{ns_pic}}}cNvPr"):
                            alt_text = cNvPr.get("descr", "") or cNvPr.get("name", "")
                            break
                image_paragraphs.append((p, alt_text.strip()))

        for _, (p, _) in enumerate(image_paragraphs, start=1):
            # Center the image paragraph
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)

    def _apply_body_indent(self):
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

    def save(self, output_path: str):
        self.doc.save(str(output_path))

    def _apply_apa_table_borders(self, table):
        """
        Apply APA-style borders:
        - Top/Bottom of table: single line
        - Bottom of header row: single line
        - No vertical lines.
        """
        # Single-pass: set correct borders for each row position

        # Clear all borders first for all cells
        for row in table.rows:
            for cell in row.cells:
                self._set_cell_border(
                    cell, top={}, bottom={}, start={}, end={}, insideH={}, insideV={}
                )

        # Iterate once and set correct edges.
        num_rows = len(table.rows)
        for i, row in enumerate(table.rows):
            is_first_row = i == 0
            is_last_row = i == num_rows - 1

            for cell in row.cells:
                borders = {}
                if is_first_row:
                    borders["top"] = {"val": "single", "sz": "12", "color": "auto"}
                    borders["bottom"] = {
                        "val": "single",
                        "sz": "6",
                        "color": "auto",
                    }  # Header underline

                if is_last_row:
                    borders["bottom"] = {"val": "single", "sz": "12", "color": "auto"}

                # Apply
                self._set_cell_border(cell, **borders)

    # ────────────────────────── OXML Helpers ──────────────────────────

    def _set_cell_border(self, cell, **kwargs):
        """Set border on a table cell (OpenXML). Clears existing first."""
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        # Remove any existing cell borders
        for old in tcPr.findall(qn("w:tcBorders")):
            tcPr.remove(old)
        tcBorders = OxmlElement("w:tcBorders")
        for edge_name in ("start", "top", "end", "bottom", "insideH", "insideV"):
            if edge_name in kwargs:
                el = OxmlElement(f"w:{edge_name}")
                for attr, val in kwargs[edge_name].items():
                    el.set(qn(f"w:{attr}"), str(val))
                tcBorders.append(el)
        tcPr.append(tcBorders)

    # ────────────────────────── Formatting Steps ──────────────────────────

    def _setup_page_layout(self):
        """Set margins to 1 inch and add page numbers top-right."""
        for section in self.doc.sections:
            section.page_height = Inches(11)
            section.page_width = Inches(8.5)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)

            # Disable separate first-page header/footer
            section.different_first_page_header_footer = False

            # Clear footers completely to prevent Pandoc page numbers at bottom
            footer = section.footer
            footer.is_linked_to_previous = False
            for p in footer.paragraphs:
                p.clear()
                # Also remove any field codes (PAGE) Pandoc may have injected
                for child in list(p._element):
                    p._element.remove(child)

            self._add_page_number(section)

    def _add_page_number(self, section):
        """Add page number top-right in header."""
        header = section.header
        header.is_linked_to_previous = False

        # Clear existing header text
        for p in header.paragraphs:
            p.clear()

        hp = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        run = hp.add_run()
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        run._r.append(fld_begin)
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " PAGE "
        run._r.append(instr)
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        run._r.append(fld_end)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

        # Strip excessive paragraphs in header
        while len(header.paragraphs) > 1:
            p_elem = header.paragraphs[-1]._element
            p_elem.getparent().remove(p_elem)

    def _create_styles(self):
        """
        Configure Normal, Headings, and other styles.
        """
        styles = self.doc.styles

        # Normal
        normal = styles["Normal"]
        self._apply_font_style(normal, size=12)
        pf = normal.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Body Text
        for style_name in ["Body Text", "First Paragraph"]:
            try:
                style = styles[style_name]
                self._apply_font_style(style, size=12)
                style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
                style.paragraph_format.first_line_indent = Inches(0.5)
                style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            except KeyError:
                pass

        # Headings
        configs = {
            "Heading 1": {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.CENTER,
            },
            "Heading 2": {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
            },
            "Heading 3": {
                "bold": True,
                "italic": True,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
            },
        }
        for sn, cfg in configs.items():
            try:
                h = styles[sn]
                self._apply_font_style(h, size=12, bold=cfg["bold"], italic=cfg["italic"])
                h.paragraph_format.alignment = cfg["align"]
                h.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
                h.paragraph_format.page_break_before = False
            except KeyError:
                pass

        # Remove Pandoc Table Style borders
        self._neutralize_table_style()

    def _neutralize_table_style(self):
        """Remove borders from the 'Table' style definition."""
        ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for style_el in self.doc.styles.element.findall(f"{{{ns}}}style"):
            style_id = style_el.get(f"{{{ns}}}styleId", "")
            if style_id == "Table":
                tblPr_el = style_el.find(f"{{{ns}}}tblPr")
                if tblPr_el is not None:
                    for old_b in tblPr_el.findall(f"{{{ns}}}tblBorders"):
                        tblPr_el.remove(old_b)

                    # Set explicit no borders
                    brd = OxmlElement("w:tblBorders")
                    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
                        e = OxmlElement(f"w:{edge}")
                        e.set(qn("w:val"), "none")
                        e.set(qn("w:sz"), "0")
                        e.set(qn("w:space"), "0")
                        brd.append(e)
                    tblPr_el.append(brd)

    def _apply_font_style(
        self,
        style_or_run,
        font_name="Times New Roman",
        size=12,
        bold=None,
        italic=None,
        color_rgb=(0, 0, 0),
    ):
        """Helper to apply font settings."""
        font = style_or_run.font
        font.name = font_name
        font.size = Pt(size)
        if hasattr(font.color, "rgb"):
            font.color.rgb = RGBColor(*color_rgb)
        if bold is not None:
            font.bold = bold
        if italic is not None:
            font.italic = italic

    def _apply_font_to_paragraph(self, paragraph, font_size=None):
        size = 12 if font_size is None else font_size.pt
        for run in paragraph.runs:
            self._apply_font_style(run, size=size)

    def _add_cover_page(self, meta: DocumentMetadata):
        """
        Insert a new paragraph at index 0 for the cover page.
        """
        # Create a new paragraph for the cover content
        self.doc.add_paragraph()
        if self.doc.paragraphs:
            self.doc.paragraphs[0].insert_paragraph_before("")

        # Extract extra fields safely
        instructor = meta.extra.get("instructor", "")
        due_date = meta.date or ""
        institution = meta.institution or ""
        program = meta.program or ""
        ficha = meta.ficha or ""
        center = meta.center or ""

        # APA 7 Student Paper: title in upper third of page (~3-4 lines down
        # from top margin), then blank line, then author info.
        # With double spacing (24pt lines), 6 blank lines ≈ top-third position.
        elements = [
            ("", False),  # Spacer
            ("", False),  # Spacer
            ("", False),  # Spacer
            ("", False),  # Spacer
            ("", False),  # Spacer
            ("", False),  # Spacer
            (meta.title, True),  # Title: centred, bold
            ("", False),  # Blank line between title and author info
            (meta.author or "", False),
        ]

        # Append remaining fields only if they exist
        for field_val in [program, ficha, institution, center, instructor, due_date]:
            if field_val:
                elements.append((field_val, False))

        ref_p = self.doc.paragraphs[0]

        for text, is_bold in elements:
            p = ref_p.insert_paragraph_before(text)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.style = self.doc.styles["Normal"]

            # Apply bold manually if needed
            if is_bold and text.strip() and p.runs:
                p.runs[0].bold = True

        # Remove the leftover reference paragraph to avoid blank page 2.
        ref_p._element.getparent().remove(ref_p._element)

        # Remove the trailing empty paragraph added by doc.add_paragraph()
        last_p = self.doc.paragraphs[-1]
        if not last_p.text.strip():
            last_p._element.getparent().remove(last_p._element)

        # Add page break after cover page so body text starts on page 2
        # Find the last cover paragraph (centered) and set page break on the
        # first non-cover paragraph that follows
        cover_ended = False
        for p in self.doc.paragraphs:
            if cover_ended:
                # First paragraph after cover — force new page
                p.paragraph_format.page_break_before = True
                break
            # Cover paragraphs are centered; first non-centered = end of cover
            style_name = p.style.name if p.style else ""
            if style_name.startswith("Heading"):
                p.paragraph_format.page_break_before = True
                break
            if p.alignment != WD_ALIGN_PARAGRAPH.CENTER and p.text.strip():
                cover_ended = True
                p.paragraph_format.page_break_before = True
                break

    def _process_paragraphs(self):
        """Iterate through paragraphs to apply indentation, fix citations, etc."""
        in_references = False
        in_toc = False
        in_abstract = False
        just_left_abstract = False
        heading_levels = self._build_heading_level_map()

        for p in self.doc.paragraphs:
            style_name = p.style.name if p.style else ""
            self._apply_font_to_paragraph(p)

            text_lower = p.text.lower()

            # Detect sections
            if style_name.startswith("Heading"):
                if "referencia" in text_lower or "reference" in text_lower:
                    in_references = True
                    in_toc = False
                    in_abstract = False
                    p.paragraph_format.page_break_before = True
                elif "resumen" in text_lower or "abstract" in text_lower:
                    in_abstract = True
                    in_toc = False
                elif "contenido" in text_lower or "index" in text_lower:
                    in_toc = True
                    p.paragraph_format.page_break_before = True
                else:
                    # If leaving abstract section, force page break
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
                elif style_name in ("Heading 2", "Heading 3"):
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in p.runs:
                        run.bold = True
                p.paragraph_format.first_line_indent = Inches(0)

            # Line spacing
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)

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
                    p.paragraph_format.first_line_indent = Inches(0.5)

            # Fix citations (y -> &)
            self._fix_citations(p)

    def _format_toc_entry(self, p, heading_levels):
        """Format Table of Contents entries with correct indentation."""
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
        self._apply_font_style(run)

        run = p.add_run("\t")
        self._apply_font_style(run)

        run = p.add_run(page_num)
        self._apply_font_style(run)

    def _build_heading_level_map(self):
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

    def _fix_citations(self, p):
        """Replace ' (Author y Author, YEAR)' with '&'."""
        citation_re = re.compile(
            r"\(([A-ZÁ-Ú][a-záéíóúñ]+(?:\s+(?:et\s+al\.))?)\s+y\s+([A-ZÁ-Ú][a-záéíóúñ]+),\s*(\d{4})\)"
        )
        for run in p.runs:
            if " y " in run.text and "(" in run.text:
                run.text = citation_re.sub(r"(\1 & \2, \3)", run.text)

    def _format_tables(self):
        """Apply APA borders and formatting to all tables."""
        for i, table in enumerate(self.doc.tables):
            self._apply_apa_table_borders(table)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            # Set table to full page width with fixed layout
            tbl_pr = table._tbl.tblPr
            if tbl_pr is not None:
                # Use fixed layout for consistent rendering
                existing_layout = tbl_pr.find(qn("w:tblLayout"))
                if existing_layout is not None:
                    tbl_pr.remove(existing_layout)
                layout = OxmlElement("w:tblLayout")
                layout.set(qn("w:type"), "fixed")
                tbl_pr.append(layout)

                # Set table width to 100% of page
                tbl_w = tbl_pr.find(qn("w:tblW"))
                if tbl_w is None:
                    tbl_w = OxmlElement("w:tblW")
                    tbl_pr.append(tbl_w)
                tbl_w.set(qn("w:type"), "pct")
                tbl_w.set(qn("w:w"), "5000")  # 100% in fifths of a percent

                # Set table-level cell margins to zero
                existing_tblcm = tbl_pr.find(qn("w:tblCellMar"))
                if existing_tblcm is not None:
                    tbl_pr.remove(existing_tblcm)
                tbl_cell_mar = OxmlElement("w:tblCellMar")
                for side in ("top", "bottom", "start", "end"):
                    el = OxmlElement(f"w:{side}")
                    el.set(qn("w:w"), "0")
                    el.set(qn("w:type"), "dxa")
                    tbl_cell_mar.append(el)
                tbl_pr.append(tbl_cell_mar)

            # Reduce cell margins for all tables to maximize usable space
            for row in table.rows:
                for cell in row.cells:
                    tc_pr = cell._element.find(qn("w:tcPr"))
                    if tc_pr is None:
                        tc_pr = OxmlElement("w:tcPr")
                        cell._element.insert(0, tc_pr)
                    # Remove existing margins
                    existing_mar = tc_pr.find(qn("w:tcMar"))
                    if existing_mar is not None:
                        tc_pr.remove(existing_mar)
                    tc_mar = OxmlElement("w:tcMar")
                    for side in ("top", "bottom", "start", "end"):
                        el = OxmlElement(f"w:{side}")
                        el.set(qn("w:w"), "0")  # zero margin
                        el.set(qn("w:type"), "dxa")
                        tc_mar.append(el)
                    tc_pr.append(tc_mar)

            # Scale font size based on column count
            num_cols = len(table.columns)
            if num_cols >= 6:
                font_size = 7
            elif num_cols >= 5:
                font_size = 8
            else:
                font_size = 10

            # Set proportional column widths based on content
            if num_cols > 2:
                # Calculate max content length per column (across all rows)
                max_content_len = [0] * num_cols
                max_word_len = [0] * num_cols
                for row in table.rows:
                    for ci, cell in enumerate(row.cells):
                        if ci < num_cols:
                            text = cell.text.strip()
                            max_content_len[ci] = max(max_content_len[ci], len(text))
                            for word in text.split():
                                max_word_len[ci] = max(max_word_len[ci], len(word))

                # Char width estimate per font size (includes ~0.1in padding)
                cw_map = {7: 0.08, 8: 0.10, 10: 0.12}
                cw = cw_map.get(font_size, 0.10)
                # Minimum = longest word * char width + padding
                min_widths = [max(w * cw + 0.12, 0.70) for w in max_word_len]
                total_min = sum(min_widths)

                avail = 6.5
                col_widths_inches = []
                if total_min <= avail:
                    remaining = avail - total_min
                    total_content = sum(max_content_len) or 1
                    for ci in range(num_cols):
                        extra = remaining * (max_content_len[ci] / total_content)
                        col_widths_inches.append(min_widths[ci] + extra)
                else:
                    # Proportional fallback
                    total_content = sum(max_content_len) or 1
                    for ci in range(num_cols):
                        proportion = max_content_len[ci] / total_content
                        col_widths_inches.append(max(avail * proportion, 0.85))

                # CRITICAL: Normalize total to exactly 6.5in so LibreOffice
                # doesn't proportionally downscale all columns
                current_total = sum(col_widths_inches)
                if current_total > 0 and abs(current_total - avail) > 0.01:
                    scale = avail / current_total
                    col_widths_inches = [w * scale for w in col_widths_inches]

                # Apply widths to columns, cells, AND gridCol elements
                tbl_grid = table._tbl.find(qn("w:tblGrid"))
                grid_cols = tbl_grid.findall(qn("w:gridCol")) if tbl_grid is not None else []
                for ci, col in enumerate(table.columns):
                    col_width = Inches(col_widths_inches[ci])
                    col.width = col_width
                    # Update gridCol (authoritative for LibreOffice)
                    if ci < len(grid_cols):
                        grid_cols[ci].set(qn("w:w"), str(int(col_widths_inches[ci] * 1440)))
                    # Update each cell width
                    for row in table.rows:
                        if ci < len(row.cells):
                            row.cells[ci].width = col_width

            # Repeat table headers across pages
            if len(table.rows) > 0:
                tr = table.rows[0]._tr
                tblHeader = OxmlElement("w:tblHeader")
                tr.get_or_add_trPr().append(tblHeader)

            # Clean and merge cell text
            for row in table.rows:
                for cell in row.cells:
                    # Collect ALL text from ALL paragraphs in this cell
                    cell_texts = []
                    for p in cell.paragraphs:
                        para_text = ""
                        for run in p.runs:
                            t = run.text or ""
                            t = re.sub(r"[+|][-=]{3,}[+|]?", "", t)
                            t = re.sub(r"={3,}", "", t)
                            t = t.strip("|").strip()
                            para_text += " " + t if para_text else t
                        para_text = para_text.strip()
                        if para_text:
                            cell_texts.append(para_text)

                    # Join all paragraphs into one continuous text
                    merged = " ".join(cell_texts)
                    # Strip ** bold markers left by Pandoc
                    merged = merged.replace("**", "")
                    # Strip * italic markers
                    merged = merged.replace("*", "")
                    # Fix missing spaces between words (camelCase joins from line merging)
                    # E.g: "deStock" -> "de Stock", "ProductOwner)" -> "Product Owner)"
                    merged = re.sub(r"([a-záéíóúñ])([A-ZÁÉÍÓÚÑ])", r"\1 \2", merged)
                    # Collapse multiple spaces
                    merged = re.sub(r"\s{2,}", " ", merged).strip()

                    # Clear all paragraphs except the first, set merged text
                    if cell.paragraphs:
                        first_p = cell.paragraphs[0]
                        # Detect if header row (first row of table)
                        is_header = row == table.rows[0]

                        # Clear first paragraph
                        first_p.clear()
                        new_run = first_p.add_run(merged)
                        self._apply_font_style(new_run, size=font_size)
                        if is_header:
                            new_run.bold = True

                        # Remove extra paragraphs from the cell
                        for extra_p in list(cell.paragraphs[1:]):
                            extra_p._element.getparent().remove(extra_p._element)

            self._add_table_caption(table, i + 1)

    def _add_table_caption(self, table, num):
        """
        Add 'Tabla N' (Bold) and Table Title (Italic).
        Extracts the title from the preceding paragraph, or from the table's
        own 'Nombre' / 'Atributo de Calidad' row if no preceding title exists.
        """
        parent = table._tbl.getparent()
        if parent is None:
            return

        idx = parent.index(table._tbl)
        table_title = None

        # Try to retrieve the title from the immediately preceding paragraph
        if idx > 0:
            prev_el = parent[idx - 1]
            if prev_el.tag.endswith("p"):
                from docx.text.paragraph import Paragraph

                prev_p = Paragraph(prev_el, self.doc)
                ptxt = prev_p.text.strip()
                if ptxt and not ptxt.isdigit() and "[Título" not in ptxt:
                    table_title = ptxt
                    parent.remove(prev_el)

        # If no title found, try extracting from the table's own content
        if not table_title:
            table_title = self._extract_table_title(table)

        if not table_title:
            table_title = "[Título de la Tabla]"

        # Create paragraph for "Tabla N"
        p_label = OxmlElement("w:p")
        p_label_pr = OxmlElement("w:pPr")
        p_spacing = OxmlElement("w:spacing")
        p_spacing.set(qn("w:after"), "0")  # No space after label
        p_spacing.set(qn("w:line"), "480")  # Double spacing
        p_spacing.set(qn("w:lineRule"), "auto")
        p_label_pr.append(p_spacing)
        p_label.append(p_label_pr)

        run_label = OxmlElement("w:r")
        rPr_label = OxmlElement("w:rPr")
        b_label = OxmlElement("w:b")
        rPr_label.append(b_label)
        run_label.append(rPr_label)
        t_label = OxmlElement("w:t")
        t_label.text = f"Tabla {num}"
        run_label.append(t_label)
        p_label.append(run_label)

        # Create paragraph for Title placeholder
        p_title = OxmlElement("w:p")
        p_title_pr = OxmlElement("w:pPr")
        p_spacing_title = OxmlElement("w:spacing")
        p_spacing_title.set(qn("w:after"), "0")
        p_spacing_title.set(qn("w:line"), "480")  # Double spacing
        p_spacing_title.set(qn("w:lineRule"), "auto")
        p_title_pr.append(p_spacing_title)
        p_title.append(p_title_pr)

        run_title = OxmlElement("w:r")
        rPr_title = OxmlElement("w:rPr")
        i_title = OxmlElement("w:i")
        rPr_title.append(i_title)
        run_title.append(rPr_title)
        t_title = OxmlElement("w:t")
        t_title.text = table_title
        run_title.append(t_title)
        p_title.append(run_title)

        # Insert before table
        parent.insert(parent.index(table._tbl), p_label)
        parent.insert(parent.index(table._tbl), p_title)

    @staticmethod
    def _extract_table_title(table):
        """
        Extract a descriptive title from a grid table's own content.
        Looks for 'Nombre' or 'Atributo de Calidad' rows and combines with the ID.
        Returns None if no suitable data found.
        """
        if len(table.rows) < 2 or len(table.columns) < 2:
            return None

        # Build a dict of label → value from first column pairs
        data = {}
        for row in table.rows[:4]:  # Only check first 4 rows
            cells = row.cells
            if len(cells) >= 2:
                label = cells[0].text.strip().lower()
                value = cells[1].text.strip()
                if label and value:
                    data[label] = value

        # Extract ID and name/attribute
        table_id = data.get("id", "")
        name = data.get("nombre", "") or data.get("atributo de calidad", "")

        if name and table_id:
            return f"{table_id}: {name}"
        if name:
            return name

        return None

    def _format_keywords(self, meta: DocumentMetadata):
        """Format 'Palabras clave', and add repeated title + page break."""
        found_kw = False
        kw_idx = -1

        for i, p in enumerate(self.doc.paragraphs):
            if "palabras clave" in p.text.lower() or "keywords" in p.text.lower():
                found_kw = True
                kw_idx = i

                full = p.text.strip()
                # Regex for "Palabras clave: ..." or "Keywords: ..."
                match = re.search(r"((?:Palabras\s+clave|Keywords):)(.*)", full, re.IGNORECASE)
                if match:
                    label, content = match.groups()
                    p.clear()
                    p.paragraph_format.first_line_indent = Inches(0.5)
                    r1 = p.add_run(label + " ")
                    r1.italic = True
                    self._apply_font_style(r1)
                    r2 = p.add_run(content.strip())
                    self._apply_font_style(r2)
                break

        if found_kw and kw_idx != -1:
            # Logic to insert page break after keywords would go here
            pass

    def _fix_text_spacing_global(self):
        """Run merge_and_clean on all paragraphs."""
        for p in self.doc.paragraphs:
            if not p.style or not p.style.name.startswith("Heading"):
                self._merge_and_clean_paragraph(p)
                # Enforce left align
                if p.paragraph_format.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def _merge_and_clean_paragraph(self, p):
        """Consolidate runs to fix spacing and remove artifacts from hard returns."""
        if not p.runs:
            return

        # Collect all text, joining with space where breaks existed
        full_text = ""
        for run in p.runs:
            t = run.text or ""
            # Replace newlines inside a run with space (hard returns within cells)
            t = t.replace("\n", " ").replace("\r", " ")
            # Clean grid-table artifacts
            t = re.sub(r"[+|][-=]{3,}[+|]?", "", t)
            t = re.sub(r"={3,}", "", t)
            t = t.strip("|")
            full_text += t

        # Collapse multiple spaces into one
        full_text = re.sub(r"\s{2,}", " ", full_text).strip()

        if not full_text:
            return

        # Preserve the formatting of the first run
        if p.runs:
            first_run = p.runs[0]
            was_bold = first_run.bold
            was_italic = first_run.italic
            font_name = first_run.font.name
            font_size = first_run.font.size

            # Clear all runs
            for run in list(p.runs):
                run._r.getparent().remove(run._r)

            # Add single clean run
            new_run = p.add_run(full_text)
            if font_name:
                new_run.font.name = font_name
            if font_size:
                new_run.font.size = font_size
            if was_bold:
                new_run.bold = True
            if was_italic:
                new_run.italic = True

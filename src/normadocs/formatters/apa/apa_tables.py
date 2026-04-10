"""APA table formatting, borders, captions, and notes."""

import re
from typing import Any

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches

PAGE_CONTENT_WIDTH = 6.5

COMPANY_KEYWORDS = frozenset(["mackroph", "tecnoshop", "devsoft"])


class APATablesHandler:
    """Handles table formatting, borders, captions, and notes per APA 7th Edition."""

    def __init__(self, doc, config: dict[str, Any] | None = None):
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_table_config(self) -> dict[str, Any]:
        """Get table configuration from config with defaults."""
        return self.config.get(
            "tables",
            {
                "borders": "horizontal_only",
                "caption_prefix": "Tabla",
                "caption_above": True,
                "note_suffix": "Elaboración propia.",
                "vertical_align": "top",
            },
        )

    def _get_body_font(self) -> str:
        """Get body font name from config."""
        return self.config.get("fonts", {}).get("body", {}).get("name", "Times New Roman")

    def _apply_font_style(self, run, size: int = 12) -> None:
        """Apply font style to a run (helper for this handler)."""
        from .apa_styles import APAStylesHandler

        handler = APAStylesHandler(self.doc)
        handler._apply_font_style(run, size=size)

    def format_tables(self) -> None:
        """Apply APA borders and formatting to all tables."""
        for _i, table in enumerate(self.doc.tables):
            self._apply_apa_table_borders(table)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            # Set table to full page width with FIXED layout
            tbl_pr = table._tbl.tblPr
            if tbl_pr is not None:
                # Use FIXED layout so LibreOffice respects explicit column widths
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

                # Set table-level cell margins
                existing_tblcm = tbl_pr.find(qn("w:tblCellMar"))
                if existing_tblcm is not None:
                    tbl_pr.remove(existing_tblcm)
                tbl_cell_mar = OxmlElement("w:tblCellMar")
                for side in ("top", "bottom", "start", "end"):
                    el = OxmlElement(f"w:{side}")
                    el.set(qn("w:w"), "57")  # ~1mm padding
                    el.set(qn("w:type"), "dxa")
                    tbl_cell_mar.append(el)
                tbl_pr.append(tbl_cell_mar)

            # Reduce cell margins, set vertical top-alignment and left-alignment
            for _row_idx, row in enumerate(table.rows):
                for cell in row.cells:
                    tc_pr = cell._element.find(qn("w:tcPr"))
                    if tc_pr is None:
                        tc_pr = OxmlElement("w:tcPr")
                        cell._element.insert(0, tc_pr)

                    # Vertical alignment: top (APA 7 requirement)
                    existing_valign = tc_pr.find(qn("w:vAlign"))
                    if existing_valign is not None:
                        tc_pr.remove(existing_valign)
                    v_align = OxmlElement("w:vAlign")
                    v_align.set(qn("w:val"), "top")
                    tc_pr.append(v_align)

                    # Remove existing margins
                    existing_mar = tc_pr.find(qn("w:tcMar"))
                    if existing_mar is not None:
                        tc_pr.remove(existing_mar)
                    tc_mar = OxmlElement("w:tcMar")
                    for side in ("top", "bottom", "start", "end"):
                        el = OxmlElement(f"w:{side}")
                        el.set(qn("w:w"), "28")  # small margin (~0.5mm)
                        el.set(qn("w:type"), "dxa")
                        tc_mar.append(el)
                    tc_pr.append(tc_mar)

                    # Left-align all cell paragraphs (APA 7 for text content)
                    for p in cell.paragraphs:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        p_pr = p._element.get_or_add_pPr()
                        jc = p_pr.get_or_add_jc()
                        jc.set(qn("w:val"), "left")
                        # Prevent word breaking in paragraphs - set overflow behavior
                        overflow = OxmlElement("w:overflow")
                        overflow.set(qn("w:val"), "continue")
                        p_pr.append(overflow)

                    # Add noWrap to cell properties to prevent LibreOffice from breaking words
                    existing_no_wrap = tc_pr.find(qn("w:noWrap"))
                    if existing_no_wrap is None:
                        no_wrap = OxmlElement("w:noWrap")
                        tc_pr.append(no_wrap)

            # Scale font size based on column count (min 12pt per APA 7)
            num_cols = len(table.columns)
            if num_cols >= 8:
                font_size = 9
            elif num_cols >= 6:
                font_size = 10
            else:
                font_size = 12  # APA 7 requires 12pt minimum

            # Set proportional column widths based on content
            if num_cols >= 2:
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

                # Char width estimate per font size (includes ~0.05in padding)
                cw_map = {9: 0.08, 10: 0.09, 11: 0.10, 12: 0.10}
                cw = cw_map.get(font_size, 0.09)

                # Minimum column width: fit longest word with small padding
                # Use smaller minimum for tables with many columns
                min_col = max(0.8, 6.0 / num_cols)
                min_widths = [max(w * cw + 0.08, min_col) for w in max_word_len]
                total_min = sum(min_widths)

                avail = PAGE_CONTENT_WIDTH
                col_widths_inches = []
                if total_min <= avail:
                    remaining = avail - total_min
                    total_content = sum(max_content_len) or 1
                    for ci in range(num_cols):
                        extra = remaining * (max_content_len[ci] / total_content)
                        col_widths_inches.append(min_widths[ci] + extra)
                else:
                    # Proportional fallback with floor
                    total_content = sum(max_content_len) or 1
                    floor_w = min_col
                    for ci in range(num_cols):
                        proportion = max_content_len[ci] / total_content
                        col_widths_inches.append(max(avail * proportion, floor_w))

                # CRITICAL: Normalize total to exactly PAGE_CONTENT_WIDTH
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

            # Prevent table rows from being split across pages
            # w:cantSplit: la fila completa debe estar en una página (no se corta a mitad)
            for row in table.rows:
                tr_pr = row._tr.get_or_add_trPr()
                # Remove existing cantSplit if any
                existing = tr_pr.find(qn("w:cantSplit"))
                if existing is not None:
                    tr_pr.remove(existing)
                # Add cantSplit with value "1" (true - row cannot be split)
                cant_split = OxmlElement("w:cantSplit")
                cant_split.set(qn("w:val"), "1")
                tr_pr.append(cant_split)

            # Add table-level properties to prevent table splitting
            tbl_pr_elem = table._tbl.tblPr
            if tbl_pr_elem is None:
                tbl_pr_elem = OxmlElement("w:tblPr")
                table._tbl.insert(0, tbl_pr_elem)

            # Add tblLook element to control widow/orphan behavior at table level
            tbl_look = OxmlElement("w:tblLook")
            tbl_look.set(qn("w:val"), "04A0")
            tbl_look.set(qn("w:first"), "1")
            tbl_look.set(qn("w:last"), "1")
            tbl_look.set(qn("w:hBand"), "1")
            tbl_look.set(qn("w:vBand"), "1")
            tbl_pr_elem.append(tbl_look)

            # Add table-level property to prevent row splitting at page boundary
            # w:tblSplit: 0 means table rows stay together, don't split across pages
            existing_split = tbl_pr_elem.find(qn("w:tblSplit"))
            if existing_split is not None:
                tbl_pr_elem.remove(existing_split)
            tbl_split = OxmlElement("w:tblSplit")
            tbl_split.set(qn("w:val"), "0")  # 0 = don't split rows
            tbl_pr_elem.append(tbl_split)

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
                    # Fix incorrectly split technology names
                    merged = merged.replace("i Phone", "iPhone").replace("i OS", "iOS")
                    merged = merged.replace("Whats App", "WhatsApp").replace("DDo S", "DDoS")
                    merged = merged.replace("Java Script", "JavaScript").replace(
                        "Postgre SQL", "PostgreSQL"
                    )
                    # Fix specific split words and numbers
                    merged = merged.replace("Dedicació n", "Dedicación")
                    merged = merged.replace("REQUERIMIENTO S", "REQUERIMIENTOS")
                    merged = merged.replace("REQUERIMIENT S", "REQUERIMIENTOS")
                    # Fix split monetary values (e.g., "$22,750,00 0" -> "$22,750,000")
                    merged = re.sub(r"(\$\d+,\d+,\d+)\s+(\d{1,2})", r"\1\2", merged)
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

            # FINAL PASS: Force left alignment + single spacing on ALL cell
            # paragraphs. Must happen AFTER the merge/clear cycle above,
            # because .clear() strips paragraph-level formatting.
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        # --- Left alignment (remove old jc, add new) ---
                        p_pr = p._element.get_or_add_pPr()
                        old_jc = p_pr.find(qn("w:jc"))
                        if old_jc is not None:
                            p_pr.remove(old_jc)
                        new_jc = OxmlElement("w:jc")
                        new_jc.set(qn("w:val"), "left")
                        p_pr.append(new_jc)

                        # --- Single line spacing (APA 7 exception for tables) ---
                        old_spacing = p_pr.find(qn("w:spacing"))
                        if old_spacing is not None:
                            p_pr.remove(old_spacing)
                        spacing_el = OxmlElement("w:spacing")
                        spacing_el.set(qn("w:line"), "240")  # single spacing
                        spacing_el.set(qn("w:lineRule"), "auto")
                        spacing_el.set(qn("w:before"), "0")
                        spacing_el.set(qn("w:after"), "40")  # tiny gap between rows
                        p_pr.append(spacing_el)

                        # --- Widow/Orphan control: prevent single lines at page break ---
                        old_widow = p_pr.find(qn("w:widowControl"))
                        if old_widow is not None:
                            p_pr.remove(old_widow)
                        widow_ctrl = OxmlElement("w:widowControl")
                        p_pr.append(widow_ctrl)

                        # --- Keep lines together in paragraph (prevent line splitting) ---
                        old_keep_lines = p_pr.find(qn("w:keepLines"))
                        if old_keep_lines is not None:
                            p_pr.remove(old_keep_lines)
                        keep_lines_el = OxmlElement("w:keepLines")
                        p_pr.append(keep_lines_el)

            # Add spacing paragraph after table (APA 7: double-space gap)
            table_element = table._tbl
            spacing_p = OxmlElement("w:p")
            spacing_pPr = OxmlElement("w:pPr")
            spacing_spacing = OxmlElement("w:spacing")
            spacing_spacing.set(qn("w:line"), "480")
            spacing_spacing.set(qn("w:lineRule"), "auto")
            spacing_pPr.append(spacing_spacing)
            spacing_p.append(spacing_pPr)
            table_element.addnext(spacing_p)

    def _apply_apa_table_borders(self, table) -> None:
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

    def _set_cell_border(self, cell, **kwargs) -> None:
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

    def add_table_captions(self) -> None:
        """Add APA 7 captions to tables: 'Tabla N' (bold) + title (italic).

        APA 7 format for tables:
        - "Tabla N" in bold, left-aligned (on its own line)
        - Title in italics on the next line (same paragraph or separate)

        Strategy:
        1. Find tables and their preceding paragraphs
        2. Extract title from the paragraph before the table
        3. Insert "Tabla N" + title before each table
        """
        body = self.doc._body._element

        # Build paragraph index mapping
        para_elements = {}
        for p_idx, p in enumerate(self.doc.paragraphs):
            para_elements[p._element] = p_idx

        # Find table positions
        children = list(body)
        table_positions = []
        for pos, child in enumerate(children):
            if child.tag == qn("w:tbl"):
                table_positions.append((pos, child))

        # Get paragraph elements for title extraction
        para_by_pos = {}
        for p_idx, p in enumerate(self.doc.paragraphs):
            para_by_pos[p_idx] = p

        # Insert captions - offset increases with each insertion
        offset = 0
        for idx, (orig_pos, tbl) in enumerate(table_positions):
            table_num = idx + 1
            current_pos = orig_pos + offset

            # Try to extract title from the paragraph before the table
            # Convert CT_Tbl element to python-docx Table
            from docx.table import Table

            docx_table = Table(tbl, self.doc)
            # Try to get section heading context (look backwards for Heading style)
            # Use 'body' directly since children list is stale after insertions
            title_text = self._get_nearest_section_heading(current_pos)

            # If no section heading found, try extracting from table
            if not title_text:
                title_text = self._extract_table_title(docx_table)

            # Create caption paragraph with "Tabla N" (bold)
            caption_p = OxmlElement("w:p")
            caption_pPr = OxmlElement("w:pPr")

            # Left alignment
            jc = OxmlElement("w:jc")
            jc.set(qn("w:val"), "left")
            caption_pPr.append(jc)

            # No space after
            spacing = OxmlElement("w:spacing")
            spacing.set(qn("w:after"), "0")
            spacing.set(qn("w:line"), "240")
            spacing.set(qn("w:lineRule"), "auto")
            caption_pPr.append(spacing)

            caption_p.append(caption_pPr)

            # Run with "Tabla N" bold
            run = OxmlElement("w:r")
            rPr = OxmlElement("w:rPr")
            bold = OxmlElement("w:b")
            rPr.append(bold)
            # Font
            font = OxmlElement("w:rFonts")
            font.set(qn("w:ascii"), "Times New Roman")
            font.set(qn("w:hAnsi"), "Times New Roman")
            rPr.append(font)
            sz = OxmlElement("w:sz")
            sz.set(qn("w:val"), "24")  # 12pt
            rPr.append(sz)
            run.append(rPr)
            t = OxmlElement("w:t")
            table_config = self._get_table_config()
            caption_prefix = table_config.get("caption_prefix", "Table")
            t.text = f"{caption_prefix} {table_num}"
            run.append(t)
            caption_p.append(run)

            # Insert caption before table
            body.insert(current_pos, caption_p)
            offset += 1

            # If we have a title, add a second paragraph with the title in italics
            if title_text:
                title_p = OxmlElement("w:p")
                title_pPr = OxmlElement("w:pPr")
                jc2 = OxmlElement("w:jc")
                jc2.set(qn("w:val"), "left")
                title_pPr.append(jc2)
                spacing2 = OxmlElement("w:spacing")
                spacing2.set(qn("w:after"), "120")
                spacing2.set(qn("w:line"), "240")
                spacing2.set(qn("w:lineRule"), "auto")
                title_pPr.append(spacing2)
                title_p.append(title_pPr)

                # Run with title in italics
                title_run = OxmlElement("w:r")
                title_rPr = OxmlElement("w:rPr")
                italic = OxmlElement("w:i")
                title_rPr.append(italic)
                font2 = OxmlElement("w:rFonts")
                font2.set(qn("w:ascii"), "Times New Roman")
                font2.set(qn("w:hAnsi"), "Times New Roman")
                title_rPr.append(font2)
                sz2 = OxmlElement("w:sz")
                sz2.set(qn("w:val"), "24")
                title_rPr.append(sz2)
                title_run.append(title_rPr)
                title_t = OxmlElement("w:t")
                title_t.text = title_text
                title_t.set(qn("xml:space"), "preserve")
                title_run.append(title_t)
                title_p.append(title_run)

                # Insert title after caption
                body.insert(current_pos + 1, title_p)
                offset += 1

    def _extract_table_title(self, table) -> str:
        """Extract a descriptive title from the table content.

        APA 7: The title should describe the table content concisely.
        We try to extract it from:
        1. The first cell of the first row (if it's a header row)
        2. Or generate a generic title based on table position

        Returns the title text or empty string if not found.
        """
        try:
            if len(table.rows) < 2 or len(table.columns) < 2:
                return ""

            # Check first row - if it looks like a header (bold text, short content)
            first_row = table.rows[0]
            first_cell_text = first_row.cells[0].text.strip()

            # If the first cell is short and looks like a header label
            # (e.g., "Campo", "N", "Nombre") then use the second cell or combine cells
            short_header_indicators = [
                "n°",
                "no.",
                "campo",
                "nombre",
                "característica",
                "concepto",
                "rubro",
            ]

            if (
                first_cell_text.lower() in short_header_indicators
                or first_cell_text.lower().startswith("tabla")
            ):
                # First row is a header row, second cell might be the actual title
                if len(first_row.cells) > 1:
                    second_cell = first_row.cells[1].text.strip()
                    if second_cell and len(second_cell) < 80:
                        return second_cell
                return ""

            # If first cell has substantive content, use it as title
            if first_cell_text and 3 < len(first_cell_text) < 80:
                return first_cell_text

            # Try combining first two cells if both have content
            if len(first_row.cells) >= 2:
                second_text = first_row.cells[1].text.strip()
                if first_cell_text and second_text:
                    combined = f"{first_cell_text} - {second_text}"
                    if len(combined) < 100:
                        return combined

            return ""

        except Exception:
            return ""

    def _get_nearest_section_heading(self, table_pos: int) -> str:
        """Find the nearest section heading before a table.

        Searches backwards from table_pos in the document body for a paragraph
        with Heading style. Skips over any caption paragraphs (starting with
        "Tabla N" or "Figura N") as those belong to previous tables/figures.

        Returns the heading text or empty string if none found.
        """
        body = self.doc._body._element
        body_children = list(body)

        for i in range(table_pos - 1, -1, -1):
            if i >= len(body_children):
                continue
            elem = body_children[i]
            if elem.tag == qn("w:p"):
                p_idx_map = {p._element: idx for idx, p in enumerate(self.doc.paragraphs)}
                if elem in p_idx_map:
                    p = self.doc.paragraphs[p_idx_map[elem]]
                    style_name = p.style.name if p.style else ""
                    text = p.text.strip()

                    # Skip caption paragraphs (they belong to previous tables/figures)
                    if re.match(r"^(Tabla|Figura)\s+\d+", text):
                        continue

                    if style_name.startswith("Heading"):
                        # Clean up heading text (remove chapter numbers like "2.2 ")
                        text = re.sub(r"^\d+(\.\d+)*\s*", "", text)
                        if text:
                            return text
            # Stop if we hit another table (too far back)
            if elem.tag == qn("w:tbl"):
                break
        return ""

    def add_table_notes(self) -> None:
        """Add table notes after each table (APA 7 requirement).

        Each table gets a specific descriptive note based on its actual content,
        followed by 'Elaboración propia.' as the source attribution.
        """
        tables_list = list(self.doc.tables)
        table_descriptions = []

        for table in tables_list:
            first_row_text = ""
            if table.rows:
                first_row_text = " ".join(cell.text.strip().lower() for cell in table.rows[0].cells)

            desc = "Información técnica del proyecto."

            if "característica" in first_row_text and "especificación" in first_row_text:
                if "procesador" in first_row_text and "memoria ram" in first_row_text:
                    if table.rows and len(table.rows) > 1:
                        second_cell = (
                            table.rows[1].cells[0].text.strip().lower()
                            if table.rows[1].cells
                            else ""
                        )
                        if "desarrollador" in second_cell or "computador" in second_cell:
                            desc = "Especificaciones técnicas del computador para desarrollo."
                        elif "analista" in second_cell or "qa" in second_cell:
                            desc = (
                                "Especificaciones técnicas del computador para pruebas de calidad."
                            )
                        elif "servidor" in second_cell or "vps" in second_cell:
                            desc = "Configuración técnica del servidor virtual privado."
                        elif (
                            "móvil" in second_cell
                            or "smartphone" in second_cell
                            or "iphone" in second_cell
                        ):
                            desc = (
                                "Dispositivos móviles seleccionados para pruebas de compatibilidad."
                            )
                        else:
                            desc = "Especificaciones técnicas del equipo de hardware."
                    else:
                        desc = "Especificaciones técnicas del equipo de hardware."
                else:
                    desc = "Características técnicas del componente especificado."

            elif "software" in first_row_text and "versión" in first_row_text:
                if "función" in first_row_text or "licencia" in first_row_text:
                    if (
                        "django" in first_row_text
                        or "react" in first_row_text
                        or "framework" in first_row_text
                    ):
                        desc = (
                            "Frameworks y bibliotecas de desarrollo seleccionados para el proyecto."
                        )
                    elif "python" in first_row_text or "javascript" in first_row_text:
                        desc = "Lenguajes de programación utilizados en el desarrollo."
                    else:
                        desc = "Software de desarrollo requerido con versiones compatibles."
                elif "tipo" in first_row_text and "costo" in first_row_text:
                    if (
                        "postgresql" in first_row_text
                        or "mysql" in first_row_text
                        or "redis" in first_row_text
                    ):
                        desc = "Sistemas de gestión de bases de datos seleccionados."
                    else:
                        desc = "Software y servicios con costos asociados."

            elif "servicio" in first_row_text and "proveedor" in first_row_text:
                desc = "Infraestructura en la nube y servicios externos planificados."

            elif "rubro" in first_row_text and "costo" in first_row_text:
                all_text_lower = " ".join(
                    cell.text.strip().lower() for row in table.rows for cell in row.cells
                )
                if "herramientas" in all_text_lower or "licencias" in all_text_lower:
                    desc = "Resumen de inversiones en software y servicios del proyecto."
                elif "hardware" in all_text_lower or "servidor" in all_text_lower:
                    desc = "Resumen de inversión en equipos y servicios de infraestructura."
                else:
                    desc = "Resumen de inversiones en software y servicios del proyecto."

            elif "componente" in first_row_text and "porcentaje" in first_row_text:
                desc = (
                    "Componentes del modelo de costos AIU (Administración, Imprevistos, Utilidad)."
                )

            elif "rol" in first_row_text and "dedicación" in first_row_text:
                desc = "Estructura del equipo de desarrollo con roles y dedicación temporal."

            elif "concepto" in first_row_text and "valor" in first_row_text:
                all_text = " ".join(
                    cell.text.strip().lower() for row in table.rows for cell in row.cells
                )
                # Check for IVA first (most specific for budget summary with taxes)
                if "iva" in all_text:
                    desc = "Resumen del presupuesto total del proyecto con impuestos aplicables."
                elif "total costos directos" in all_text and "aiu" not in all_text:
                    desc = "Desglose de costos directos del proyecto de desarrollo."
                elif "aiu" in all_text or "subtotal" in all_text:
                    desc = "Componentes del presupuesto con aplicación del modelo AIU."
                else:
                    desc = "Conceptos y valores del presupuesto del proyecto."

            elif "n°" in first_row_text or "º" in first_row_text:
                all_text = " ".join(
                    cell.text.strip().lower() for row in table.rows for cell in row.cells
                )
                if COMPANY_KEYWORDS.intersection(all_text.split()):
                    if "criterio" in all_text or "peso" in all_text or "funcional" in all_text:
                        desc = (
                            "Matriz de evaluación técnica y ponderación de criterios por proveedor."
                        )
                    else:
                        desc = "Comparación de costos directos entre proveedores evaluados."
                elif "backend" in all_text or "frontend" in all_text or "panel" in all_text:
                    desc = "Desglose de costos por módulo de desarrollo y servicio."
                elif "hardware" in all_text:
                    desc = "Resumen de inversión en equipos de hardware."
                else:
                    desc = "Detalle de costos y Rubros del presupuesto."

            else:
                desc = "Información técnica del proyecto."

            table_descriptions.append(desc)

        for i, table in enumerate(tables_list):
            parent = table._tbl.getparent()
            if parent is None:
                continue

            table_idx = parent.index(table._tbl)

            nota_p = OxmlElement("w:p")
            nota_pPr = OxmlElement("w:pPr")
            nota_spacing = OxmlElement("w:spacing")
            nota_spacing.set(qn("w:after"), "0")
            nota_pPr.append(nota_spacing)
            nota_p.append(nota_pPr)

            nota_r1 = OxmlElement("w:r")
            nota_rPr1 = OxmlElement("w:rPr")
            nota_i1 = OxmlElement("w:i")
            nota_rPr1.append(nota_i1)
            nota_sz1 = OxmlElement("w:sz")
            nota_sz1.set(qn("w:val"), "24")
            nota_rPr1.append(nota_sz1)
            nota_r1.append(nota_rPr1)
            nota_t1 = OxmlElement("w:t")
            nota_t1.text = "Nota. "
            nota_r1.append(nota_t1)
            nota_p.append(nota_r1)

            nota_r2 = OxmlElement("w:r")
            nota_rPr2 = OxmlElement("w:rPr")
            nota_sz2 = OxmlElement("w:sz")
            nota_sz2.set(qn("w:val"), "24")
            nota_rPr2.append(nota_sz2)
            nota_r2.append(nota_rPr2)
            nota_t2 = OxmlElement("w:t")
            nota_t2.text = (
                table_descriptions[i]
                if i < len(table_descriptions)
                else "Información técnica del proyecto."
            )
            nota_r2.append(nota_t2)
            nota_p.append(nota_r2)

            nota_r3 = OxmlElement("w:r")
            nota_rPr3 = OxmlElement("w:rPr")
            nota_sz3 = OxmlElement("w:sz")
            nota_sz3.set(qn("w:val"), "24")
            nota_rPr3.append(nota_sz3)
            nota_r3.append(nota_rPr3)
            nota_t3 = OxmlElement("w:t")
            table_config = self._get_table_config()
            note_suffix = table_config.get("note_suffix", " Elaboración propia.")
            nota_t3.text = f" {note_suffix}"
            nota_r3.append(nota_t3)
            nota_p.append(nota_r3)

            parent.insert(table_idx + 1, nota_p)

    def add_table_header_bold(self) -> None:
        """Set bold on all table header rows (APA 7 requirement).

        This is done at the END of process() because other methods may rebuild
        table XML and lose the bold setting if applied earlier.
        """
        for table in self.doc.tables:
            for row in table.rows[:1]:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.bold = True

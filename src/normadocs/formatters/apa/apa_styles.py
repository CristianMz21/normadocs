"""APA styles creation and font handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

if TYPE_CHECKING:
    from docx.document import Document as DocType
    from docx.text.paragraph import Paragraph as ParagraphType


class APAStylesHandler:
    """Handles creation and application of APA 7th Edition styles.

    Creates and applies styles for Normal, Heading 1-6, and other
    paragraph styles with correct fonts, sizes, and spacing per APA 7.

    Args:
        doc: The python-docx Document object.
        config: Optional configuration dictionary.
    """

    def __init__(self, doc: DocType, config: dict[str, Any] | None = None) -> None:
        """Initialize APAStylesHandler.

        Args:
            doc: The python-docx Document object.
            config: Optional configuration dictionary.
        """
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_font_name(self, key: str = "body") -> str:
        """Get the body font name from config.

        Returns:
            Font name (APA default is Times New Roman).
        """
        fonts: dict[str, Any] = {}
        return cast(
            str, self.config.get("fonts", fonts).get(key, {}).get("name", "Times New Roman")
        )

    def _get_font_size(self, key: str = "body") -> int:
        """Get the body font size from config.

        Returns:
            Font size in half-points (APA default is 24 = 12pt).
        """
        fonts: dict[str, Any] = {}
        return cast(int, self.config.get("fonts", fonts).get(key, {}).get("size", 12))

    def _get_spacing_line(self) -> str:
        """Get line spacing from config.

        Returns:
            Line spacing value (APA default is double).
        """
        spacing: dict[str, str] = {"line": "double"}
        return cast(str, self.config.get("spacing", spacing).get("line", "double"))

    def create_styles(self) -> None:
        """
        Configure Normal, Headings (5 levels per APA 7), and other styles.

        APA 7 Heading Levels:
        - Level 1: Centered, Bold, Title Case (new paragraph)
        - Level 2: Left-aligned, Bold, Title Case (new paragraph)
        - Level 3: Left-aligned, Bold, Italic, Title Case (new paragraph)
        - Level 4: Indented, Bold, Title Case, ends with period (same line)
        - Level 5: Indented, Bold, Italic, Title Case, ends with period (same line)
        """
        styles = self.doc.styles

        body_font = self._get_font_name("body")
        body_size = self._get_font_size("body")
        spacing_line = self._get_spacing_line()
        line_spacing = (
            WD_LINE_SPACING.DOUBLE if spacing_line == "double" else WD_LINE_SPACING.ONE_POINT_FIVE
        )

        # Normal - APA 7: Times New Roman 12pt, double spacing, left aligned
        normal = styles["Normal"]
        self._apply_font_style(normal, font_name=body_font, size=body_size)
        pf = normal.paragraph_format
        pf.line_spacing_rule = line_spacing
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Body Text
        for style_name in ["Body Text", "First Paragraph"]:
            try:
                style = styles[style_name]
                self._apply_font_style(style, font_name=body_font, size=body_size)
                style.paragraph_format.line_spacing_rule = line_spacing
                style.paragraph_format.first_line_indent = Inches(0.5)
                style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            except KeyError:
                pass

        # APA 7 Headings - 5 levels
        # Level 1: Centered, Bold, Title Case (text starts new paragraph)
        configs = {
            "Heading 1": {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.CENTER,
                "indent": False,
                "ends_period": False,
            },
            # Level 2: Left-aligned, Bold, Title Case (text starts new paragraph)
            "Heading 2": {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": False,
                "ends_period": False,
            },
            # Level 3: Left-aligned, Bold, Italic, Title Case (text starts new paragraph)
            "Heading 3": {
                "bold": True,
                "italic": True,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": False,
                "ends_period": False,
            },
            # Level 4: Indented, Bold, Title Case, ends with period (same line)
            "Heading 4": {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": Inches(0.5),
                "ends_period": True,
            },
            # Level 5: Indented, Bold, Italic, Title Case, ends with period (same line)
            "Heading 5": {
                "bold": True,
                "italic": True,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": Inches(0.5),
                "ends_period": True,
            },
        }
        for sn, cfg in configs.items():
            try:
                h = styles[sn]
                self._apply_font_style(
                    h,
                    font_name=body_font,
                    size=body_size,
                    bold=bool(cfg["bold"]),
                    italic=bool(cfg["italic"]),
                )
                h.paragraph_format.alignment = cfg["align"]
                h.paragraph_format.line_spacing_rule = line_spacing
                h.paragraph_format.page_break_before = False
                if cfg["indent"]:
                    h.paragraph_format.first_line_indent = Inches(0.5)
                if cfg["ends_period"]:
                    # Ensure text ends with period
                    pass
            except KeyError:
                pass

        # Override Compact style (used by Pandoc for table cells & lists)
        # Must have single spacing + left alignment for APA tables
        ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for style_el in self.doc.styles.element.findall(f"{{{ns}}}style"):
            style_id = style_el.get(f"{{{ns}}}styleId", "")
            if style_id == "Compact":
                # Replace pPr with single spacing + left alignment
                old_pPr = style_el.find(f"{{{ns}}}pPr")
                if old_pPr is not None:
                    style_el.remove(old_pPr)
                pPr = OxmlElement("w:pPr")
                spacing = OxmlElement("w:spacing")
                spacing.set(qn("w:line"), "240")
                spacing.set(qn("w:lineRule"), "auto")
                spacing.set(qn("w:before"), "36")
                spacing.set(qn("w:after"), "36")
                pPr.append(spacing)
                jc = OxmlElement("w:jc")
                jc.set(qn("w:val"), "left")
                pPr.append(jc)
                # Remove first-line indent inherited from BodyText
                ind = OxmlElement("w:ind")
                ind.set(qn("w:firstLine"), "0")
                pPr.append(ind)
                style_el.append(pPr)
                break

        # Remove Pandoc Table Style borders
        self._neutralize_table_style()

    def _neutralize_table_style(self) -> None:
        """Remove borders from 'Table' style and force left-alignment + single spacing."""
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

                # Add paragraph properties to the Table style (left align + single spacing)
                # This is authoritative for LibreOffice's style inheritance
                old_pPr = style_el.find(f"{{{ns}}}pPr")
                if old_pPr is not None:
                    style_el.remove(old_pPr)
                pPr = OxmlElement("w:pPr")
                jc = OxmlElement("w:jc")
                jc.set(qn("w:val"), "left")
                pPr.append(jc)
                spacing = OxmlElement("w:spacing")
                spacing.set(qn("w:line"), "240")
                spacing.set(qn("w:lineRule"), "auto")
                spacing.set(qn("w:before"), "0")
                spacing.set(qn("w:after"), "0")
                pPr.append(spacing)
                style_el.append(pPr)

                # Add run properties (font) to the Table style
                old_rPr = style_el.find(f"{{{ns}}}rPr")
                if old_rPr is not None:
                    style_el.remove(old_rPr)
                rPr = OxmlElement("w:rPr")
                rFonts = OxmlElement("w:rFonts")
                rFonts.set(qn("w:ascii"), self._get_font_name("body"))
                rFonts.set(qn("w:hAnsi"), self._get_font_name("body"))
                rPr.append(rFonts)
                sz = OxmlElement("w:sz")
                sz.set(
                    qn("w:val"), str(self._get_font_size("body") * 2)
                )  # body_size in points, stored as half-points
                rPr.append(sz)
                style_el.append(rPr)

                # Fix the firstRow tblStylePr: change vAlign from bottom to top
                for tsp in style_el.findall(f"{{{ns}}}tblStylePr"):
                    if tsp.get(f"{{{ns}}}type") == "firstRow":
                        tcPr = tsp.find(f"{{{ns}}}tcPr")
                        if tcPr is not None:
                            old_va = tcPr.find(f"{{{ns}}}vAlign")
                            if old_va is not None:
                                tcPr.remove(old_va)
                            va = OxmlElement("w:vAlign")
                            va.set(qn("w:val"), "top")
                            tcPr.append(va)

    def _apply_font_style(
        self,
        style_or_run: Any,
        font_name: str | None = None,
        size: int | None = None,
        bold: bool | None = None,
        italic: bool | None = None,
        color_rgb: tuple[int, int, int] | None = None,
    ) -> None:
        """Apply font style settings to a style or run element.

        Args:
            style_or_run: The style or run element to apply formatting to.
            font_name: Font name to apply (optional).
            size: Font size in half-points (optional).
            bold: Whether to apply bold (optional).
            italic: Whether to apply italic (optional).
            color_rgb: RGB color tuple (optional).
        """
        font = style_or_run.font
        if font_name is not None:
            font.name = font_name
        if size is not None:
            font.size = Pt(size)
        if color_rgb is not None and hasattr(font.color, "rgb"):
            font.color.rgb = RGBColor(*color_rgb)
        if bold is not None:
            font.bold = bold
        if italic is not None:
            font.italic = italic

    def _apply_font_to_paragraph(
        self, paragraph: ParagraphType, font_size: int | None = None
    ) -> None:
        """Apply font style to all runs in a paragraph.

        Args:
            paragraph: The paragraph to apply formatting to.
            font_size: Font size to apply (optional).
        """
        size = 12 if font_size is None else font_size
        for run in paragraph.runs:
            self._apply_font_style(run, size=size)

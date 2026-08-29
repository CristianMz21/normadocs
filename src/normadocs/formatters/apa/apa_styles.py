"""APA styles creation and font handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from ...config import (
    BODY_TEXT_STYLE,
    COMPACT_STYLE,
    DEFAULT_BODY_FONT,
    HEADING_1_STYLE,
    HEADING_2_STYLE,
    HEADING_3_STYLE,
    HEADING_4_STYLE,
    HEADING_5_STYLE,
    NORMAL_STYLE,
    W_AFTER,
    W_BEFORE,
    W_LINE,
    W_LINE_RULE,
    W_SPACING,
    W_VAL,
)
from ...utils.docx_helpers import paragraph_style

if TYPE_CHECKING:
    from docx.document import Document as DocType
    from docx.text.paragraph import Paragraph as ParagraphType

_BODY_KEY = "body"
_DOUBLE = "double"
_NS_MAIN = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


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

    def _get_font_name(self, key: str = _BODY_KEY) -> str:
        """Get the body font name from config.

        Returns:
            Font name (APA default is Times New Roman).
        """
        fonts: dict[str, Any] = {}
        return cast(
            str, self.config.get("fonts", fonts).get(key, {}).get("name", DEFAULT_BODY_FONT)
        )

    def _get_font_size(self, key: str = _BODY_KEY) -> int:
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
        spacing: dict[str, str] = {"line": _DOUBLE}
        return cast(str, self.config.get("spacing", spacing).get("line", _DOUBLE))

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
        body_font = self._get_font_name(_BODY_KEY)
        body_size = self._get_font_size(_BODY_KEY)
        line_spacing = self._resolve_line_spacing(self._get_spacing_line())
        self._configure_normal(body_font, body_size, line_spacing)
        self._configure_body_text(body_font, body_size, line_spacing)
        self._configure_headings(body_font, body_size, line_spacing)
        self._configure_compact_style()
        self._neutralize_table_style()

    def _resolve_line_spacing(self, spacing_line: str) -> WD_LINE_SPACING:
        """Resolve spacing line string to enum."""
        if spacing_line == _DOUBLE:
            return WD_LINE_SPACING.DOUBLE
        return WD_LINE_SPACING.ONE_POINT_FIVE

    def _configure_normal(
        self, body_font: str, body_size: int, line_spacing: WD_LINE_SPACING
    ) -> None:
        """Configure Normal style."""
        normal = paragraph_style(self.doc.styles, NORMAL_STYLE)
        self._apply_font_style(normal, font_name=body_font, size=body_size)
        pf = normal.paragraph_format
        pf.line_spacing_rule = line_spacing
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def _configure_body_text(
        self, body_font: str, body_size: int, line_spacing: WD_LINE_SPACING
    ) -> None:
        """Configure Body Text and First Paragraph styles."""
        for style_name in [BODY_TEXT_STYLE, "First Paragraph"]:
            try:
                style = paragraph_style(self.doc.styles, style_name)
                self._apply_font_style(style, font_name=body_font, size=body_size)
                style.paragraph_format.line_spacing_rule = line_spacing
                style.paragraph_format.first_line_indent = Inches(0.5)
                style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            except KeyError:
                continue

    def _configure_headings(
        self, body_font: str, body_size: int, line_spacing: WD_LINE_SPACING
    ) -> None:
        """Configure APA 7 heading styles."""
        configs = self._heading_configs()
        for sn, cfg in configs.items():
            try:
                h = paragraph_style(self.doc.styles, sn)
                self._apply_heading_style(h, body_font, body_size, cfg, line_spacing)
            except KeyError:
                continue

    def _heading_configs(self) -> dict[str, dict[str, Any]]:
        """Return heading configuration map."""
        return {
            HEADING_1_STYLE: {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.CENTER,
                "indent": False,
            },
            HEADING_2_STYLE: {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": False,
            },
            HEADING_3_STYLE: {
                "bold": True,
                "italic": True,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": False,
            },
            HEADING_4_STYLE: {
                "bold": True,
                "italic": False,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": Inches(0.5),
            },
            HEADING_5_STYLE: {
                "bold": True,
                "italic": True,
                "align": WD_ALIGN_PARAGRAPH.LEFT,
                "indent": Inches(0.5),
            },
        }

    def _apply_heading_style(
        self,
        heading: Any,
        body_font: str,
        body_size: int,
        cfg: dict[str, Any],
        line_spacing: WD_LINE_SPACING,
    ) -> None:
        """Apply style to a single heading."""
        self._apply_font_style(
            heading,
            font_name=body_font,
            size=body_size,
            bold=bool(cfg["bold"]),
            italic=bool(cfg["italic"]),
        )
        heading.paragraph_format.alignment = cfg["align"]
        heading.paragraph_format.line_spacing_rule = line_spacing
        heading.paragraph_format.page_break_before = False
        indent = cfg["indent"]
        if indent:
            heading.paragraph_format.first_line_indent = indent

    def _configure_compact_style(self) -> None:
        """Override Compact style for table cells and lists."""
        ns = _NS_MAIN
        for style_el in self.doc.styles.element.findall(f"{{{ns}}}style"):
            style_id = style_el.get(f"{{{ns}}}styleId", "")
            if style_id != COMPACT_STYLE:
                continue
            self._replace_compact_ppr(style_el, ns)
            break

    def _replace_compact_ppr(self, style_el: Any, ns: str) -> None:
        """Replace Compact paragraph properties."""
        old = style_el.find(f"{{{ns}}}pPr")
        if old is not None:
            style_el.remove(old)
        p_pr = OxmlElement("w:pPr")
        spacing = OxmlElement(W_SPACING)
        spacing.set(qn(W_LINE), "240")
        spacing.set(qn(W_LINE_RULE), "auto")
        spacing.set(qn(W_BEFORE), "36")
        spacing.set(qn(W_AFTER), "36")
        p_pr.append(spacing)
        jc = OxmlElement("w:jc")
        jc.set(qn(W_VAL), "left")
        p_pr.append(jc)
        ind = OxmlElement("w:ind")
        ind.set(qn("w:firstLine"), "0")
        p_pr.append(ind)
        style_el.append(p_pr)

    def _neutralize_table_style(self) -> None:
        """Remove borders from 'Table' style and force left-alignment + single spacing."""
        ns = _NS_MAIN
        for style_el in self.doc.styles.element.findall(f"{{{ns}}}style"):
            style_id = style_el.get(f"{{{ns}}}styleId", "")
            if style_id != "Table":
                continue
            self._neutralize_table_borders(style_el, ns)
            self._neutralize_table_ppr(style_el, ns)
            self._neutralize_table_rpr(style_el)
            self._fix_first_row_v_align(style_el, ns)

    def _neutralize_table_borders(self, style_el: Any, ns: str) -> None:
        """Remove and reset table borders to none."""
        tbl_pr_el = style_el.find(f"{{{ns}}}tblPr")
        if tbl_pr_el is None:
            return
        for old_b in tbl_pr_el.findall(f"{{{ns}}}tblBorders"):
            tbl_pr_el.remove(old_b)
        brd = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{edge}")
            e.set(qn(W_VAL), "none")
            e.set(qn("w:sz"), "0")
            e.set(qn("w:space"), "0")
            brd.append(e)
        tbl_pr_el.append(brd)

    def _neutralize_table_ppr(self, style_el: Any, ns: str) -> None:
        """Set left alignment and single spacing on Table style."""
        old = style_el.find(f"{{{ns}}}pPr")
        if old is not None:
            style_el.remove(old)
        p_pr = OxmlElement("w:pPr")
        jc = OxmlElement("w:jc")
        jc.set(qn(W_VAL), "left")
        p_pr.append(jc)
        spacing = OxmlElement(W_SPACING)
        spacing.set(qn(W_LINE), "240")
        spacing.set(qn(W_LINE_RULE), "auto")
        spacing.set(qn(W_BEFORE), "0")
        spacing.set(qn(W_AFTER), "0")
        p_pr.append(spacing)
        style_el.append(p_pr)

    def _neutralize_table_rpr(self, style_el: Any) -> None:
        """Set font on Table style."""
        ns = _NS_MAIN
        old = style_el.find(f"{{{ns}}}rPr")
        if old is not None:
            style_el.remove(old)
        r_pr = OxmlElement("w:rPr")
        r_fonts = OxmlElement("w:rFonts")
        font_name = self._get_font_name(_BODY_KEY)
        r_fonts.set(qn("w:ascii"), font_name)
        r_fonts.set(qn("w:hAnsi"), font_name)
        r_pr.append(r_fonts)
        sz = OxmlElement("w:sz")
        sz.set(qn(W_VAL), str(self._get_font_size(_BODY_KEY) * 2))
        r_pr.append(sz)
        style_el.append(r_pr)

    def _fix_first_row_v_align(self, style_el: Any, ns: str) -> None:
        """Fix firstRow vAlign to top."""
        for tsp in style_el.findall(f"{{{ns}}}tblStylePr"):
            if tsp.get(f"{{{ns}}}type") != "firstRow":
                continue
            tc_pr = tsp.find(f"{{{ns}}}tcPr")
            if tc_pr is None:
                continue
            old_va = tc_pr.find(f"{{{ns}}}vAlign")
            if old_va is not None:
                tc_pr.remove(old_va)
            va = OxmlElement("w:vAlign")
            va.set(qn(W_VAL), "top")
            tc_pr.append(va)

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

"""APA 7 display-equation formatting.

Pandoc emits display math (``$$…$$``) as an OMML ``m:oMathPara`` element in
its own paragraph. APA 7 requires display equations to be centered with a
consecutive equation number, in parentheses, aligned to the right margin.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches

from ...config import DEFAULT_BODY_FONT, W_VAL

if TYPE_CHECKING:
    from docx.document import Document as DocType
    from docx.text.paragraph import Paragraph as ParagraphType


class APAEquationsHandler:
    """Handles display equations per APA 7th Edition."""

    def __init__(self, doc: DocType, config: dict[str, Any] | None = None) -> None:
        """Initialize APAEquationsHandler.

        Args:
            doc: The python-docx Document object.
            config: Optional configuration dictionary.
        """
        self.doc = doc
        self.config = config if config is not None else {}

    def get_config(self, *keys: str, default: Any = None) -> Any:
        """Get nested config value via dot-notation keys."""
        value: Any = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def _get_equations_config(self) -> dict[str, Any]:
        """Get equation configuration with APA defaults."""
        default: dict[str, Any] = {
            "numbering": True,
            "format": "({n})",
            "center_tab_inches": 3.25,
            "right_tab_inches": 6.5,
        }
        return cast(dict[str, Any], self.get_config("equations", default=default))

    def format_equations(self) -> None:
        """Number and lay out display equations per APA 7.

        Each pure-equation paragraph is rebuilt with the canonical Word/APA
        layout ``[tab] equation [tab] (N)``: a center tab stop places the
        equation on the middle of the text column and a right tab stop puts
        the equation number on the right margin.
        """
        eq_config = self._get_equations_config()
        numbering = bool(eq_config.get("numbering", True))
        number_format = cast(str, eq_config.get("format", "({n})"))
        center_tab = cast(float, eq_config.get("center_tab_inches", 3.25))
        right_tab = cast(float, eq_config.get("right_tab_inches", 6.5))

        number = 0
        for p in self.doc.paragraphs:
            math_paras = p._element.findall(f".//{qn('m:oMathPara')}")
            if not math_paras:
                continue
            # Mixed paragraphs (text + display math) keep pandoc's layout
            if p.text.strip():
                continue

            number += 1
            math_el = self._unwrap_display_math(p)
            if math_el is None:
                continue

            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Inches(0)
            tab_stops = p.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(center_tab), WD_TAB_ALIGNMENT.CENTER)
            tab_stops.add_tab_stop(Inches(right_tab), WD_TAB_ALIGNMENT.RIGHT)

            lead_tab = self._make_tab_run()
            math_el.addprevious(lead_tab)

            if numbering:
                label_run = self._make_number_run(number_format.format(n=number))
                math_el.addnext(label_run)

    def _unwrap_display_math(self, p: ParagraphType) -> Any:
        """Replace each m:oMathPara wrapper with its inline m:oMath child.

        Returns the first unwrapped m:oMath element, or None if the paragraph
        held no convertible math.
        """
        first: Any = None
        for wrapper in p._element.findall(f".//{qn('m:oMathPara')}"):
            math_el = wrapper.find(qn("m:oMath"))
            parent = wrapper.getparent()
            if math_el is None or parent is None:
                continue
            parent.replace(wrapper, math_el)
            if first is None:
                first = math_el
        return first

    @staticmethod
    def _make_tab_run() -> Any:
        """Build an empty run holding a single tab character."""
        run = OxmlElement("w:r")
        run.append(OxmlElement("w:tab"))
        return run

    @staticmethod
    def _make_number_run(label: str) -> Any:
        """Build a Times New Roman 12pt run with tab + equation number text."""
        run = OxmlElement("w:r")
        rpr = OxmlElement("w:rPr")
        fonts = OxmlElement("w:rFonts")
        fonts.set(qn("w:ascii"), DEFAULT_BODY_FONT)
        fonts.set(qn("w:hAnsi"), DEFAULT_BODY_FONT)
        rpr.append(fonts)
        size = OxmlElement("w:sz")
        size.set(qn(W_VAL), "24")
        rpr.append(size)
        run.append(rpr)
        run.append(OxmlElement("w:tab"))
        text = OxmlElement("w:t")
        text.set(qn("xml:space"), "preserve")
        text.text = label
        run.append(text)
        return run

"""APA page layout and page number handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

if TYPE_CHECKING:
    from docx.document import Document as DocType
    from docx.section import Section as SectionType


class APAPageHandler:
    """Handles page layout and page numbers per APA 7th Edition.

    Sets up page margins, headers with page numbers, and section
    page breaks according to APA 7th Edition requirements.

    Args:
        doc: The python-docx Document object.
        config: Optional configuration dictionary.
    """

    def __init__(self, doc: DocType, config: dict[str, Any] | None = None) -> None:
        """Initialize APAPageHandler.

        Args:
            doc: The python-docx Document object.
            config: Optional configuration dictionary.
        """
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_margins(self) -> dict[str, float]:
        """Get margins from config with defaults."""
        margins = self.config.get("margins", {})
        return {
            "top": margins.get("top", 1.0),
            "bottom": margins.get("bottom", 1.0),
            "left": margins.get("left", 1.0),
            "right": margins.get("right", 1.0),
            "unit": margins.get("unit", "inches"),
        }

    def _margin_to_inches(self, value: float, unit: str) -> Inches | Cm:
        """Convert margin value to inches based on unit.

        Args:
            value: The margin value.
            unit: The unit type ("inches", "cm", or "Emu").

        Returns:
            The value converted to inches.
        """
        if unit == "cm":
            return Cm(value)
        return Inches(value)

    def setup_page_layout(self) -> None:
        """Set margins and add page numbers top-right."""
        margins = self._get_margins()
        unit = str(margins["unit"])

        for section in self.doc.sections:
            section.page_height = Inches(11)
            section.page_width = Inches(8.5)
            section.left_margin = self._margin_to_inches(margins["left"], unit)
            section.right_margin = self._margin_to_inches(margins["right"], unit)
            section.top_margin = self._margin_to_inches(margins["top"], unit)
            section.bottom_margin = self._margin_to_inches(margins["bottom"], unit)

            # Disable separate first-page header/footer
            section.different_first_page_header_footer = False

            # Clear footers completely to prevent Pandoc page numbers at bottom
            footer = section.footer
            footer.is_linked_to_previous = False
            for p in footer.paragraphs:
                p.clear()
                # Remove ALL child elements (runs, field codes, pPr, etc.)
                for child in list(p._element):
                    p._element.remove(child)
            # Also set footer distance to zero to suppress any residual space
            sectPr = section._sectPr
            existing_pgMar = sectPr.find(qn("w:pgMar"))
            if existing_pgMar is not None:
                existing_pgMar.set(qn("w:footer"), "0")

            # Remove the footerReference entirely to prevent LibreOffice
            # from rendering any footer content
            for fref in list(sectPr.findall(qn("w:footerReference"))):
                sectPr.remove(fref)

            self._add_page_number(section)

    def _add_page_number(self, section: SectionType) -> None:
        """Add page number top-right in header."""
        header = section.header
        header.is_linked_to_previous = False

        # Clear existing header text
        for p in header.paragraphs:
            p.clear()

        hp = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Build PAGE field with begin/separate/end sequence
        # (LibreOffice requires the 'separate' marker to render page numbers)
        run_begin = hp.add_run()
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        run_begin._r.append(fld_begin)
        run_begin.font.name = "Times New Roman"
        run_begin.font.size = Pt(12)

        run_instr = hp.add_run()
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " PAGE "
        run_instr._r.append(instr)
        run_instr.font.name = "Times New Roman"
        run_instr.font.size = Pt(12)

        run_sep = hp.add_run()
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        run_sep._r.append(fld_sep)
        run_sep.font.name = "Times New Roman"
        run_sep.font.size = Pt(12)

        # Placeholder text (will be replaced by actual page number)
        run_num = hp.add_run("1")
        run_num.font.name = "Times New Roman"
        run_num.font.size = Pt(12)

        run_end = hp.add_run()
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        run_end._r.append(fld_end)
        run_end.font.name = "Times New Roman"
        run_end.font.size = Pt(12)

        # Strip excessive paragraphs in header
        while len(header.paragraphs) > 1:
            p_elem = header.paragraphs[-1]._element
            p_elem.getparent().remove(p_elem)

    def add_section_page_breaks(self) -> None:
        """Add page breaks before Conclusions and Referencias sections."""
        # Sections that need to start on a new page
        new_page_sections = ["Conclusiones", "Referencias"]

        # Find headings and add page breaks before them
        for _i, p in enumerate(self.doc.paragraphs):
            if p.style and p.style.name.startswith("Heading"):
                # Check if this heading is one of our target sections
                heading_text = p.text.strip()
                for section in new_page_sections:
                    if heading_text.lower() == section.lower():
                        # Create a page break using br element
                        br = OxmlElement("w:br")
                        br.set(qn("w:type"), "page")
                        p._element.addprevious(br)
                        break

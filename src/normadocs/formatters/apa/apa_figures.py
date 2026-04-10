"""APA figure formatting and captions."""

import re
from typing import Any

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from lxml.etree import Element


class APAFiguresHandler:
    """Handles figure formatting and captions per APA 7th Edition."""

    def __init__(self, doc, config: dict[str, Any] | None = None):
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_figure_config(self) -> dict[str, Any]:
        """Get figure configuration from config with defaults."""
        return self.config.get(
            "figures",
            {
                "caption_prefix": "Figura",
                "title_above": True,
                "nota_prefix": "Nota.",
            },
        )

    def _get_body_font(self) -> str:
        """Get body font name from config."""
        return self.config.get("fonts", {}).get("body", {}).get("name", "Times New Roman")

    def _apply_font_style(self, run, bold: bool = False, italic: bool = False) -> None:
        """Apply font style to a run (helper for this handler)."""
        from .apa_styles import APAStylesHandler

        handler = APAStylesHandler(self.doc)
        handler._apply_font_style(run, bold=bold, italic=italic)

    def _make_figure_paragraph(
        self, text: str, bold: bool = False, italic: bool = False, space_after: str = "0"
    ) -> Element:
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

    def format_figures(self) -> None:
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

            # Scale oversized images to fit within the usable page area.
            # Inline images in DOCX CANNOT span pages — LibreOffice clips
            # them at the page boundary. We must always scale to fit.
            # Max usable: 6.5in wide x 8.5in tall (leaving room for captions).
            max_w = Inches(6.5)
            max_h = Inches(8.5)
            drawings = p._element.findall(f".//{{{ns_wp}}}inline") + p._element.findall(
                f".//{{{ns_wp}}}anchor"
            )
            for d in drawings:
                extent = d.find(f"{{{ns_wp}}}extent")
                if extent is None:
                    continue
                cx = int(extent.get("cx", 0))
                cy = int(extent.get("cy", 0))
                if cx == 0 or cy == 0:
                    continue

                scale = 1.0
                if cx > max_w:
                    scale = min(scale, max_w / cx)
                if cy > max_h:
                    scale = min(scale, max_h / cy)

                if scale < 1.0:
                    new_cx = int(cx * scale)
                    new_cy = int(cy * scale)
                    extent.set("cx", str(new_cx))
                    extent.set("cy", str(new_cy))

                    # Also update the a:ext in the spPr (shape properties)
                    ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
                    for ext_el in d.iter(f"{{{ns_a}}}ext"):
                        old_cx = int(ext_el.get("cx", 0))
                        old_cy = int(ext_el.get("cy", 0))
                        if old_cx > 0:
                            ext_el.set("cx", str(int(old_cx * scale)))
                        if old_cy > 0:
                            ext_el.set("cy", str(int(old_cy * scale)))

    def add_figure_captions(self) -> None:
        """Add APA 7 captions to figures: 'Figura N' (bold) + title (italic).

        Finds images and their titles from Pandoc output, creates proper captions.
        The title comes AFTER the image in Pandoc output (from ![Title](path) syntax).
        """
        body = self.doc._body._element
        children = list(body)

        # Find all image paragraphs
        image_positions = []

        for i, child in enumerate(children):
            if child.tag == qn("w:p"):
                drawings = child.findall(f".//{qn('w:drawing')}")
                if drawings:
                    image_positions.append(i)

        # Get all paragraph indices and their elements
        para_elements = {}
        for p_idx, para in enumerate(self.doc.paragraphs):
            para_elements[para._element] = p_idx

        # Process each image - search FORWARD to find title after image
        for img_idx, img_pos in enumerate(image_positions, start=1):
            title_para = None
            title_para_idx = None
            title_text = None

            # Search forward from image for the title (paragraph after image)
            # Pandoc structure: image -> title (from ![Title](path)) -> Nota
            for j in range(img_pos + 1, len(children)):
                next_elem = children[j]
                if next_elem.tag == qn("w:p"):
                    para_idx = para_elements.get(next_elem)
                    if para_idx is not None:
                        text = self.doc.paragraphs[para_idx].text.strip()

                        # Skip empty paragraphs
                        if not text:
                            continue

                        # Check if this is "Nota" - if so, title is the paragraph before it
                        if text.lower().startswith("nota"):
                            if para_idx > 1:
                                prev_text = self.doc.paragraphs[para_idx - 1].text.strip()
                                # Make sure it's a valid title (not a list, not a heading, not empty)
                                if (
                                    prev_text
                                    and not prev_text.startswith("•")
                                    and not prev_text.startswith("-")
                                    and not prev_text.startswith("#")
                                    and not prev_text.startswith("Figura ")
                                ):
                                    title_text = prev_text
                                    title_para_idx = para_idx - 1
                                    title_para = self.doc.paragraphs[para_idx - 1]
                            break

                        # Also check if text starts with "Figura N" - that's the original title from markdown
                        if re.match(r"^Figura\s+\d+", text):
                            # This is the original title - extract the actual title
                            match = re.match(r"^Figura\s+\d+\s+(.+)$", text)
                            if match:
                                title_text = match.group(1).strip()
                                title_para_idx = para_idx
                                title_para = self.doc.paragraphs[para_idx]
                            break

            # Create "Figura N. Title" caption with proper formatting
            if title_text:
                # Create new caption paragraph BEFORE the image
                new_p = self.doc.add_paragraph()
                body.remove(new_p._element)
                body.insert(img_pos, new_p._element)

                fig_config = self._get_figure_config()
                caption_prefix = fig_config.get("caption_prefix", "Figura")
                run1 = new_p.add_run(f"{caption_prefix} {img_idx}. ")
                run1.bold = True
                self._apply_font_style(run1, bold=True)

                run2 = new_p.add_run(title_text)
                run2.italic = True
                self._apply_font_style(run2, italic=True)

                new_p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                # Remove the original title paragraph if it exists
                if title_para is not None and title_para_idx is not None:
                    try:
                        # Only remove if it's a different paragraph
                        if title_para_idx != img_pos:
                            title_para._element.getparent().remove(title_para._element)
                    except Exception:  # nosec: B110 - XML element removal is best-effort
                        pass
            else:
                # No title found, just create "Figura N"
                new_p = self.doc.add_paragraph()
                body.remove(new_p._element)
                body.insert(img_pos, new_p._element)

                fig_config = self._get_figure_config()
                caption_prefix = fig_config.get("caption_prefix", "Figura")
                run1 = new_p.add_run(f"{caption_prefix} {img_idx}")
                run1.bold = True
                self._apply_font_style(run1, bold=True)

                new_p.alignment = WD_ALIGN_PARAGRAPH.LEFT

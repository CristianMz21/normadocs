"""APA figure formatting and captions."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, cast

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from lxml.etree import Element

if TYPE_CHECKING:
    from docx.document import Document as DocType
    from docx.text.run import Run as RunType


class APAFiguresHandler:
    """Handles figure formatting and captions per APA 7th Edition."""

    def __init__(self, doc: DocType, config: dict[str, Any] | None = None) -> None:
        self.doc = doc
        self.config = config if config is not None else {}

    def _get_figure_config(self) -> dict[str, Any]:
        """Get figure configuration from config with defaults."""
        default_config: dict[str, Any] = {
            "caption_prefix": "Figure",
            "title_above": True,
            "nota_prefix": "Nota.",
        }
        return cast(dict[str, Any], self.config.get("figures", default_config))

    def _get_body_font(self) -> str:
        """Get body font name from config."""
        fonts: dict[str, Any] = {}
        return cast(
            str, self.config.get("fonts", fonts).get("body", {}).get("name", "Times New Roman")
        )

    def _apply_font_style(self, run: RunType, bold: bool = False, italic: bool = False) -> None:
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
        """Ensure every figure has an APA 7 caption: 'Figura N.' bold + title italic.

        APA 7 places the figure number and title ABOVE the image (the note
        stays below), so caption paragraphs found directly below an image are
        moved above it. Images without any caption get one inserted, numbered
        after the highest number already present and titled from the image's
        alt text. Already-formatted captions are normalized in place.
        """
        from docx.text.paragraph import Paragraph

        caption_re = re.compile(r"^(Figura|Figure)\s+(\d+)\s*[.:]?\s*(.*)$")

        image_paragraphs = [
            p for p in self.doc.paragraphs if p._element.findall(f".//{qn('w:drawing')}")
        ]

        # Move captions sitting directly below their image to above it
        for img_p in image_paragraphs:
            nxt = img_p._element.getnext()
            if nxt is None or nxt.tag != qn("w:p"):
                continue
            next_p = Paragraph(nxt, img_p._parent)
            if caption_re.match(next_p.text.strip()):
                img_p._element.addprevious(nxt)

        # Number new captions after the highest existing figure number
        max_used = 0
        for p in self.doc.paragraphs:
            match = caption_re.match(p.text.strip())
            if match:
                max_used = max(max_used, int(match.group(2)))

        for img_p in image_paragraphs:
            if self._has_adjacent_caption(img_p, caption_re) or self._has_manual_title(img_p):
                continue
            max_used += 1
            alt_text = self._extract_alt_text(img_p)
            caption_el = self._build_caption_element(max_used, alt_text)
            img_p._element.addprevious(caption_el)

        # Normalize caption paragraphs into bold label + italic title runs
        for para in self.doc.paragraphs:
            text = para.text.strip()
            m = caption_re.match(text)
            if not m:
                continue
            label, num, title = m.group(1), m.group(2), m.group(3).strip()
            runs = para.runs
            label_ok = bool(runs) and bool(runs[0].bold)
            italic_ok = not title or any(r.italic for r in runs)
            if label_ok and italic_ok:
                continue
            for r in list(runs):
                parent = r._element.getparent()
                if parent is not None:
                    parent.remove(r._element)
            label_run = para.add_run(f"{label} {num}. ")
            label_run.bold = True
            self._apply_font_style(label_run, bold=True)
            if title:
                title_run = para.add_run(title)
                title_run.italic = True
                self._apply_font_style(title_run, italic=True)
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def _has_adjacent_caption(self, img_p: Any, caption_re: re.Pattern[str]) -> bool:
        """Return whether the paragraphs around an image contain its caption."""
        from docx.text.paragraph import Paragraph

        for el in (img_p._element.getprevious(), img_p._element.getnext()):
            if el is None or el.tag != qn("w:p"):
                continue
            neighbor = Paragraph(el, img_p._parent)
            if caption_re.match(neighbor.text.strip()):
                return True
        return False

    def _has_manual_title(self, img_p: Any) -> bool:
        """Return whether a short untitled line next to an image is its caption.

        Authors may write a plain caption line below an image ("My Figure
        Title") instead of a numbered "Figura N" label; auto-numbering over
        it would duplicate the caption, so it is left untouched.
        """
        from docx.text.paragraph import Paragraph

        for el in (img_p._element.getprevious(), img_p._element.getnext()):
            if el is None or el.tag != qn("w:p"):
                continue
            neighbor = Paragraph(el, img_p._parent)
            text = neighbor.text.strip()
            if not text or text.startswith("Nota.") or text.startswith("Note."):
                continue
            style_name = neighbor.style.name if neighbor.style else ""
            if style_name.startswith("Heading"):
                continue
            if len(text) < 80 and not text.endswith((".", ",", ";")):
                return True
        return False

    def _build_caption_element(self, number: int, title: str) -> Element:
        """Build a 'Figura N' (bold) + title (italic) caption paragraph."""
        prefix = cast(str, self._get_figure_config().get("caption_prefix", "Figure"))

        p_el = OxmlElement("w:p")
        p_pr = OxmlElement("w:pPr")
        jc = OxmlElement("w:jc")
        jc.set(qn("w:val"), "left")
        p_pr.append(jc)
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:after"), "0")
        spacing.set(qn("w:line"), "480")
        spacing.set(qn("w:lineRule"), "auto")
        p_pr.append(spacing)
        p_el.append(p_pr)

        label_run = OxmlElement("w:r")
        label_rpr = OxmlElement("w:rPr")
        label_rpr.append(OxmlElement("w:b"))
        self._append_font_props(label_rpr)
        label_run.append(label_rpr)
        label_t = OxmlElement("w:t")
        label_t.set(qn("xml:space"), "preserve")
        label_t.text = f"{prefix} {number}. "
        label_run.append(label_t)
        p_el.append(label_run)

        if title:
            title_run = OxmlElement("w:r")
            title_rpr = OxmlElement("w:rPr")
            title_rpr.append(OxmlElement("w:i"))
            self._append_font_props(title_rpr)
            title_run.append(title_rpr)
            title_t = OxmlElement("w:t")
            title_t.set(qn("xml:space"), "preserve")
            title_t.text = title
            title_run.append(title_t)
            p_el.append(title_run)

        return p_el

    def _append_font_props(self, rpr: Element) -> None:
        """Append Times New Roman 12pt run properties to a w:rPr element."""
        font = OxmlElement("w:rFonts")
        font.set(qn("w:ascii"), "Times New Roman")
        font.set(qn("w:hAnsi"), "Times New Roman")
        rpr.append(font)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "24")
        rpr.append(sz)

    @staticmethod
    def _extract_alt_text(p: Any) -> str:
        """Extract alt text from the first drawing of a paragraph."""
        ns_wp = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
        for drawing in p._element.findall(f".//{qn('w:drawing')}"):
            for docPr in drawing.iter(f"{{{ns_wp}}}docPr"):
                return str((docPr.get("descr", "") or docPr.get("name", "")).strip())
            ns_pic = "http://schemas.openxmlformats.org/drawingml/2006/picture"
            for cNvPr in drawing.iter(f"{{{ns_pic}}}cNvPr"):
                return str((cNvPr.get("descr", "") or cNvPr.get("name", "")).strip())
        return ""

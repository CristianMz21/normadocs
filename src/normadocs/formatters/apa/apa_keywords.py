"""APA keywords and foreign word formatting."""

import re
from typing import Any

from docx.shared import Inches

from ...models import DocumentMetadata


class APAKeywordsHandler:
    """Handles formatting of keywords and foreign words per APA 7th Edition."""

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

    def _apply_font_style(self, run, italic: bool | None = None) -> None:
        """Apply font style to a run (helper for this handler)."""
        from .apa_styles import APAStylesHandler

        handler = APAStylesHandler(self.doc)
        handler._apply_font_style(run, italic=italic)

    def format_keywords(self, meta: DocumentMetadata) -> None:
        """Format 'Palabras clave' per APA 7.

        APA 7 requires:
        - Keywords on its own line after abstract
        - Left indent of 0.5 inches
        - "Keywords:" label in italics
        """
        found_kw = False

        for p in self.doc.paragraphs:
            text_lower = p.text.lower()
            if "palabras clave" in text_lower or "keywords" in text_lower:
                found_kw = True

                full = p.text.strip()
                match = re.search(r"((?:Palabras\s+clave|Keywords):)(.*)", full, re.IGNORECASE)
                if match:
                    label, content = match.groups()
                    p.clear()
                    p.paragraph_format.left_indent = Inches(0.5)
                    p.paragraph_format.first_line_indent = Inches(0)
                    r1 = p.add_run(label + " ")
                    r1.italic = True
                    self._apply_font_style(r1)
                    r2 = p.add_run(content.strip())
                    self._apply_font_style(r2)
                break

        if found_kw:
            self._add_page_break_before_introduction()

    def _add_page_break_before_introduction(self) -> None:
        """Add page break before the Introduction section.

        APA 7: After keywords, the introduction starts on a new page.
        """
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        for p in self.doc.paragraphs:
            if p.style and p.style.name.startswith("Heading"):
                text = p.text.strip().lower()
                if "introducción" in text or "introduction" in text:
                    br = OxmlElement("w:br")
                    br.set(qn("w:type"), "page")
                    p._element.addprevious(br)
                    break

    def format_nota_italic(self) -> None:
        """APA 7: 'Nota.' must be italic in figure/table notes.

        Finds paragraphs starting with 'Nota.' and splits the first run
        so that 'Nota.' is italic and the rest is regular.
        """
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches

        for p in self.doc.paragraphs:
            text = p.text.strip()
            if not text.startswith("Nota."):
                continue

            # Get full text and rebuild with italic "Nota."
            full_text = p.text
            # Clear all runs
            for run in list(p.runs):
                run._element.getparent().remove(run._element)

            # Add "Nota. " as italic
            nota_run = p.add_run("Nota. ")
            nota_run.italic = True
            self._apply_font_style(nota_run, italic=True)

            # Add the rest as regular text
            rest = full_text[len("Nota.") :].strip()
            if rest:
                rest_run = p.add_run(rest)
                self._apply_font_style(rest_run)

            # Ensure left alignment and no indent for notes
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.first_line_indent = Inches(0)

    def apply_foreign_word_italics(self) -> None:
        """Apply italics to foreign words per APA 7 (Backend, Frontend, etc.).

        APA 7 requires that foreign words used as nouns be italicized on first use.
        This method searches for these terms in table cells and applies italics.
        """
        foreign_words = [
            "Backend",
            "Frontend",
            "backend",
            "frontend",
            "PostgreSQL",
            "Redis",
            "Django",
            "React",
            "Next.js",
            "JavaScript",
            "Python",
            "Celery",
            "Docker",
            "Wompi",
            "WhatsApp",
            "iPhone",
            "iOS",
            "DDoS",
            "SSL",
            "PCI DSS",
            "RESTful",
            "API",
            "APIs",
            "SQL",
            "ORM",
            "CDN",
            "CEO",
        ]

        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        runs = list(p.runs)
                        for run in runs:
                            if not run.text:
                                continue
                            text = run.text
                            has_foreign = any(fw in text for fw in foreign_words)
                            if not has_foreign:
                                continue
                            if run.italic:
                                continue
                            run.italic = True

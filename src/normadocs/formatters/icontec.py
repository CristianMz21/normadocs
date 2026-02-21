from docx import Document
from docx.document import Document as DocumentObject
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm, Pt, RGBColor

from ..models import DocumentMetadata
from .base import DocumentFormatter


class IcontecFormatter(DocumentFormatter):
    """
    Applies ICONTEC (NTC 1486) formatting to a DOCX file.
    """

    def __init__(self, doc_path: str):
        super().__init__(doc_path)
        self.doc: DocumentObject = Document(doc_path)

    def process(self, meta: DocumentMetadata):
        """Run the ICONTEC formatting pipeline."""
        self._setup_page_layout()
        self._create_styles()
        self._add_cover_page(meta)
        self._process_paragraphs()
        # Tables and Citations logic can be added later/adapted
        # For now, we focus on layout and text style.

    def save(self, output_path: str):
        self.doc.save(str(output_path))

    def _setup_page_layout(self):
        """
        NTC 1486 Margins:
        Top: 3 cm (4 cm if Title) - We'll use 3 cm generally
        Left: 3 cm (4 cm if bound) - We'll use 3 cm
        Right: 2 cm
        Bottom: 2 cm
        """
        for section in self.doc.sections:
            section.top_margin = Cm(3)
            section.bottom_margin = Cm(2)
            section.left_margin = Cm(3)
            section.right_margin = Cm(2)

    def _create_styles(self):
        """
        Font: Arial 12.
        Spacing: 1.5 lines.
        """
        styles = self.doc.styles

        # Normal
        normal = styles["Normal"]
        font = normal.font
        font.name = "Arial"
        font.size = Pt(12)
        font.color.rgb = RGBColor(0, 0, 0)

        pf = normal.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)

        # Headings
        # Heading 1: Centered, Bold, Uppercase (handled in text)
        if "Heading 1" in styles:
            h1 = styles["Heading 1"]
            h1.font.name = "Arial"
            h1.font.size = Pt(12)
            h1.font.bold = True
            h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            h1.paragraph_format.space_before = Pt(12)  # Space before title
            h1.paragraph_format.space_after = Pt(12)

    def _add_cover_page(self, meta: DocumentMetadata):
        """
        ICONTEC Cover Page:
        - Title (Centered, Vertical align top approx)
        - Author (Centered, vertical align middle)
        - Legend (Institution, Faculty, etc. at bottom)
        - City, Year (Bottom)
        """
        # Simplistic implementation: Insert at top
        self.doc.add_paragraph()
        if self.doc.paragraphs:
            self.doc.paragraphs[0].insert_paragraph_before("")

        ref_p = self.doc.paragraphs[0]

        # Helper to add centered line
        def add_line(text, bold=False, space_after=0):
            p = ref_p.insert_paragraph_before(text)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.style = self.doc.styles["Normal"]
            if bold and p.runs:
                p.runs[0].bold = True
            p.paragraph_format.space_after = Pt(space_after)
            return p

        # Title formatting
        add_line(meta.title.upper(), bold=True, space_after=120)  # Approx space

        # Author
        add_line(meta.author or "Author Name", space_after=200)

        # Legend/Footer block
        # Institution
        institution = meta.institution or "Institution Name"
        add_line(institution.upper())

        # Program/Faculty
        if meta.program:
            add_line(meta.program.upper())

        # City, Year
        city = meta.extra.get("city", "City")
        year = meta.date or "2024"
        add_line(f"{city.upper()}, {year}")

        # Page Break
        pb_p = ref_p.insert_paragraph_before()
        pb_p.add_run().add_break()

    def _process_paragraphs(self):
        """Justify text and ensure Arial."""
        for p in self.doc.paragraphs:
            # Skip if cover page created just now...
            # Ideally we skip based on section or style
            if p.style and p.style.name.startswith("Heading"):
                continue

            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Cm(0)  # No indent in ICONTEC usually

            # Ensure font
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(12)

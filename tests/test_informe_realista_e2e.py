"""End-to-end tests over an ultra-realistic full report.

Fixture: ``tests/fixtures/informe_realista.md`` — a SENA/ADSO report with
YAML frontmatter, cover metadata, H1/H2/H3 sections, ordered and bullet
lists, a pipe table with note, display math, a ``sql {code}`` block, a
>40-word block quote, narrative/parenthetical citations and references.

The pipeline (CLI -> Pandoc -> formatter -> DOCX/PDF) must convert it with
exactly one page break per H1 transition (no blank pages), a complete
cover page, and APA-styled body elements.

Requires: pandoc installed. PDF class additionally requires LibreOffice.
"""

import shutil
import unittest
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from typer.testing import CliRunner

from normadocs.cli import app

try:
    import fitz

    HAS_FITZ = True
except ImportError:  # pragma: no cover - dev dependency present in CI
    HAS_FITZ = False

runner = CliRunner()

PANDOC_AVAILABLE = shutil.which("pandoc") is not None
SOFFICE_AVAILABLE = shutil.which("soffice") is not None

FIXTURE_MD = Path(__file__).resolve().parent / "fixtures" / "informe_realista.md"
BIB_PATH = Path(__file__).resolve().parent.parent / "examples" / "references.bib"

EXPECTED_H1 = [
    "Resumen",
    "Introducción",
    "Marco teórico",
    "Metodología",
    "Resultados",
    "Discusión",
    "Conclusiones",
    "Referencias",
]

MATH_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
QUOTE_MARKERS = ('"', "\u201c", "\u201d", "\u00ab", "\u00bb")


def _has_page_break(paragraph) -> bool:
    """Return whether a paragraph holds an explicit page-break run."""
    return any(
        br.get(qn("w:type")) == "page"
        for run in paragraph.runs
        for br in run._element.findall(qn("w:br"))
    )


def _assert_no_blank_page_mechanics(testcase, doc) -> None:
    """No doubled page-break mechanism anywhere in the document.

    Each H1 transition must use exactly one mechanism: either a preceding
    explicit break paragraph or a ``page_break_before`` flag — never both,
    and never two consecutive break paragraphs (both render as blank
    pages in Word/LibreOffice).
    """
    paras = doc.paragraphs
    for i, para in enumerate(paras[1:], start=1):
        if _has_page_break(para) and _has_page_break(paras[i - 1]):
            testcase.fail(f"Consecutive page-break paragraphs at index {i - 1}, {i}")
    for i, para in enumerate(paras):
        if not para.style.name.startswith("Heading"):
            continue
        if i == 0:
            continue
        if bool(para.paragraph_format.page_break_before) and _has_page_break(paras[i - 1]):
            testcase.fail(f"Doubled break before heading {para.text.strip()!r} at {i}")


def _assert_reference_opens_new_page(testcase, doc) -> None:
    """Reference sections open on a fresh page with a single mechanism.

    Both pagination policies (one page per H1, continuous body with a
    References break) agree that Referencias starts on a new page, so the
    E2E locks exactly that: one explicit break paragraph or one break
    flag — never both, never none.
    """
    paras = doc.paragraphs
    ref_idx = next(
        i
        for i, p in enumerate(paras)
        if p.style.name == "Heading 1" and p.text.strip().lower() == "referencias"
    )
    has_para_break = ref_idx > 0 and _has_page_break(paras[ref_idx - 1])
    has_flag = bool(paras[ref_idx].paragraph_format.page_break_before)
    testcase.assertTrue(
        has_para_break != has_flag,
        "Referencias must open a new page with exactly one break mechanism",
    )


def _assert_h1_sequence(testcase, doc, headings) -> None:
    """All expected H1 sections present in order, tolerating a cover title.

    The cover handler may insert the document title as a leading H1 when
    the Markdown body starts directly with a section, so the assertion
    accepts an optional extra first heading.
    """
    paras = doc.paragraphs
    h1_texts = [p.text.strip() for p in paras if p.style.name == "Heading 1" and p.text.strip()]
    testcase.assertTrue(len(h1_texts) >= len(headings), f"H1 texts: {h1_texts}")
    testcase.assertEqual(
        h1_texts[len(h1_texts) - len(headings) :],
        headings,
        f"H1 order/content mismatch: {h1_texts}",
    )


def _full_text(doc) -> str:
    """Concatenated paragraph text of a document."""
    return "\n".join(p.text for p in doc.paragraphs)


def _run_cli(args: list[str]):
    """Invoke the CLI, raising a rich assertion message on failure."""
    return runner.invoke(app, args)


@unittest.skipUnless(PANDOC_AVAILABLE, "Pandoc not installed — skipping realistic-report E2E")
class TestInformeRealistaDocx(unittest.TestCase):
    """Full report -> APA7ESTUDIANTE DOCX with complete content validation."""

    output_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.output_dir = Path("tests/temp_informe_realista")
        cls.output_dir.mkdir(parents=True, exist_ok=True)
        cls.cli_result = _run_cli(
            [
                str(FIXTURE_MD),
                "--style",
                "apa7estudiante",
                "--format",
                "docx",
                "--output-dir",
                str(cls.output_dir),
            ]
        )
        cls.docx_path = cls.output_dir / "informe_realista_APA7ESTUDIANTE.docx"
        cls.doc = Document(str(cls.docx_path)) if cls.docx_path.exists() else None

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)

    def test_cli_exits_successfully(self):
        """CLI must exit with code 0 on the full report."""
        self.assertEqual(
            self.cli_result.exit_code,
            0,
            f"CLI failed: {self.cli_result.output}\n{self.cli_result.exception}",
        )

    def test_docx_created_and_non_empty(self):
        """Output DOCX must exist with content."""
        self.assertTrue(self.docx_path.exists())
        self.assertGreater(self.docx_path.stat().st_size, 0)
        self.assertIsNotNone(self.doc)

    def test_cover_fields_present(self):
        """All frontmatter metadata must reach the cover page."""
        text = _full_text(self.doc)
        for expected in [
            "Automatización de procesos administrativos",
            "Cristian Muñoz Arellano",
            "Tecnología en Análisis y Desarrollo de Software",
            "Servicio Nacional de Aprendizaje (SENA)",
            "Análisis y Diseño de Sistemas de Información (ADSO-2026)",
            "Carolina Restrepo",
            "26 de septiembre de 2026",
        ]:
            self.assertIn(expected, text, f"Cover field missing: {expected}")

    def test_heading_structure_complete(self):
        """All eight H1 sections in order, plus H2/H3 subsections."""
        _assert_h1_sequence(self, self.doc, EXPECTED_H1)
        heading_texts = [
            p.text.strip() for p in self.doc.paragraphs if p.style.name.startswith("Heading")
        ]
        joined = " | ".join(heading_texts)
        for expected in EXPECTED_H1:
            self.assertIn(expected, joined)
        for expected in ["Antecedentes", "Enfoque", "Fases del estudio", "Definiciones básicas"]:
            self.assertIn(expected, joined)

    def test_no_blank_page_mechanics(self):
        """No doubled page-break mechanism (blank-page regression)."""
        _assert_no_blank_page_mechanics(self, self.doc)

    def test_reference_opens_new_page(self):
        """Referencias opens on a fresh page with a single break mechanism."""
        _assert_reference_opens_new_page(self, self.doc)

    def test_margins_and_body_font(self):
        """APA layout: 1-inch margins, Times New Roman 12pt body."""
        one_inch = Inches(1)
        for section in self.doc.sections:
            self.assertEqual(section.left_margin, one_inch)
            self.assertEqual(section.top_margin, one_inch)
        normal = self.doc.styles["Normal"]
        self.assertEqual(normal.font.name, "Times New Roman")
        self.assertEqual(normal.font.size, Pt(12))

    def test_table_with_caption_and_note(self):
        """Pipe table converts with caption and italic note."""
        self.assertGreater(len(self.doc.tables), 0, "No tables in output")
        text = _full_text(self.doc)
        self.assertTrue("Tabla 1" in text or "Table 1" in text, "Table caption missing")
        self.assertIn("Elaboración propia", text)

    def test_block_quote_formatting(self):
        """The >40-word quote is a freestanding indented block without quotes."""
        candidates = [p for p in self.doc.paragraphs if "personalizar el contenido" in p.text]
        self.assertEqual(len(candidates), 1, "Block quote paragraph not found exactly once")
        quote = candidates[0]
        for marker in QUOTE_MARKERS:
            self.assertNotIn(marker, quote.text)
        self.assertEqual(quote.paragraph_format.left_indent, Inches(0.5))

    def test_references_hanging_indent(self):
        """Reference entries use hanging indent and keep their content."""
        ref_paras = [
            p for p in self.doc.paragraphs if "García, J." in p.text or "Pressman, R. S." in p.text
        ]
        self.assertGreaterEqual(len(ref_paras), 2, "Reference entries missing")
        for para in ref_paras:
            self.assertEqual(para.paragraph_format.left_indent, Inches(0.5))
            self.assertEqual(para.paragraph_format.first_line_indent, Inches(-0.5))

    def test_math_and_code_content(self):
        """Display math survives as OMML and SQL content is preserved.

        The SQL ``{code}`` block reaches the DOCX either as text (when image
        rendering is unavailable, e.g. CI without wkhtmltoimage) or as a
        rendered code image (when wkhtmltoimage is installed locally).
        """
        omath = [el for p in self.doc.paragraphs for el in p._element.iter(f"{MATH_NS}oMath")]
        self.assertGreater(len(omath), 0, "Display math (oMath) missing from output")
        text = _full_text(self.doc)
        sql_as_text = "SELECT" in text or "select" in text
        sql_as_image = len(self.doc.inline_shapes) > 0
        self.assertTrue(
            sql_as_text or sql_as_image,
            "SQL block content missing (neither text nor code image found)",
        )

    def test_lists_and_keywords(self):
        """Ordered/list items and keywords line reach the document."""
        text = _full_text(self.doc)
        self.assertIn("Levantamiento de requerimientos", text)
        self.assertIn("Entrevistas semiestructuradas", text)
        self.assertIn("Palabras clave", text)


@unittest.skipUnless(
    PANDOC_AVAILABLE and SOFFICE_AVAILABLE, "Pandoc/LibreOffice missing — skipping PDF E2E"
)
@unittest.skipUnless(HAS_FITZ, "pymupdf missing — skipping PDF E2E")
class TestInformeRealistaPdf(unittest.TestCase):
    """Full report -> PDF: pagination without blank pages."""

    output_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.output_dir = Path("tests/temp_informe_realista_pdf")
        cls.output_dir.mkdir(parents=True, exist_ok=True)
        cls.cli_result = _run_cli(
            [
                str(FIXTURE_MD),
                "--style",
                "apa7estudiante",
                "--format",
                "pdf",
                "--no-verify-apa",
                "--output-dir",
                str(cls.output_dir),
            ]
        )
        cls.pdf_path = cls.output_dir / "informe_realista_APA7ESTUDIANTE.pdf"

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)

    def test_pdf_created_without_blank_pages(self):
        """PDF must exist, cover all sections, and contain zero blank pages."""
        self.assertEqual(self.cli_result.exit_code, 0, f"CLI failed: {self.cli_result.output}")
        self.assertTrue(self.pdf_path.exists())
        with fitz.open(str(self.pdf_path)) as pdf:
            self.assertGreaterEqual(len(pdf), 5, "PDF suspiciously short for a full report")
            blank = [i for i, page in enumerate(pdf) if not page.get_text().strip()]
            self.assertEqual(blank, [], f"Blank pages at indices {blank}")
            pdf_text = "\n".join(page.get_text() for page in pdf)
        for expected in EXPECTED_H1:
            self.assertIn(expected, pdf_text)


@unittest.skipUnless(PANDOC_AVAILABLE, "Pandoc not installed — skipping cross-style E2E")
class TestInformeRealistaApaStyle(unittest.TestCase):
    """Full report converts under the APA style with the same break invariants."""

    output_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.output_dir = Path("tests/temp_informe_realista_apa")
        cls.output_dir.mkdir(parents=True, exist_ok=True)
        cls.cli_result = _run_cli(
            [
                str(FIXTURE_MD),
                "--style",
                "apa",
                "--format",
                "docx",
                "--output-dir",
                str(cls.output_dir),
            ]
        )
        cls.docx_path = cls.output_dir / "informe_realista_APA.docx"
        cls.doc = Document(str(cls.docx_path)) if cls.docx_path.exists() else None

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)

    def test_apa_style_break_invariants(self):
        """APA style keeps the no-blank-page guarantees."""
        self.assertEqual(self.cli_result.exit_code, 0, f"CLI failed: {self.cli_result.output}")
        self.assertIsNotNone(self.doc)
        _assert_no_blank_page_mechanics(self, self.doc)
        _assert_reference_opens_new_page(self, self.doc)


@unittest.skipUnless(PANDOC_AVAILABLE, "Pandoc not installed — skipping bibliography E2E")
class TestInformeRealistaBibliography(unittest.TestCase):
    """Full report with --bibliography renders cited entries."""

    output_dir: Path

    @classmethod
    def setUpClass(cls) -> None:
        cls.output_dir = Path("tests/temp_informe_realista_bib")
        cls.output_dir.mkdir(parents=True, exist_ok=True)
        cls.cli_result = _run_cli(
            [
                str(FIXTURE_MD),
                "--style",
                "apa",
                "--format",
                "docx",
                "--bibliography",
                str(BIB_PATH),
                "--output-dir",
                str(cls.output_dir),
            ]
        )
        cls.docx_path = cls.output_dir / "informe_realista_APA.docx"
        cls.doc = Document(str(cls.docx_path)) if cls.docx_path.exists() else None

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)

    def test_bibliography_renders(self):
        """Pandoc bibliography entries appear in the output."""
        self.assertEqual(self.cli_result.exit_code, 0, f"CLI failed: {self.cli_result.output}")
        self.assertIsNotNone(self.doc)
        self.assertIn("Doe", _full_text(self.doc))


class TestInformeRealistaCliErrors(unittest.TestCase):
    """CLI input validation on the realistic fixture."""

    def test_invalid_style_fails(self):
        """An unsupported style exits with code 1."""
        result = _run_cli([str(FIXTURE_MD), "--style", "chicago"])
        self.assertEqual(result.exit_code, 1)

    def test_missing_file_fails(self):
        """A nonexistent input file exits nonzero (Typer usage error)."""
        result = _run_cli(["tests/fixtures/no_existe.md"])
        self.assertEqual(result.exit_code, 2)


if __name__ == "__main__":
    unittest.main()

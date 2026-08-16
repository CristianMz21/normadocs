"""Unit tests for CitationsCheck - APA 7th Edition in-text citation verification."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from docx import Document

from normadocs.models import DocumentMetadata
from normadocs.verifier.apa_verifier import APAVerifier, VerificationContext
from normadocs.verifier.checks.citations import CitationsCheck


class TestCitationsCheck(unittest.TestCase):
    """Tests for the in-text citations verifier check."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def _run_check(self, paragraphs: list[tuple[str, str]]) -> list:
        path = self.temp_path / "citations.docx"
        doc = Document()
        for text, style in paragraphs:
            doc.add_paragraph(text, style=style)
        doc.save(str(path))

        pdf_path = self.temp_path / "output.pdf"
        pdf_path.touch()
        meta = DocumentMetadata(title="Test Document")
        verifier = APAVerifier(pdf_path=pdf_path, docx_path=path, meta=meta)
        ctx = VerificationContext(
            pdf=MagicMock(),
            docx=verifier.docx,
            meta=meta,
            strict=False,
        )
        try:
            return CitationsCheck().run(ctx)
        finally:
            verifier.close()

    def test_ampersand_violation_is_reported(self):
        """Spanish 'y' inside a parenthetical citation is flagged."""
        issues = self._run_check(
            [("Los resultados coinciden (García y López, 2020) con la hipótesis.", "Normal")]
        )
        ampersand = [i for i in issues if i.check == "citations.ampersand"]
        self.assertEqual(len(ampersand), 1)

    def test_correct_ampersand_passes(self):
        """'&'-joined citations produce no issues."""
        issues = self._run_check(
            [("Los resultados coinciden (García & López, 2020) con la hipótesis.", "Normal")]
        )
        self.assertEqual(issues, [])

    def test_three_authors_without_et_al_is_reported(self):
        """Citations listing 3+ authors without 'et al.' are flagged."""
        issues = self._run_check(
            [("García, López y Martínez (2020) demostraron el efecto.", "Normal")]
        )
        et_al = [i for i in issues if i.check == "citations.et_al"]
        self.assertEqual(len(et_al), 1)

    def test_et_al_citation_passes(self):
        """Truncated citations produce no issues."""
        issues = self._run_check(
            [
                ("García et al. (2020) demostraron el efecto medido (p < 0.05).", "Normal"),
            ]
        )
        self.assertEqual(issues, [])

    def test_long_quoted_text_is_reported(self):
        """A 40+ word quotation still wrapped in quotes is flagged."""
        words = " ".join(f"palabra{i}" for i in range(45))
        issues = self._run_check([(f'"{words}" (García, 2020).', "Normal")])
        block = [i for i in issues if i.check == "citations.block_quote_format"]
        self.assertEqual(len(block), 1)

    def test_short_quotation_passes(self):
        """Short in-line quotations are fine."""
        issues = self._run_check([('"cita breve" según García (2020).', "Normal")])
        self.assertEqual(issues, [])

    def test_references_section_is_not_scanned(self):
        """Reference entries after the heading are not treated as citations."""
        issues = self._run_check(
            [
                ("Referencias", "Heading 1"),
                ("García, A., López, B. y Silva, C. (2020). Estudio completo.", "Normal"),
            ]
        )
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()

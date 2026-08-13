"""Unit tests for strict general APA report structure validation."""

import unittest
from unittest.mock import MagicMock

from normadocs.models import DocumentMetadata
from normadocs.verifier.apa_verifier import VerificationContext
from normadocs.verifier.checks.structure import StructureCheck
from normadocs.verifier.docx_analyzer import DOCXParagraphInfo


class _ParagraphSource:
    """Small analyzer double exposing only the paragraphs used by StructureCheck."""

    def __init__(self, paragraphs: list[DOCXParagraphInfo]) -> None:
        self._paragraphs = paragraphs

    def get_paragraphs_info(self) -> list[DOCXParagraphInfo]:
        """Return the configured paragraph sequence."""
        return self._paragraphs


class TestStructureCheck(unittest.TestCase):
    """Tests for the mandatory structure of a general academic report."""

    def _paragraphs(self, *items: tuple[str, str | None]) -> list[DOCXParagraphInfo]:
        return [
            DOCXParagraphInfo(
                text=text,
                style_name=style,
                alignment="left",
                first_line_indent=None,
                space_before=None,
                space_after=None,
                line_spacing=2.0,
                runs=[],
            )
            for text, style in items
        ]

    def _run(self, paragraphs: list[DOCXParagraphInfo]) -> list:
        context = VerificationContext(
            pdf=MagicMock(),
            docx=_ParagraphSource(paragraphs),
            meta=DocumentMetadata(title="Informe de prueba"),
            strict=True,
        )
        return StructureCheck().run(context)

    def test_complete_report_structure_passes(self) -> None:
        """A report with the required sections and order should pass."""
        issues = self._run(
            self._paragraphs(
                ("Informe de prueba", None),
                ("Autor", None),
                ("2026", None),
                ("Informe de prueba", "Heading 1"),
                ("Introducción", "Heading 1"),
                ("La introducción presenta el problema.", None),
                ("Desarrollo", "Heading 1"),
                ("El desarrollo presenta el análisis.", None),
                ("Conclusiones", "Heading 1"),
                ("Las conclusiones resumen los hallazgos.", None),
                ("Referencias", "Heading 1"),
                ("Autor, A. (2026). Obra consultada.", None),
            )
        )
        self.assertEqual(issues, [], f"Unexpected structure issues: {issues}")

    def test_missing_required_section_is_error(self) -> None:
        """Missing conclusions must fail strict validation."""
        issues = self._run(
            self._paragraphs(
                ("Informe de prueba", None),
                ("Informe de prueba", "Heading 1"),
                ("Introducción", "Heading 1"),
                ("Contenido introductorio.", None),
                ("Desarrollo", "Heading 1"),
                ("Contenido principal.", None),
                ("Referencias", "Heading 1"),
                ("Autor, A. (2026). Obra consultada.", None),
            )
        )
        conclusion_errors = [i for i in issues if "conclusion_present" in i.check]
        self.assertTrue(conclusion_errors, f"Expected missing conclusion error: {issues}")
        self.assertTrue(all(i.severity == "error" for i in conclusion_errors))

    def test_optional_abstract_and_keywords_are_validated_when_present(self) -> None:
        """An oversized abstract and misplaced keywords must fail."""
        oversized = "palabra " * 251
        issues = self._run(
            self._paragraphs(
                ("Informe de prueba", None),
                ("Informe de prueba", "Heading 1"),
                ("Introducción", "Heading 1"),
                ("Contenido introductorio.", None),
                ("Resumen", "Heading 1"),
                (oversized, None),
                ("Palabras clave: APA, estructura", None),
                ("Desarrollo", "Heading 1"),
                ("Contenido principal.", None),
                ("Conclusiones", "Heading 1"),
                ("Conclusión.", None),
                ("Referencias", "Heading 1"),
                ("Autor, A. (2026). Obra consultada.", None),
            )
        )
        self.assertTrue(any("abstract_length" in i.check for i in issues))
        self.assertTrue(any("abstract_order" in i.check for i in issues))

    def test_heading_after_references_is_rejected(self) -> None:
        """Only appendix headings may follow References."""
        issues = self._run(
            self._paragraphs(
                ("Informe de prueba", None),
                ("Informe de prueba", "Heading 1"),
                ("Introducción", "Heading 1"),
                ("Contenido introductorio.", None),
                ("Desarrollo", "Heading 1"),
                ("Contenido principal.", None),
                ("Conclusiones", "Heading 1"),
                ("Conclusiones del informe.", None),
                ("Referencias", "Heading 1"),
                ("Autor, A. (2026). Obra consultada.", None),
                ("Anexo", "Heading 1"),
            )
        )
        self.assertTrue(any("content_after_references" in i.check for i in issues))


if __name__ == "__main__":
    unittest.main()

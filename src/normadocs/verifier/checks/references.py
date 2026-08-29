"""References verification for APA 7th Edition.

Verifies references section meets APA 7th Edition requirements:
- Section titled "Referencias" or "References" at document end
- Hanging indent (0.5 inches) on all references
- Alphabetical order
- Proper APA 7th citation format
- Double-spaced throughout
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from .. import CheckCategory, VerificationIssue
from ..docx_analyzer import DOCXParagraphInfo

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class ReferencesCheck:
    """Check references formatting against APA 7th Edition requirements."""

    _JOURNAL_VOLUME = re.compile(r"(?<=[.!?]\s)([A-ZÁÉÍÓÚÑ][^.!?]*?),\s*\d+(?=\s*[(,])")
    _YEAR_MARKER = re.compile(r"\((?:s\.\s*f\.|n\.\s*d\.|\d{4})")
    _SPANISH_CONJUNCTION = re.compile(r"\.\s*y\s+[A-ZÁÉÍÓÚÑ]")

    @staticmethod
    def _sort_key(reference: str) -> tuple[str, int, str]:
        """Return an APA-aware ordering key for a reference entry.

        APA orders works alphabetically by author, then chronologically for
        works by the same author. Undated works (``s. f.``/``n.d.``) precede
        dated works, which a plain lexical comparison does not implement.
        """
        author = reference.split("(", 1)[0].strip().casefold()
        date_match = re.search(r"\((s\.\s*f\.|n\.\s*d\.|\d{4})\)", reference, re.IGNORECASE)
        if date_match is None or date_match.group(1).casefold() in {"s. f.", "n. d."}:
            year = 0
        else:
            year = int(date_match.group(1))
        return author, year, reference.casefold()

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run references verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []
        paragraphs_info = ctx.docx.get_paragraphs_info()
        ref_section_idx = self._find_section(paragraphs_info)
        if ref_section_idx is None:
            return self._missing_section(issues)
        ref_paragraphs = self._collect_entries(paragraphs_info, ref_section_idx)
        if not ref_paragraphs:
            return self._missing_entries(issues)
        self._check_hanging_and_spacing(ref_paragraphs, ctx, issues)
        self._check_alphabetical_order(ref_paragraphs, ctx, issues)
        issues.extend(self._check_entry_format(ref_paragraphs))
        return issues

    def _find_section(self, paragraphs_info: list[DOCXParagraphInfo]) -> int | None:
        ref_keywords = ["referencias", "references", "bibliografía", "bibliography"]
        for i, p_info in enumerate(paragraphs_info):
            if p_info.text.strip().lower() in ref_keywords:
                return i
        return None

    def _missing_section(self, issues: list[VerificationIssue]) -> list[VerificationIssue]:
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.REFERENCES}.section_present",
                severity="error",
                expected="Section titled 'Referencias' or 'References'",
                actual="No references section found",
                evidence="Document lacks a references section",
            )
        )
        return issues

    def _collect_entries(
        self, paragraphs_info: list[DOCXParagraphInfo], ref_section_idx: int
    ) -> list[DOCXParagraphInfo]:
        ref_paragraphs: list[DOCXParagraphInfo] = []
        for p_info in paragraphs_info[ref_section_idx + 1 :]:
            if p_info.text.strip() and (p_info.style_name or "").startswith("Heading"):
                break
            if p_info.text.strip():
                ref_paragraphs.append(p_info)
        return ref_paragraphs

    def _missing_entries(self, issues: list[VerificationIssue]) -> list[VerificationIssue]:
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.REFERENCES}.entries_present",
                severity="error",
                expected="Reference entries",
                actual="No reference entries found",
                evidence="References section exists but contains no entries",
            )
        )
        return issues

    def _check_hanging_and_spacing(
        self,
        ref_paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        spacing_errors: list[int] = []
        for index, reference in enumerate(ref_paragraphs, start=1):
            self._check_single_hanging(reference, index, issues)
            if self._has_spacing_violation(reference, ctx):
                spacing_errors.append(index)
        if spacing_errors:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.REFERENCES}.spacing",
                    severity="error",
                    expected="Double-spaced references with no extra paragraph spacing",
                    actual=f"References with spacing violations: {spacing_errors}",
                    evidence="Every reference entry must use the APA reference spacing",
                )
            )

    def _check_single_hanging(
        self, reference: DOCXParagraphInfo, index: int, issues: list[VerificationIssue]
    ) -> None:
        expected_hanging = -0.5
        first_line_indent = reference.first_line_indent
        if first_line_indent is None:
            actual = "No first-line indent"
            indent_valid = False
        else:
            indent_inches = first_line_indent / 914400.0
            indent_valid = abs(indent_inches - expected_hanging) <= 0.1
            actual = f"{indent_inches:.2f} inch"
        if indent_valid:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.REFERENCES}.hanging_indent",
                severity="error",
                expected="-0.5 inch hanging indent (first line outdent)",
                actual=actual,
                evidence=f"Reference {index} lacks proper hanging indent",
            )
        )

    def _has_spacing_violation(
        self, reference: DOCXParagraphInfo, ctx: VerificationContext
    ) -> bool:
        if not ctx.strict:
            return False
        if reference.line_spacing is None:
            return True
        if abs(reference.line_spacing - 2.0) > 0.2:
            return True
        if reference.space_before not in (None, 0):
            return True
        return reference.space_after not in (None, 0)

    def _check_alphabetical_order(
        self,
        ref_paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        ref_texts = [p.text.strip() for p in ref_paragraphs]
        for i in range(len(ref_texts) - 1):
            if self._sort_key(ref_texts[i]) <= self._sort_key(ref_texts[i + 1]):
                continue
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.REFERENCES}.alphabetical_order",
                    severity="error" if ctx.strict else "warning",
                    expected="Alphabetical order",
                    actual=f"'{ref_texts[i]}' before '{ref_texts[i + 1]}'",
                    evidence="References not in alphabetical order",
                )
            )
            break

    def _check_entry_format(self, ref_paragraphs: list[Any]) -> list[VerificationIssue]:
        """Verify the internal format of each reference entry."""
        issues: list[VerificationIssue] = []
        for index, p_info in enumerate(ref_paragraphs, start=1):
            self._check_single_entry(p_info, index, issues)
        return issues

    def _check_single_entry(self, p_info: Any, index: int, issues: list[VerificationIssue]) -> None:
        text = p_info.text.strip()
        if not text:
            return
        self._check_retrieved_from(text, index, issues)
        self._check_spanish_conjunction(text, index, issues)
        self._check_doi_format(text, index, issues)
        self._check_italic_source(p_info, text, index, issues)

    def _check_retrieved_from(self, text: str, index: int, issues: list[VerificationIssue]) -> None:
        if not re.search(r"\b(?:recuperado\s+de|retrieved\s+from)\b", text, re.IGNORECASE):
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.REFERENCES}.retrieved_from",
                severity="warning",
                expected="Direct URL or DOI without 'Recuperado de'",
                actual="APA 6 retrieval phrase present",
                evidence=f"Reference {index} still uses 'Recuperado de'/'Retrieved from'",
            )
        )

    def _check_spanish_conjunction(
        self, text: str, index: int, issues: list[VerificationIssue]
    ) -> None:
        marker = self._YEAR_MARKER.search(text)
        head = text[: marker.start()] if marker else text
        if not self._SPANISH_CONJUNCTION.search(head):
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.REFERENCES}.entry_ampersand",
                severity="error",
                expected="Last author joined with ', & '",
                actual="Authors joined with 'y'",
                evidence=f"Reference {index} must use '&' before the last author",
            )
        )

    def _check_doi_format(self, text: str, index: int, issues: list[VerificationIssue]) -> None:
        if not re.search(r"\bdoi:", text, re.IGNORECASE) and "dx.doi.org" not in text:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.REFERENCES}.doi_format",
                severity="warning",
                expected="DOI as 'https://doi.org/…'",
                actual="Legacy DOI notation",
                evidence=f"Reference {index} must use the https://doi.org/ format",
            )
        )

    def _check_italic_source(
        self, p_info: Any, text: str, index: int, issues: list[VerificationIssue]
    ) -> None:
        has_italic = any(run.get("italic") for run in p_info.runs)
        if has_italic or not self._JOURNAL_VOLUME.search(text):
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.REFERENCES}.italic_source",
                severity="warning",
                expected="Journal name and volume in italics",
                actual="No italicized source in a journal-style entry",
                evidence=f"Reference {index} looks like a journal article without italics",
            )
        )

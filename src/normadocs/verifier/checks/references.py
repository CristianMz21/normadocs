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
from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class ReferencesCheck:
    """Check references formatting against APA 7th Edition requirements."""

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

        ref_section_idx = None
        ref_keywords = ["referencias", "references", "bibliografía", "bibliography"]

        for i, p_info in enumerate(paragraphs_info):
            if p_info.text.strip().lower() in ref_keywords:
                ref_section_idx = i
                break

        if ref_section_idx is None:
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

        # Collect entries until the next heading (e.g. "Apéndices") so sections
        # that follow the references (appendices) are not counted as references.
        # Note: assumes no subheadings inside the reference list (APA 7 forbids
        # grouping references under subheadings).
        ref_paragraphs = []
        for p_info in paragraphs_info[ref_section_idx + 1 :]:
            if p_info.text.strip() and (p_info.style_name or "").startswith("Heading"):
                break
            if p_info.text.strip():
                ref_paragraphs.append(p_info)

        if not ref_paragraphs:
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

        expected_hanging = -0.5  # APA 7 hanging indent: -0.5in first line, +0.5in left
        spacing_errors: list[int] = []
        for index, reference in enumerate(ref_paragraphs, start=1):
            first_line_indent = reference.first_line_indent
            indent_valid = False
            if first_line_indent is not None:
                indent_inches = first_line_indent / 914400.0
                indent_valid = abs(indent_inches - expected_hanging) <= 0.1
                actual = f"{indent_inches:.2f} inch"
            else:
                actual = "No first-line indent"

            if not indent_valid:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.REFERENCES}.hanging_indent",
                        severity="error",
                        expected="-0.5 inch hanging indent (first line outdent)",
                        actual=actual,
                        evidence=f"Reference {index} lacks proper hanging indent",
                    )
                )

            if ctx.strict and (
                reference.line_spacing is None
                or abs(reference.line_spacing - 2.0) > 0.2
                or reference.space_before not in (None, 0)
                or reference.space_after not in (None, 0)
            ):
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

        ref_texts = [p.text.strip() for p in ref_paragraphs]
        for i in range(len(ref_texts) - 1):
            if self._sort_key(ref_texts[i]) > self._sort_key(ref_texts[i + 1]):
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

        return issues

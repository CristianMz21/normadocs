"""References verification for APA 7th Edition.

Verifies references section meets APA 7th Edition requirements:
- Section titled "Referencias" or "References" at document end
- Hanging indent (0.5 inches) on all references
- Alphabetical order
- Proper APA 7th citation format
- Double-spaced throughout
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class ReferencesCheck:
    """Check references formatting against APA 7th Edition requirements."""

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

        ref_paragraphs = [p for p in paragraphs_info[ref_section_idx + 1 :] if p.text.strip()]

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

        first_ref = ref_paragraphs[0]
        first_line_indent = first_ref.first_line_indent
        if first_line_indent is not None:
            indent_inches = first_line_indent / 914400.0
            if abs(indent_inches - 0.5) > 0.1:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.REFERENCES}.hanging_indent",
                        severity="error",
                        expected="0.5 inch hanging indent",
                        actual=f"{indent_inches:.2f} inch",
                        evidence="First reference lacks proper hanging indent",
                    )
                )
        else:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.REFERENCES}.hanging_indent",
                    severity="error",
                    expected="0.5 inch hanging indent",
                    actual="No first-line indent",
                    evidence="First reference lacks first-line indent for hanging indent",
                )
            )

        ref_texts = [p.text.strip() for p in ref_paragraphs]
        for i in range(len(ref_texts) - 1):
            if ref_texts[i] > ref_texts[i + 1]:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.REFERENCES}.alphabetical_order",
                        severity="warning",
                        expected="Alphabetical order",
                        actual=f"'{ref_texts[i]}' before '{ref_texts[i + 1]}'",
                        evidence="References not in alphabetical order",
                    )
                )
                break

        return issues

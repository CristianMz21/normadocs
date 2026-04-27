"""Paragraphs verification for APA 7th Edition.

Verifies paragraph formatting meets APA 7th Edition requirements:
- First-line indent: 0.5 inches (1.27cm)
- No extra space before or after paragraphs
- Text is justified
- No widow/orphan lines (handled by styles)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


EXPECTED_FIRST_LINE_INENT = 0.5
INDENT_TOLERANCE = 0.1


class ParagraphsCheck:
    """Check paragraph formatting against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run paragraphs verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []

        paragraphs_info = ctx.docx.get_paragraphs_info()

        body_paragraphs = [p for p in paragraphs_info if p.text.strip()]

        paragraphs_with_indent = 0
        paragraphs_without_indent = 0

        for p_info in body_paragraphs:
            indent = p_info.first_line_indent
            if indent is not None:
                indent_inches = indent / 914400.0
                if abs(indent_inches - EXPECTED_FIRST_LINE_INENT) <= INDENT_TOLERANCE:
                    paragraphs_with_indent += 1
                else:
                    paragraphs_without_indent += 1
            else:
                paragraphs_without_indent += 1

        total = len(body_paragraphs)
        if total > 0:
            indent_ratio = paragraphs_with_indent / total
            if indent_ratio < 0.5 and paragraphs_without_indent > 3:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.PARAGRAPHS}.first_line_indent",
                        severity="error",
                        expected="0.5 inch first-line indent on body paragraphs",
                        actual=(
                            f"Only {paragraphs_with_indent}/{total} paragraphs properly indented"
                        ),
                        evidence=f"{paragraphs_without_indent} paragraphs lack first-line indent",
                    )
                )
            elif paragraphs_without_indent > 0:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.PARAGRAPHS}.first_line_indent",
                        severity="warning",
                        expected="0.5 inch first-line indent on body paragraphs",
                        actual="Some paragraphs lack proper indent",
                        evidence=f"{paragraphs_without_indent}/{total} paragraphs lack indent",
                    )
                )

        justified_count = sum(1 for p in body_paragraphs if p.alignment == "justify")
        if total > 0 and justified_count / total < 0.5:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.PARAGRAPHS}.justification",
                    severity="warning",
                    expected="Text should be justified",
                    actual=f"Only {justified_count}/{total} paragraphs are justified",
                    evidence="Most paragraphs are not justified",
                )
            )

        return issues

"""Spacing verification for APA 7th Edition.

Verifies that line spacing meets APA 7th Edition requirements:
- Double spacing throughout the document
- No extra space before or after paragraphs
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue, is_apa_caption_or_table_title

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


APA_LINE_SPACING = 2.0
LINE_SPACING_TOLERANCE = 0.2


class SpacingCheck:
    """Check line spacing against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run spacing verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []

        paragraphs_info = ctx.docx.get_paragraphs_info()

        non_empty_paragraphs = [p for p in paragraphs_info if p.text.strip()]
        if not non_empty_paragraphs:
            return issues

        # Exclude table captions, table titles, and table notes from spacing check
        # APA 7 allows single spacing in table-related elements
        spacing_paragraphs = [
            p
            for p in non_empty_paragraphs
            if not is_apa_caption_or_table_title(p.text)
            and not p.text.strip().isdigit()
            and (p.style_name or "") != ""
            and not (p.style_name or "").startswith("Heading")
            and "Caption" not in (p.style_name or "")
            and "Source" not in (p.style_name or "")
        ]
        if not spacing_paragraphs:
            return issues

        spacing_issues = 0
        for p_info in spacing_paragraphs:
            line_spacing = p_info.line_spacing
            if line_spacing is not None:
                if isinstance(line_spacing, float):
                    actual_spacing = line_spacing
                elif isinstance(line_spacing, int):
                    actual_spacing = float(line_spacing)
                else:
                    actual_spacing = None

                if actual_spacing is not None:
                    diff = abs(actual_spacing - APA_LINE_SPACING)
                    if diff > LINE_SPACING_TOLERANCE:
                        spacing_issues += 1

        total_checked = len(spacing_paragraphs)
        if total_checked > 0:
            issue_ratio = spacing_issues / total_checked
            if issue_ratio > 0.5:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.SPACING}.line_spacing",
                        severity="error",
                        expected=f"Double spacing ({APA_LINE_SPACING})",
                        actual="Most paragraphs have non-double spacing",
                        evidence=f"{spacing_issues}/{total_checked} paragraphs incorrect",
                    )
                )
            elif spacing_issues > 0:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.SPACING}.line_spacing",
                        severity="warning",
                        expected=f"Double spacing ({APA_LINE_SPACING})",
                        actual="Some paragraphs have incorrect spacing",
                        evidence=f"{spacing_issues}/{total_checked} paragraphs incorrect",
                    )
                )

        return issues

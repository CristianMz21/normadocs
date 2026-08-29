"""Spacing verification for APA 7th Edition.

Verifies that line spacing meets APA 7th Edition requirements:
- Double spacing throughout the document
- No extra space before or after paragraphs
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import (
    CheckCategory,
    VerificationIssue,
    caption_and_title_indexes,
    is_apa_caption_or_table_title,
)

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext
    from ..docx_analyzer import DOCXParagraphInfo


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
        skip_indexes = caption_and_title_indexes(paragraphs_info)
        spacing_paragraphs = self._collect_spacing_paragraphs(paragraphs_info, skip_indexes, ctx)
        if not spacing_paragraphs:
            return issues
        spacing_issues, paragraph_spacing_issues = self._count_spacing_issues(
            spacing_paragraphs, ctx
        )
        self._report_spacing(
            spacing_paragraphs, spacing_issues, paragraph_spacing_issues, ctx, issues
        )
        return issues

    def _collect_spacing_paragraphs(
        self,
        paragraphs_info: list[DOCXParagraphInfo],
        skip_indexes: set[int],
        ctx: VerificationContext,
    ) -> list[DOCXParagraphInfo]:
        result: list[DOCXParagraphInfo] = []
        for i, p in enumerate(paragraphs_info):
            if self._should_skip_spacing_paragraph(p, i, skip_indexes, ctx):
                continue
            result.append(p)
        return result

    def _should_skip_spacing_paragraph(
        self,
        p: DOCXParagraphInfo,
        index: int,
        skip_indexes: set[int],
        ctx: VerificationContext,
    ) -> bool:
        if index in skip_indexes:
            return True
        if not p.text.strip():
            return True
        if is_apa_caption_or_table_title(p.text):
            return True
        if p.text.strip().isdigit():
            return True
        style = p.style_name or ""
        if not style:
            return True
        if not ctx.strict and style.startswith("Heading"):
            return True
        return "Caption" in style or "Source" in style

    def _count_spacing_issues(
        self,
        spacing_paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
    ) -> tuple[int, int]:
        spacing_issues = 0
        paragraph_spacing_issues = 0
        for p_info in spacing_paragraphs:
            if self._has_line_spacing_issue(p_info, ctx):
                spacing_issues += 1
            paragraph_spacing_issues += self._count_paragraph_spacing_for_para(p_info, ctx)
        return spacing_issues, paragraph_spacing_issues

    def _count_paragraph_spacing_for_para(
        self, p_info: DOCXParagraphInfo, ctx: VerificationContext
    ) -> int:
        if not ctx.strict:
            return 0
        count = 0
        for value in (p_info.space_before, p_info.space_after):
            if value is not None and abs(float(value) / 12700.0) > 0.01:
                count += 1
        return count

    def _has_line_spacing_issue(self, p_info: DOCXParagraphInfo, ctx: VerificationContext) -> bool:
        line_spacing = p_info.line_spacing
        if line_spacing is None:
            return False
        actual = self._to_float_spacing(line_spacing)
        if actual is None:
            return bool(ctx.strict)
        return abs(actual - APA_LINE_SPACING) > LINE_SPACING_TOLERANCE

    def _to_float_spacing(self, line_spacing: float | int | None) -> float | None:
        if isinstance(line_spacing, float):
            return line_spacing
        if isinstance(line_spacing, int):
            return float(line_spacing)
        return None

    def _report_spacing(
        self,
        spacing_paragraphs: list[DOCXParagraphInfo],
        spacing_issues: int,
        paragraph_spacing_issues: int,
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        total_checked = len(spacing_paragraphs)
        if total_checked == 0:
            return
        if ctx.strict and (spacing_issues or paragraph_spacing_issues):
            self._report_strict_spacing(
                total_checked, spacing_issues, paragraph_spacing_issues, issues
            )
            return
        self._report_loose_spacing(total_checked, spacing_issues, issues)

    def _report_strict_spacing(
        self,
        total_checked: int,
        spacing_issues: int,
        paragraph_spacing_issues: int,
        issues: list[VerificationIssue],
    ) -> None:
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.SPACING}.strict_spacing",
                severity="error",
                expected="Double spacing with 0pt before and after",
                actual=(
                    f"{spacing_issues} line-spacing and "
                    f"{paragraph_spacing_issues} paragraph-spacing violations"
                ),
                evidence=(
                    f"Checked {total_checked} non-caption paragraphs without "
                    "allowing a majority-compliant document"
                ),
            )
        )

    def _report_loose_spacing(
        self,
        total_checked: int,
        spacing_issues: int,
        issues: list[VerificationIssue],
    ) -> None:
        issue_ratio = spacing_issues / total_checked if total_checked else 0
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
            return
        if spacing_issues > 0:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.SPACING}.line_spacing",
                    severity="warning",
                    expected=f"Double spacing ({APA_LINE_SPACING})",
                    actual="Some paragraphs have incorrect spacing",
                    evidence=f"{spacing_issues}/{total_checked} paragraphs incorrect",
                )
            )

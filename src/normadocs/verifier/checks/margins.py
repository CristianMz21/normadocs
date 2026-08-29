"""Margins verification for APA 7th Edition.

Verifies that document margins meet APA 7th Edition requirements:
- All margins (top, bottom, left, right) must be exactly 1 inch.
- Page size must be Letter (8.5" x 11").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue
from ..docx_analyzer import DOCXPageInfo

if TYPE_CHECKING:
    from docx.section import Section

    from ..apa_verifier import VerificationContext


MARGIN_TOLERANCE = 0.05
APA_MARGIN = 1.0
APA_PAGE_WIDTH = 8.5
APA_PAGE_HEIGHT = 11.0


class MarginsCheck:
    """Check margins and page size against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run margins verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []
        docx_info = ctx.docx.get_page_info()
        self._check_primary_margins(docx_info, issues)
        self._check_page_size(docx_info, issues)
        if ctx.strict:
            self._check_additional_sections(ctx, issues)
        return issues

    def _check_primary_margins(
        self, docx_info: DOCXPageInfo, issues: list[VerificationIssue]
    ) -> None:
        margins = docx_info.margins
        expected_margins = {
            "top": APA_MARGIN,
            "bottom": APA_MARGIN,
            "left": APA_MARGIN,
            "right": APA_MARGIN,
        }
        actual_margins = {
            "top": margins[0],
            "bottom": margins[2],
            "left": margins[3],
            "right": margins[1],
        }
        for margin_name, expected in expected_margins.items():
            self._check_single_margin(margin_name, expected, actual_margins[margin_name], issues)

    def _check_single_margin(
        self, margin_name: str, expected: float, actual: float, issues: list[VerificationIssue]
    ) -> None:
        diff = abs(actual - expected)
        if diff > MARGIN_TOLERANCE:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.MARGINS}.{margin_name}",
                    severity="error",
                    expected=f"{expected:.2f} inches",
                    actual=f"{actual:.2f} inches",
                    evidence=f"Margin '{margin_name}' = {actual:.2f}\" (exp {expected:.2f}\")",
                )
            )
            return
        if diff > MARGIN_TOLERANCE * 0.5:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.MARGINS}.{margin_name}",
                    severity="warning",
                    expected=f"{expected:.2f} inches",
                    actual=f"{actual:.2f} inches",
                    evidence=f"Margin '{margin_name}' = {actual:.2f}\" (exp {expected:.2f}\")",
                )
            )

    def _check_page_size(self, docx_info: DOCXPageInfo, issues: list[VerificationIssue]) -> None:
        self._check_width(docx_info.page_width, issues)
        self._check_height(docx_info.page_height, issues)

    def _check_width(self, page_width: float, issues: list[VerificationIssue]) -> None:
        if abs(page_width - APA_PAGE_WIDTH) <= 0.1:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.MARGINS}.page_width",
                severity="error",
                expected=f"{APA_PAGE_WIDTH:.1f} inches (Letter)",
                actual=f"{page_width:.2f} inches",
                evidence=f'Page width is {page_width:.2f}" (expected {APA_PAGE_WIDTH:.1f}")',
            )
        )

    def _check_height(self, page_height: float, issues: list[VerificationIssue]) -> None:
        if abs(page_height - APA_PAGE_HEIGHT) <= 0.1:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.MARGINS}.page_height",
                severity="error",
                expected=f"{APA_PAGE_HEIGHT:.1f} inches (Letter)",
                actual=f"{page_height:.2f} inches",
                evidence=f'Page height is {page_height:.2f}" (expected {APA_PAGE_HEIGHT:.1f}")',
            )
        )

    def _check_additional_sections(
        self, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        for section_index, section in enumerate(ctx.docx.doc.sections[1:], start=2):
            self._check_section_margins(section, section_index, issues)
            self._check_section_page_size(section, section_index, issues)

    def _check_section_margins(
        self, section: Section, section_index: int, issues: list[VerificationIssue]
    ) -> None:
        section_margins = {
            "top": int(section.top_margin or 0) / 914400.0,
            "bottom": int(section.bottom_margin or 0) / 914400.0,
            "left": int(section.left_margin or 0) / 914400.0,
            "right": int(section.right_margin or 0) / 914400.0,
        }
        for margin_name, actual in section_margins.items():
            if abs(actual - APA_MARGIN) <= MARGIN_TOLERANCE:
                continue
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.MARGINS}.section_{section_index}_{margin_name}",
                    severity="error",
                    expected=f"{APA_MARGIN:.2f} inches",
                    actual=f"{actual:.2f} inches",
                    evidence=f"Section {section_index} has a non-APA {margin_name} margin",
                )
            )

    def _check_section_page_size(
        self, section: Section, section_index: int, issues: list[VerificationIssue]
    ) -> None:
        width = int(section.page_width or 0) / 914400.0
        height = int(section.page_height or 0) / 914400.0
        self._check_section_width(width, section_index, issues)
        self._check_section_height(height, section_index, issues)

    def _check_section_width(
        self, width: float, section_index: int, issues: list[VerificationIssue]
    ) -> None:
        if abs(width - APA_PAGE_WIDTH) <= 0.1:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.MARGINS}.section_{section_index}_page_width",
                severity="error",
                expected=f"{APA_PAGE_WIDTH:.1f} inches (Letter)",
                actual=f"{width:.2f} inches",
                evidence=f"Section {section_index} is not Letter width",
            )
        )

    def _check_section_height(
        self, height: float, section_index: int, issues: list[VerificationIssue]
    ) -> None:
        if abs(height - APA_PAGE_HEIGHT) <= 0.1:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.MARGINS}.section_{section_index}_page_height",
                severity="error",
                expected=f"{APA_PAGE_HEIGHT:.1f} inches (Letter)",
                actual=f"{height:.2f} inches",
                evidence=f"Section {section_index} is not Letter height",
            )
        )

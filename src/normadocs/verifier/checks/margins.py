"""Margins verification for APA 7th Edition.

Verifies that document margins meet APA 7th Edition requirements:
- All margins (top, bottom, left, right) must be exactly 1 inch.
- Page size must be Letter (8.5" x 11").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
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
        margins = docx_info.margins
        page_width = docx_info.page_width
        page_height = docx_info.page_height

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
            actual = actual_margins[margin_name]
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
            elif diff > MARGIN_TOLERANCE * 0.5:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.MARGINS}.{margin_name}",
                        severity="warning",
                        expected=f"{expected:.2f} inches",
                        actual=f"{actual:.2f} inches",
                        evidence=f"Margin '{margin_name}' = {actual:.2f}\" (exp {expected:.2f}\")",
                    )
                )

        if abs(page_width - APA_PAGE_WIDTH) > 0.1:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.MARGINS}.page_width",
                    severity="error",
                    expected=f"{APA_PAGE_WIDTH:.1f} inches (Letter)",
                    actual=f"{page_width:.2f} inches",
                    evidence=f'Page width is {page_width:.2f}" (expected {APA_PAGE_WIDTH:.1f}")',
                )
            )

        if abs(page_height - APA_PAGE_HEIGHT) > 0.1:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.MARGINS}.page_height",
                    severity="error",
                    expected=f"{APA_PAGE_HEIGHT:.1f} inches (Letter)",
                    actual=f"{page_height:.2f} inches",
                    evidence=f'Page height is {page_height:.2f}" (expected {APA_PAGE_HEIGHT:.1f}")',
                )
            )

        # A DOCX may contain multiple sections with independent page setup.
        # Strict validation checks every section rather than trusting section 1.
        if ctx.strict:
            for section_index, section in enumerate(ctx.docx.doc.sections[1:], start=2):
                section_margins = {
                    "top": int(section.top_margin or 0) / 914400.0,
                    "bottom": int(section.bottom_margin or 0) / 914400.0,
                    "left": int(section.left_margin or 0) / 914400.0,
                    "right": int(section.right_margin or 0) / 914400.0,
                }
                for margin_name, actual in section_margins.items():
                    if abs(actual - APA_MARGIN) > MARGIN_TOLERANCE:
                        issues.append(
                            VerificationIssue(
                                check=f"{CheckCategory.MARGINS}.section_{section_index}_{margin_name}",
                                severity="error",
                                expected=f"{APA_MARGIN:.2f} inches",
                                actual=f"{actual:.2f} inches",
                                evidence=(
                                    f"Section {section_index} has a non-APA {margin_name} margin"
                                ),
                            )
                        )
                section_width = int(section.page_width or 0) / 914400.0
                section_height = int(section.page_height or 0) / 914400.0
                if abs(section_width - APA_PAGE_WIDTH) > 0.1:
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.MARGINS}.section_{section_index}_page_width",
                            severity="error",
                            expected=f"{APA_PAGE_WIDTH:.1f} inches (Letter)",
                            actual=f"{section_width:.2f} inches",
                            evidence=f"Section {section_index} is not Letter width",
                        )
                    )
                if abs(section_height - APA_PAGE_HEIGHT) > 0.1:
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.MARGINS}.section_{section_index}_page_height",
                            severity="error",
                            expected=f"{APA_PAGE_HEIGHT:.1f} inches (Letter)",
                            actual=f"{section_height:.2f} inches",
                            evidence=f"Section {section_index} is not Letter height",
                        )
                    )

        return issues

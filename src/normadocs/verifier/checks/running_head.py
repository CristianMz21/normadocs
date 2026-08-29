"""Running head verification for APA 7th Edition.

Verifies that the student-paper header meets APA 7th Edition requirements:
- Page number appears on every page, including the cover
- Student papers omit running-head text unless explicitly requested
- Professional papers may include a short title in ALL CAPS on pages 2+
- Format: page number only, or "SHORT TITLE                                     1"
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


MAX_RUNNING_HEAD_LENGTH = 50


class RunningHeadCheck:
    """Check running head against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run running head verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []
        self._check_different_first_page(ctx, issues)
        default_header = ctx.docx.get_header_text("default")
        first_page_header = ctx.docx.get_header_text("first")
        self._check_default_header(default_header, ctx, issues)
        self._check_first_page_header(first_page_header, issues)
        return issues

    def _check_different_first_page(
        self, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        docx_info = ctx.docx.get_page_info()
        if docx_info.has_different_first_page_header_footer:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.RUNNING_HEAD}.different_first_page",
                severity="error",
                expected="different_first_page_header_footer = True",
                actual="False",
                evidence="Document does not have different first page header/footer enabled",
            )
        )

    def _check_default_header(
        self, default_header: str, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        if not default_header.strip():
            self._report_missing_default_header(ctx, issues)
            return
        if ctx.meta.short_title:
            self._check_short_title(default_header, ctx, issues)
            self._check_page_number_professional(default_header, ctx, issues)
        else:
            self._check_student_header(default_header, issues)

    def _report_missing_default_header(
        self, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        expected_header = (
            "Running head with short title and page number"
            if ctx.meta.short_title
            else "Page number only"
        )
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.RUNNING_HEAD}.missing_on_pages_2+",
                severity="error",
                expected=expected_header,
                actual="Empty header",
                evidence="Pages 2+ have no page number header",
            )
        )

    def _check_short_title(
        self, default_header: str, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        if not ctx.meta.short_title:
            return
        expected_short = ctx.meta.short_title.upper()
        if len(expected_short) > MAX_RUNNING_HEAD_LENGTH:
            expected_short = expected_short[:MAX_RUNNING_HEAD_LENGTH]
        if expected_short in default_header.upper():
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.RUNNING_HEAD}.short_title_content",
                severity="error",
                expected=f"'{expected_short}' in running head",
                actual=f"'{default_header}'",
                evidence=f"Running head missing '{expected_short}'",
            )
        )

    def _check_page_number_professional(
        self, default_header: str, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        if not ctx.meta.short_title:
            return
        if "PAGE" in default_header.upper() or default_header.strip().isdigit():
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.RUNNING_HEAD}.page_number",
                severity="error",
                expected="Page number in header",
                actual="No page number found",
                evidence="Header lacks page number",
            )
        )

    def _check_student_header(self, default_header: str, issues: list[VerificationIssue]) -> None:
        normalized_header = " ".join(default_header.split()).upper()
        if normalized_header == "PAGE" or normalized_header.isdigit():
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.RUNNING_HEAD}.student_header_content",
                severity="error",
                expected="Only the page number in the header",
                actual=f"'{default_header}'",
                evidence="Student APA header contains text besides the page number",
            )
        )

    def _check_first_page_header(
        self, first_page_header: str, issues: list[VerificationIssue]
    ) -> None:
        normalized_first = " ".join(first_page_header.split()).upper()
        if normalized_first and normalized_first in {"PAGE", "1"}:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.RUNNING_HEAD}.present_on_cover",
                severity="error",
                expected="Page number only on cover page",
                actual=f"'{first_page_header}'",
                evidence="Cover page header contains running-head text",
            )
        )

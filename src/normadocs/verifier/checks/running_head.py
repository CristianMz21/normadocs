"""Running head verification for APA 7th Edition.

Verifies that the running head meets APA 7th Edition requirements:
- Appears on all pages except the first (cover page)
- Left side: Short title in ALL CAPS (max 50 characters)
- Right side: Page number
- Format: "SHORT TITLE                                     1"
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

        docx_info = ctx.docx.get_page_info()

        if not docx_info.has_different_first_page_header_footer:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.RUNNING_HEAD}.different_first_page",
                    severity="error",
                    expected="different_first_page_header_footer = True",
                    actual="False",
                    evidence="Document does not have different first page header/footer enabled",
                )
            )

        default_header = ctx.docx.get_header_text("default")
        first_page_header = ctx.docx.get_header_text("first")

        if not default_header.strip():
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.RUNNING_HEAD}.missing_on_pages_2+",
                    severity="error",
                    expected="Running head with short title and page number",
                    actual="Empty header",
                    evidence="Pages 2+ have no running head in header",
                )
            )
        else:
            if ctx.meta.short_title:
                expected_short = ctx.meta.short_title.upper()
                if len(expected_short) > MAX_RUNNING_HEAD_LENGTH:
                    expected_short = expected_short[:MAX_RUNNING_HEAD_LENGTH]

                if expected_short not in default_header.upper():
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.RUNNING_HEAD}.short_title_content",
                            severity="error",
                            expected=f"'{expected_short}' in running head",
                            actual=f"'{default_header}'",
                            evidence=f"Running head missing '{expected_short}'",
                        )
                    )

            if "PAGE" not in default_header.upper() and "1" not in default_header:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.RUNNING_HEAD}.page_number",
                        severity="error",
                        expected="Page number in running head",
                        actual="No page number found",
                        evidence="Running head header lacks page number",
                    )
                )

        if first_page_header.strip():
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.RUNNING_HEAD}.present_on_cover",
                    severity="error",
                    expected="No running head on cover page (page 1)",
                    actual="Running head present",
                    evidence=f"Cover page header contains: '{first_page_header}'",
                )
            )

        return issues

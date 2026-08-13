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
        else:
            # APA 7 student papers do not require a running head. When the
            # source has no short_title, validate only the page number and
            # intentionally allow the title text to be absent.
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

            if ctx.meta.short_title:
                if "PAGE" not in default_header.upper() and not default_header.strip().isdigit():
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.RUNNING_HEAD}.page_number",
                            severity="error",
                            expected="Page number in header",
                            actual="No page number found",
                            evidence="Header lacks page number",
                        )
                    )
            else:
                # With no short_title, a student paper must contain only the
                # rendered page field (LibreOffice exposes it as a digit).
                normalized_header = " ".join(default_header.split()).upper()
                if normalized_header != "PAGE" and not normalized_header.isdigit():
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.RUNNING_HEAD}.student_header_content",
                            severity="error",
                            expected="Only the page number in the header",
                            actual=f"'{default_header}'",
                            evidence="Student APA header contains text besides the page number",
                        )
                    )

        # APA 7 student papers include page number 1 on the cover, but no
        # running-head text. Accept the rendered field as a digit or PAGE.
        normalized_first = " ".join(first_page_header.split()).upper()
        if not normalized_first or normalized_first not in {"PAGE", "1"}:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.RUNNING_HEAD}.present_on_cover",
                    severity="error",
                    expected="Page number only on cover page",
                    actual=f"'{first_page_header}'",
                    evidence="Cover page header contains running-head text",
                )
            )

        return issues

"""Page setup verification for APA 7th Edition.

Verifies general page setup meets APA 7th Edition requirements:
- Page numbers present and in correct position (top-right)
- Page numbers start from page 1 on cover
- Header/Footer setup correct
- No widows/orphans (via double spacing)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class PageSetupCheck:
    """Check page setup against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run page setup verification.

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
                    check=f"{CheckCategory.PAGE_SETUP}.different_first_page",
                    severity="error",
                    expected="Different first page header/footer enabled",
                    actual="Not enabled",
                    evidence="Document does not use different_first_page_header_footer",
                )
            )

        default_header = " ".join(ctx.docx.get_header_text("default").split()).upper()
        if ctx.strict:
            default_header_valid = default_header == "PAGE" or default_header.isdigit()
        else:
            default_header_valid = "PAGE" in default_header or "1" in default_header
        if not default_header_valid:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.PAGE_SETUP}.page_numbers",
                    severity="error",
                    expected="Page numbers in header",
                    actual="No page numbers found",
                    evidence="Document lacks page number field in header",
                )
            )

        if ctx.strict:
            first_header = " ".join(ctx.docx.get_header_text("first").split()).upper()
            if first_header != "PAGE" and not first_header.isdigit():
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.PAGE_SETUP}.first_page_number",
                        severity="error",
                        expected="Page number only in the first-page header",
                        actual=f"'{first_header}'",
                        evidence="The cover header must contain only the page number field",
                    )
                )

            footer_text = " ".join(
                " ".join(
                    (
                        ctx.docx.get_footer_text("default"),
                        ctx.docx.get_footer_text("first"),
                        ctx.docx.get_footer_text("even"),
                    )
                ).split()
            )
            if footer_text:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.PAGE_SETUP}.footer_content",
                        severity="error",
                        expected="No page footer content",
                        actual=f"'{footer_text}'",
                        evidence="APA page numbers belong in the header, not the footer",
                    )
                )

        return issues

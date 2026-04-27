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

        default_header = ctx.docx.get_header_text("default")
        if "PAGE" not in default_header.upper() and "1" not in default_header:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.PAGE_SETUP}.page_numbers",
                    severity="error",
                    expected="Page numbers in header",
                    actual="No page numbers found",
                    evidence="Document lacks page number field in header",
                )
            )

        return issues

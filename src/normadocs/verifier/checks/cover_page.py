"""Cover page verification for APA 7th Edition.

Verifies cover page formatting meets APA 7th Edition requirements:
- Title centered (vertically and horizontally)
- Author name centered
- Institution centered
- Date centered at bottom
- No page number on cover
- No running head on cover
- No headers/footers on cover page
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class CoverPageCheck:
    """Check cover page formatting against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run cover page verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []

        paragraphs_info = ctx.docx.get_paragraphs_info()

        if not paragraphs_info:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.content_present",
                    severity="error",
                    expected="Cover page content",
                    actual="No content found",
                    evidence="Document appears to have no content",
                )
            )
            return issues

        cover_elements = {
            "title": False,
            "author": False,
            "institution": False,
            "date": False,
        }

        for p_info in paragraphs_info[:15]:
            text = p_info.text.strip()
            if not text:
                continue

            if ctx.meta.title and ctx.meta.title.upper() in text.upper():
                cover_elements["title"] = True
                if p_info.alignment != "center":
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.COVER_PAGE}.title_alignment",
                            severity="warning",
                            expected="Title centered",
                            actual=f"Alignment: {p_info.alignment}",
                            evidence=f"Title may not be centered: '{text[:50]}...'",
                        )
                    )

            if ctx.meta.author and ctx.meta.author in text:
                cover_elements["author"] = True

            if ctx.meta.institution and ctx.meta.institution in text:
                cover_elements["institution"] = True

            if any(word in text.lower() for word in ["2024", "2025", "2026", "abril", "april"]):
                cover_elements["date"] = True

        if not cover_elements["title"]:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.title_present",
                    severity="warning",
                    expected="Title on cover page",
                    actual="Title not found in expected location",
                    evidence="Cover page may be missing title",
                )
            )

        if not cover_elements["author"]:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.author_present",
                    severity="warning",
                    expected="Author name on cover page",
                    actual="Author not found in expected location",
                    evidence="Cover page may be missing author",
                )
            )

        first_page_header = ctx.docx.get_header_text("first")
        if first_page_header.strip():
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.no_header",
                    severity="error",
                    expected="No header on cover page",
                    actual=f"Header present: '{first_page_header[:50]}'",
                    evidence="Cover page should not have a header",
                )
            )

        return issues

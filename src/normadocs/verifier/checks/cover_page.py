"""Cover page verification for APA 7th Edition.

Verifies cover page formatting meets APA 7th Edition requirements:
- Title centered (vertically and horizontally)
- Author name centered
- Institution centered
- Date centered at bottom
- Page number 1 in the cover header
- No running-head text on cover
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal

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

        first_heading_index = next(
            (
                i
                for i, p in enumerate(paragraphs_info)
                if p.style_name == "Heading 1" and p.text.strip()
            ),
            len(paragraphs_info),
        )
        cover_elements = {
            "title": False,
            "author": False,
            "institution": False,
            "date": False,
        }

        for p_info in paragraphs_info[:first_heading_index]:
            text = p_info.text.strip()
            if not text:
                continue

            if ctx.meta.title and ctx.meta.title.upper() in text.upper():
                cover_elements["title"] = True
                if p_info.alignment != "center":
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.COVER_PAGE}.title_alignment",
                            severity="error",
                            expected="Title centered",
                            actual=f"Alignment: {p_info.alignment}",
                            evidence=f"Title is not centered: '{text[:50]}...'",
                        )
                    )
                if not any(bool(run.get("bold")) for run in p_info.runs):
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.COVER_PAGE}.title_bold",
                            severity="error",
                            expected="Title in bold",
                            actual="Title is not bold",
                            evidence=f"Cover title lacks bold formatting: '{text[:50]}...'",
                        )
                    )

            if ctx.meta.author and ctx.meta.author in text:
                cover_elements["author"] = True
                if ctx.strict and p_info.alignment != "center":
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.COVER_PAGE}.author_alignment",
                            severity="error",
                            expected="Author centered",
                            actual=f"Alignment: {p_info.alignment}",
                            evidence=f"Author is not centered: '{text[:50]}...'",
                        )
                    )

            institution_values = [ctx.meta.institution, ctx.meta.affiliation]
            if any(value and value in text for value in institution_values):
                cover_elements["institution"] = True
                if ctx.strict and p_info.alignment != "center":
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.COVER_PAGE}.affiliation_alignment",
                            severity="error",
                            expected="Institutional affiliation centered",
                            actual=f"Alignment: {p_info.alignment}",
                            evidence=f"Affiliation is not centered: '{text[:50]}...'",
                        )
                    )

            date_present = (
                bool(ctx.meta.date and ctx.meta.date in text)
                if ctx.meta.date
                else bool(re.search(r"\b(?:19|20)\d{2}\b", text))
            )
            if date_present:
                cover_elements["date"] = True

        missing_severity: Literal["error", "warning"] = "error" if ctx.strict else "warning"
        if not cover_elements["title"]:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.title_present",
                    severity=missing_severity,
                    expected="Title on cover page",
                    actual="Title not found in expected location",
                    evidence="Cover page may be missing title",
                )
            )

        if not cover_elements["author"] and (not ctx.strict or ctx.meta.author):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.author_present",
                    severity=missing_severity,
                    expected="Author name on cover page",
                    actual="Author not found in expected location",
                    evidence="Cover page may be missing author",
                )
            )

        if (
            ctx.strict
            and (ctx.meta.institution or ctx.meta.affiliation)
            and not cover_elements["institution"]
        ):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.affiliation_present",
                    severity="error",
                    expected="Institutional affiliation on cover page",
                    actual="Affiliation not found in the cover region",
                    evidence="The configured institutional affiliation is missing from the cover",
                )
            )

        if ctx.strict and ctx.meta.date and not cover_elements["date"]:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.date_present",
                    severity="error",
                    expected="Due date on cover page",
                    actual="Date not found in the cover region",
                    evidence="The configured date is missing from the cover",
                )
            )

        first_page_header = " ".join(ctx.docx.get_header_text("first").split()).upper()
        if not first_page_header or first_page_header not in {"PAGE", "1"}:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.no_header",
                    severity="error",
                    expected="Only page number 1 on cover page",
                    actual=f"Header present: '{first_page_header[:50]}'",
                    evidence=(
                        "Cover page contains running-head text instead of only its page number"
                    ),
                )
            )

        # The title must be repeated exactly in a first-content heading.
        # Locate headings structurally instead of assuming a fixed cover length.
        body_headings = [
            p.text.strip()
            for p in paragraphs_info[first_heading_index:]
            if p.style_name == "Heading 1" and p.text.strip()
        ]
        if (
            ctx.meta.title
            and cover_elements["title"]
            and ctx.meta.title.casefold() not in {heading.casefold() for heading in body_headings}
        ):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.title_repeated",
                    severity="error",
                    expected=f"Repeated title exactly '{ctx.meta.title}'",
                    actual=f"'{body_headings[0] if body_headings else '<missing>'}'",
                    evidence="The title on the first content page differs from the cover title",
                )
            )

        return issues

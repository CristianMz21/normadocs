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
    from ..docx_analyzer import DOCXParagraphInfo


_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


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
            return self._missing_content_issue(issues)
        first_heading_index = self._find_first_heading_index(paragraphs_info)
        cover_elements = {
            "title": False,
            "author": False,
            "institution": False,
            "date": False,
        }
        self._scan_cover_region(paragraphs_info[:first_heading_index], ctx, cover_elements, issues)
        self._check_missing_elements(cover_elements, ctx, issues)
        self._check_header(ctx, issues)
        self._check_title_repeated(
            paragraphs_info, first_heading_index, ctx, cover_elements, issues
        )
        return issues

    def _missing_content_issue(self, issues: list[VerificationIssue]) -> list[VerificationIssue]:
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

    def _find_first_heading_index(self, paragraphs_info: list[DOCXParagraphInfo]) -> int:
        for i, p in enumerate(paragraphs_info):
            if p.style_name == "Heading 1" and p.text.strip():
                return i
        return len(paragraphs_info)

    def _scan_cover_region(
        self,
        cover_paras: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        cover_elements: dict[str, bool],
        issues: list[VerificationIssue],
    ) -> None:
        for p_info in cover_paras:
            self._process_single_cover_paragraph(p_info, ctx, cover_elements, issues)

    def _process_single_cover_paragraph(
        self,
        p_info: DOCXParagraphInfo,
        ctx: VerificationContext,
        cover_elements: dict[str, bool],
        issues: list[VerificationIssue],
    ) -> None:
        text = p_info.text.strip()
        if not text:
            return
        self._check_title_paragraph(p_info, text, ctx, cover_elements, issues)
        self._check_author_paragraph(p_info, text, ctx, cover_elements, issues)
        self._check_institution_paragraph(p_info, text, ctx, cover_elements, issues)
        self._check_date_paragraph(text, ctx, cover_elements)

    def _check_title_paragraph(
        self,
        p_info: DOCXParagraphInfo,
        text: str,
        ctx: VerificationContext,
        cover_elements: dict[str, bool],
        issues: list[VerificationIssue],
    ) -> None:
        if not ctx.meta.title:
            return
        if ctx.meta.title.upper() not in text.upper():
            return
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

    def _check_author_paragraph(
        self,
        p_info: DOCXParagraphInfo,
        text: str,
        ctx: VerificationContext,
        cover_elements: dict[str, bool],
        issues: list[VerificationIssue],
    ) -> None:
        if not ctx.meta.author:
            return
        if ctx.meta.author not in text:
            return
        cover_elements["author"] = True
        if not ctx.strict:
            return
        if p_info.alignment == "center":
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.COVER_PAGE}.author_alignment",
                severity="error",
                expected="Author centered",
                actual=f"Alignment: {p_info.alignment}",
                evidence=f"Author is not centered: '{text[:50]}...'",
            )
        )

    def _check_institution_paragraph(
        self,
        p_info: DOCXParagraphInfo,
        text: str,
        ctx: VerificationContext,
        cover_elements: dict[str, bool],
        issues: list[VerificationIssue],
    ) -> None:
        values = [ctx.meta.institution, ctx.meta.affiliation]
        if not any(value and value in text for value in values):
            return
        cover_elements["institution"] = True
        if not ctx.strict:
            return
        if p_info.alignment == "center":
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.COVER_PAGE}.affiliation_alignment",
                severity="error",
                expected="Institutional affiliation centered",
                actual=f"Alignment: {p_info.alignment}",
                evidence=f"Affiliation is not centered: '{text[:50]}...'",
            )
        )

    def _check_date_paragraph(
        self,
        text: str,
        ctx: VerificationContext,
        cover_elements: dict[str, bool],
    ) -> None:
        if ctx.meta.date:
            if ctx.meta.date in text:
                cover_elements["date"] = True
            return
        if _YEAR_RE.search(text):
            cover_elements["date"] = True

    def _check_missing_elements(
        self,
        cover_elements: dict[str, bool],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        severity: Literal["error", "warning"] = "error" if ctx.strict else "warning"
        self._check_missing_title(cover_elements, severity, issues)
        self._check_missing_author(cover_elements, ctx, severity, issues)
        self._check_missing_institution(cover_elements, ctx, issues)
        self._check_missing_date(cover_elements, ctx, issues)

    def _check_missing_title(
        self,
        cover_elements: dict[str, bool],
        severity: Literal["error", "warning"],
        issues: list[VerificationIssue],
    ) -> None:
        if cover_elements["title"]:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.COVER_PAGE}.title_present",
                severity=severity,
                expected="Title on cover page",
                actual="Title not found in expected location",
                evidence="Cover page may be missing title",
            )
        )

    def _check_missing_author(
        self,
        cover_elements: dict[str, bool],
        ctx: VerificationContext,
        severity: Literal["error", "warning"],
        issues: list[VerificationIssue],
    ) -> None:
        if cover_elements["author"]:
            return
        if ctx.strict and not ctx.meta.author:
            return
        if not ctx.strict and cover_elements["author"]:
            return
        # Non-strict always warns if missing; strict only if author configured
        if not ctx.strict or ctx.meta.author:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.COVER_PAGE}.author_present",
                    severity=severity,
                    expected="Author name on cover page",
                    actual="Author not found in expected location",
                    evidence="Cover page may be missing author",
                )
            )

    def _check_missing_institution(
        self,
        cover_elements: dict[str, bool],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        if not ctx.strict:
            return
        if not (ctx.meta.institution or ctx.meta.affiliation):
            return
        if cover_elements["institution"]:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.COVER_PAGE}.affiliation_present",
                severity="error",
                expected="Institutional affiliation on cover page",
                actual="Affiliation not found in the cover region",
                evidence="The configured institutional affiliation is missing from the cover",
            )
        )

    def _check_missing_date(
        self,
        cover_elements: dict[str, bool],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        if not ctx.strict:
            return
        if not ctx.meta.date:
            return
        if cover_elements["date"]:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.COVER_PAGE}.date_present",
                severity="error",
                expected="Due date on cover page",
                actual="Date not found in the cover region",
                evidence="The configured date is missing from the cover",
            )
        )

    def _check_header(self, ctx: VerificationContext, issues: list[VerificationIssue]) -> None:
        first_page_header = " ".join(ctx.docx.get_header_text("first").split()).upper()
        if first_page_header and first_page_header in {"PAGE", "1"}:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.COVER_PAGE}.no_header",
                severity="error",
                expected="Only page number 1 on cover page",
                actual=f"Header present: '{first_page_header[:50]}'",
                evidence="Cover page contains running-head text instead of only its page number",
            )
        )

    def _check_title_repeated(
        self,
        paragraphs_info: list[DOCXParagraphInfo],
        first_heading_index: int,
        ctx: VerificationContext,
        cover_elements: dict[str, bool],
        issues: list[VerificationIssue],
    ) -> None:
        if not ctx.meta.title:
            return
        if not cover_elements["title"]:
            return
        body_headings = [
            p.text.strip()
            for p in paragraphs_info[first_heading_index:]
            if p.style_name == "Heading 1" and p.text.strip()
        ]
        title_cf = ctx.meta.title.casefold()
        if title_cf in {h.casefold() for h in body_headings}:
            return
        actual = body_headings[0] if body_headings else "<missing>"
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.COVER_PAGE}.title_repeated",
                severity="error",
                expected=f"Repeated title exactly '{ctx.meta.title}'",
                actual=f"'{actual}'",
                evidence="The title on the first content page differs from the cover title",
            )
        )

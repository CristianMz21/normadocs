"""Blank-lines verification for APA 7th Edition.

Reports every empty body paragraph because APA 7 uses paragraph spacing,
not blank paragraphs, to separate blocks. Three intentional blanks are
excluded: page-break carriers before References/Appendices headings,
paragraphs inside the cover region, and blanks adjacent to tables.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from docx.oxml.ns import qn

from ...config import is_section_break_heading
from ...utils.docx_helpers import paragraph_style_name
from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph

    from ..apa_verifier import VerificationContext


class BlankLinesCheck:
    """Check that the body contains no empty paragraphs."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run blank-lines verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []
        paragraphs = ctx.docx.paragraphs
        if not paragraphs:
            return issues
        first_heading = self._find_first_heading_index(paragraphs)
        for i, para in enumerate(paragraphs):
            if para.text.strip():
                continue
            if i < first_heading:
                continue
            if self._is_table_associated(para):
                continue
            if self._is_section_break_carrier(paragraphs, i, para):
                continue
            issues.append(self._blank_issue(i, ctx.strict))
        return issues

    def _find_first_heading_index(self, paragraphs: list[Paragraph]) -> int:
        for i, para in enumerate(paragraphs):
            if paragraph_style_name(para) == "Heading 1" and para.text.strip():
                return i
        return len(paragraphs)

    def _is_table_associated(self, para: Paragraph) -> bool:
        parent = para._element.getparent()
        if parent is None:
            return False
        children = list(parent)
        try:
            idx = children.index(para._element)
        except ValueError:
            return False
        if idx > 0 and children[idx - 1].tag == qn("w:tbl"):
            return True
        return idx + 1 < len(children) and children[idx + 1].tag == qn("w:tbl")

    def _is_section_break_carrier(
        self, paragraphs: list[Paragraph], index: int, para: Paragraph
    ) -> bool:
        if not self._has_page_break(para):
            return False
        for nxt in paragraphs[index + 1 :]:
            if not nxt.text.strip():
                continue
            if not paragraph_style_name(nxt).startswith("Heading"):
                return False
            return is_section_break_heading(nxt.text)
        return False

    def _has_page_break(self, para: Paragraph) -> bool:
        if para.paragraph_format.page_break_before:
            return True
        return any(br.get(qn("w:type")) == "page" for br in para._element.iter(qn("w:br")))

    def _blank_issue(self, index: int, strict: bool) -> VerificationIssue:
        severity: Literal["error", "warning"] = "error" if strict else "warning"
        return VerificationIssue(
            check=f"{CheckCategory.BLANK_LINES}.blank_line",
            severity=severity,
            expected="No blank paragraphs in the body",
            actual="Blank paragraph",
            evidence=f"Empty paragraph at index {index}",
        )

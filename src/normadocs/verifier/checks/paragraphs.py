"""Paragraphs verification for APA 7th Edition.

Verifies paragraph formatting meets APA 7th Edition requirements:
- First-line indent: 0.5 inches (1.27cm)
- No extra space before or after paragraphs
- Left-aligned text with ragged right margin (APA 7 Section 2.21)
- No widow/orphan lines (handled by styles)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .. import (
    CheckCategory,
    VerificationIssue,
    caption_and_title_indexes,
    is_apa_caption_or_table_title,
)
from ..docx_analyzer import DOCXParagraphInfo

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


EXPECTED_FIRST_LINE_INDENT = 0.5
INDENT_TOLERANCE = 0.1


@dataclass
class _FilterState:
    in_abstract: bool = False
    in_references: bool = False
    in_toc: bool = False
    skip_first_body_after_heading: bool = False


class ParagraphsCheck:
    """Check paragraph formatting against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run paragraphs verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []
        paragraphs_info = ctx.docx.get_paragraphs_info()
        skip_indexes = caption_and_title_indexes(paragraphs_info)
        body_paragraphs = self._collect_body_paragraphs(paragraphs_info, skip_indexes)
        if not body_paragraphs:
            return issues
        self._check_indent(body_paragraphs, ctx, issues)
        self._check_alignment(body_paragraphs, ctx, issues)
        return issues

    def _should_skip_body(self, p: DOCXParagraphInfo, state: _FilterState) -> bool:
        if not p.text.strip():
            return True
        if self._handle_abstract_keywords(p, state):
            return True
        if state.in_abstract or state.in_references or state.in_toc:
            return True
        if self._is_skipped_style(p.style_name or ""):
            return True
        if self._is_caption_or_digit(p):
            return True
        if p.alignment == "center":
            return True
        if state.skip_first_body_after_heading:
            state.skip_first_body_after_heading = False
            return True
        return False

    def _collect_body_paragraphs(
        self,
        paragraphs_info: list[DOCXParagraphInfo],
        skip_indexes: set[int],
    ) -> list[DOCXParagraphInfo]:
        state = _FilterState()
        filtered: list[DOCXParagraphInfo] = []
        for i, p in enumerate(paragraphs_info):
            if i in skip_indexes:
                continue
            if self._handle_heading_paragraph(p, state):
                continue
            if self._should_skip_body(p, state):
                continue
            filtered.append(p)
        return filtered

    def _handle_heading_paragraph(self, p: DOCXParagraphInfo, state: _FilterState) -> bool:
        style_name = p.style_name or ""
        if not style_name.startswith("Heading"):
            return False
        text_lower = p.text.strip().lower()
        self._update_heading_state(text_lower, state)
        state.skip_first_body_after_heading = True
        return True

    def _update_heading_state(self, text_lower: str, state: _FilterState) -> None:
        ref_keywords = ("referencias", "references", "bibliografía", "bibliography")
        abstract_keywords = ("resumen", "abstract")
        toc_keywords = ("contenido", "contents", "index", "índice")
        if any(k in text_lower for k in ref_keywords):
            state.in_references = True
            state.in_abstract = False
            state.in_toc = False
            return
        if any(k in text_lower for k in abstract_keywords):
            state.in_abstract = True
            state.in_references = False
            state.in_toc = False
            return
        if any(k in text_lower for k in toc_keywords):
            state.in_toc = True
            state.in_references = False
            state.in_abstract = False
            return
        state.in_references = False
        state.in_abstract = False
        state.in_toc = False

    def _handle_abstract_keywords(self, p: DOCXParagraphInfo, state: _FilterState) -> bool:
        if not state.in_abstract:
            return False
        text_lower = p.text.strip().lower()
        if not text_lower.startswith(("palabras clave", "keywords")):
            return False
        state.in_abstract = False
        return True

    def _is_skipped_style(self, style_name: str) -> bool:
        return (
            "List" in style_name
            or "Caption" in style_name
            or "Compact" in style_name
            or "Source" in style_name
        )

    def _is_caption_or_digit(self, p: DOCXParagraphInfo) -> bool:
        text_stripped = p.text.strip()
        if is_apa_caption_or_table_title(text_stripped):
            return True
        return text_stripped.isdigit()

    def _count_indents(self, body_paragraphs: list[DOCXParagraphInfo]) -> tuple[int, int]:
        with_indent = 0
        without_indent = 0
        for p_info in body_paragraphs:
            if self._has_expected_indent(p_info):
                with_indent += 1
            else:
                without_indent += 1
        return with_indent, without_indent

    def _has_expected_indent(self, p_info: DOCXParagraphInfo) -> bool:
        indent = p_info.first_line_indent
        if indent is None:
            return False
        indent_inches = indent / 914400.0
        return abs(indent_inches - EXPECTED_FIRST_LINE_INDENT) <= INDENT_TOLERANCE

    def _check_indent(
        self,
        body_paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        with_indent, without_indent = self._count_indents(body_paragraphs)
        total = len(body_paragraphs)
        if total == 0:
            return
        if ctx.strict and without_indent > 0:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.PARAGRAPHS}.strict_first_line_indent",
                    severity="error",
                    expected="0.5 inch first-line indent on every body paragraph",
                    actual=(f"{without_indent}/{total} body paragraphs lack the required indent"),
                    evidence="Strict APA validation does not accept partial compliance",
                )
            )
            return
        self._report_indent_ratio(with_indent, without_indent, total, issues)

    def _report_indent_ratio(
        self,
        with_indent: int,
        without_indent: int,
        total: int,
        issues: list[VerificationIssue],
    ) -> None:
        indent_ratio = with_indent / total if total else 0
        if indent_ratio < 0.5 and without_indent > 3:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.PARAGRAPHS}.first_line_indent",
                    severity="error",
                    expected="0.5 inch first-line indent on body paragraphs",
                    actual=f"Only {with_indent}/{total} paragraphs properly indented",
                    evidence=f"{without_indent} paragraphs lack first-line indent",
                )
            )
            return
        if without_indent > 0:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.PARAGRAPHS}.first_line_indent",
                    severity="warning",
                    expected="0.5 inch first-line indent on body paragraphs",
                    actual="Some paragraphs lack proper indent",
                    evidence=f"{without_indent}/{total} paragraphs lack indent",
                )
            )

    def _check_alignment(
        self,
        body_paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        total = len(body_paragraphs)
        if total == 0:
            return
        justified_count = sum(1 for p in body_paragraphs if p.alignment == "left")
        if ctx.strict:
            self._report_strict_alignment(justified_count, total, issues)
            return
        self._report_loose_alignment(justified_count, total, issues)

    def _report_strict_alignment(
        self, justified_count: int, total: int, issues: list[VerificationIssue]
    ) -> None:
        if justified_count >= total:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.PARAGRAPHS}.strict_alignment",
                severity="error",
                expected="Left-aligned body paragraphs",
                actual=f"{total - justified_count}/{total} are not left-aligned",
                evidence="Strict APA validation rejects justified or ambiguous body alignment",
            )
        )

    def _report_loose_alignment(
        self, justified_count: int, total: int, issues: list[VerificationIssue]
    ) -> None:
        if justified_count / total >= 0.5:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.PARAGRAPHS}.justification",
                severity="warning",
                expected="Left-aligned text with ragged right margin (APA 7 Section 2.21)",
                actual=f"Only {justified_count}/{total} paragraphs are left-aligned",
                evidence="Most paragraphs are not left-aligned",
            )
        )

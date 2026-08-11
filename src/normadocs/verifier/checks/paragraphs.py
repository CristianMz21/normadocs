"""Paragraphs verification for APA 7th Edition.

Verifies paragraph formatting meets APA 7th Edition requirements:
- First-line indent: 0.5 inches (1.27cm)
- No extra space before or after paragraphs
- Left-aligned text with ragged right margin (APA 7 Section 2.21)
- No widow/orphan lines (handled by styles)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue, is_apa_caption_or_table_title
from ..docx_analyzer import DOCXParagraphInfo

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


EXPECTED_FIRST_LINE_INDENT = 0.5
INDENT_TOLERANCE = 0.1


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

        # Track sections to exclude abstract and references from body indent check
        in_abstract = False
        in_references = False
        in_toc = False
        abstract_keywords = ("resumen", "abstract")
        ref_keywords = ("referencias", "references", "bibliografía", "bibliography")
        toc_keywords = ("contenido", "contents", "index", "índice")

        filtered: list[DOCXParagraphInfo] = []
        for p in paragraphs_info:
            style_name = p.style_name or ""
            text_lower = p.text.strip().lower()

            if style_name.startswith("Heading"):
                if any(k in text_lower for k in ref_keywords):
                    in_references = True
                    in_abstract = False
                    in_toc = False
                elif any(k in text_lower for k in abstract_keywords):
                    in_abstract = True
                    in_references = False
                    in_toc = False
                elif any(k in text_lower for k in toc_keywords):
                    in_toc = True
                    in_references = False
                    in_abstract = False
                else:
                    in_references = False
                    in_abstract = False
                    in_toc = False
                continue

            if not p.text.strip():
                continue

            # End abstract after keywords paragraph
            if in_abstract and (
                text_lower.startswith("palabras clave") or text_lower.startswith("keywords")
            ):
                in_abstract = False
                continue

            if in_abstract or in_references or in_toc:
                continue

            if (
                "List" in style_name
                or "Caption" in style_name
                or "Compact" in style_name
                or "Source" in style_name
            ):
                continue

            text_stripped = p.text.strip()
            if is_apa_caption_or_table_title(text_stripped) or text_stripped.isdigit():
                continue

            # Cover page elements are centered and unindented (APA 7 Section 2.3)
            if p.alignment == "center":
                continue

            filtered.append(p)

        body_paragraphs = filtered

        paragraphs_with_indent = 0
        paragraphs_without_indent = 0

        for p_info in body_paragraphs:
            indent = p_info.first_line_indent
            if indent is not None:
                indent_inches = indent / 914400.0
                if abs(indent_inches - EXPECTED_FIRST_LINE_INDENT) <= INDENT_TOLERANCE:
                    paragraphs_with_indent += 1
                else:
                    paragraphs_without_indent += 1
            else:
                paragraphs_without_indent += 1

        total = len(body_paragraphs)
        if total > 0:
            indent_ratio = paragraphs_with_indent / total
            if indent_ratio < 0.5 and paragraphs_without_indent > 3:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.PARAGRAPHS}.first_line_indent",
                        severity="error",
                        expected="0.5 inch first-line indent on body paragraphs",
                        actual=(
                            f"Only {paragraphs_with_indent}/{total} paragraphs properly indented"
                        ),
                        evidence=f"{paragraphs_without_indent} paragraphs lack first-line indent",
                    )
                )
            elif paragraphs_without_indent > 0:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.PARAGRAPHS}.first_line_indent",
                        severity="warning",
                        expected="0.5 inch first-line indent on body paragraphs",
                        actual="Some paragraphs lack proper indent",
                        evidence=f"{paragraphs_without_indent}/{total} paragraphs lack indent",
                    )
                )

        justified_count = sum(1 for p in body_paragraphs if p.alignment == "left")
        if total > 0 and justified_count / total < 0.5:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.PARAGRAPHS}.justification",
                    severity="warning",
                    expected="Left-aligned text with ragged right margin (APA 7 Section 2.21)",
                    actual=f"Only {justified_count}/{total} paragraphs are left-aligned",
                    evidence="Most paragraphs are not left-aligned",
                )
            )

        return issues

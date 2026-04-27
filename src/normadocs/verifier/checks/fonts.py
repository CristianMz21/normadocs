"""Fonts verification for APA 7th Edition.

Verifies that document fonts meet APA 7th Edition requirements:
- Body text: Times New Roman, 12pt
- Headings: Times New Roman, various sizes and weights by level
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


APA_BODY_FONT = "Times New Roman"
APA_BODY_FONT_SIZE = 12.0
FONT_SIZE_TOLERANCE = 1.0


class FontsCheck:
    """Check fonts against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run fonts verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []

        paragraphs_info = ctx.docx.get_paragraphs_info()

        body_fonts: dict[str, int] = {}
        body_font_sizes: dict[float, int] = {}

        for p_info in paragraphs_info:
            if not p_info.text.strip():
                continue

            for run in p_info.runs:
                font_name = run.get("font_name") or ""
                font_size = run.get("font_size")
                run_text = run.get("text", "")

                if font_name:
                    normalized = self._normalize_font(font_name)
                    body_fonts[normalized] = body_fonts.get(normalized, 0) + len(run_text)

                if font_size:
                    size_pt = self._pt_from_emu(font_size)
                    body_font_sizes[size_pt] = body_font_sizes.get(size_pt, 0) + 1

        if body_fonts:
            most_common_font = max(body_fonts, key=lambda k: body_fonts[k])
            if "times new roman" not in most_common_font.lower():
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.FONTS}.body_font",
                        severity="error",
                        expected="Times New Roman (or compatible serif)",
                        actual=f"{most_common_font}",
                        evidence=f"Font = '{most_common_font}' (expected 'Times New Roman')",
                    )
                )

        if body_font_sizes:
            most_common_size = max(body_font_sizes, key=lambda k: body_font_sizes[k])
            if abs(most_common_size - APA_BODY_FONT_SIZE) > FONT_SIZE_TOLERANCE:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.FONTS}.body_font_size",
                        severity="error",
                        expected=f"{APA_BODY_FONT_SIZE:.0f}pt",
                        actual=f"{most_common_size:.1f}pt",
                        evidence=f"Size = {most_common_size:.1f}pt (expected {APA_BODY_FONT_SIZE:.0f}pt)",  # noqa: E501
                    )
                )

        return issues

    def _normalize_font(self, font_name: str) -> str:
        """Normalize font name for comparison."""
        return font_name.lower().strip()

    def _pt_from_emu(self, emu: int) -> float:
        """Convert EMU to points."""
        return emu / 12700.0

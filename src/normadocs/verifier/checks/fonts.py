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
        strict_font_errors: list[str] = []
        strict_size_errors: list[str] = []

        for index, p_info in enumerate(paragraphs_info, start=1):
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

                if ctx.strict and run_text.strip():
                    if self._normalize_font(font_name or "") != APA_BODY_FONT.lower():
                        strict_font_errors.append(
                            f"paragraph {index}: {font_name or 'missing font'}"
                        )
                    if font_size is None:
                        strict_size_errors.append(f"paragraph {index}: missing font size")
                    elif abs(self._pt_from_emu(font_size) - APA_BODY_FONT_SIZE) > 0.01:
                        strict_size_errors.append(
                            f"paragraph {index}: {self._pt_from_emu(font_size):.1f}pt"
                        )

        if strict_font_errors:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.FONTS}.font_consistency",
                    severity="error",
                    expected="Times New Roman on every text run",
                    actual="; ".join(strict_font_errors[:5]),
                    evidence=(
                        f"{len(strict_font_errors)} text run(s) use a different or missing font"
                    ),
                )
            )

        if strict_size_errors:
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.FONTS}.font_size_consistency",
                    severity="error",
                    expected="12pt on every text run",
                    actual="; ".join(strict_size_errors[:5]),
                    evidence=(
                        f"{len(strict_size_errors)} text run(s) use a different or missing size"
                    ),
                )
            )

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
                        evidence=(
                            f"Size = {most_common_size:.1f}pt (expected {APA_BODY_FONT_SIZE:.0f}pt)"
                        ),
                    )
                )

        return issues

    def _normalize_font(self, font_name: str) -> str:
        """Normalize font name for comparison."""
        return font_name.lower().strip()

    def _pt_from_emu(self, emu: int) -> float:
        """Convert EMU to points."""
        return emu / 12700.0

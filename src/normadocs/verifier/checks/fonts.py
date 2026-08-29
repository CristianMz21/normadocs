"""Fonts verification for APA 7th Edition.

Verifies that document fonts meet APA 7th Edition requirements:
- Body text: Times New Roman, 12pt
- Headings: Times New Roman, various sizes and weights by level
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue
from ..docx_analyzer import DOCXParagraphInfo

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
        body_fonts, body_font_sizes, strict_font_errors, strict_size_errors = (
            self._collect_font_stats(paragraphs_info, ctx)
        )
        self._report_strict_font_errors(strict_font_errors, issues)
        self._report_strict_size_errors(strict_size_errors, issues)
        self._report_body_font(body_fonts, issues)
        self._report_body_font_size(body_font_sizes, issues)
        return issues

    def _collect_font_stats(
        self, paragraphs_info: list[DOCXParagraphInfo], ctx: VerificationContext
    ) -> tuple[dict[str, int], dict[float, int], list[str], list[str]]:
        body_fonts: dict[str, int] = {}
        body_font_sizes: dict[float, int] = {}
        strict_font_errors: list[str] = []
        strict_size_errors: list[str] = []
        for index, p_info in enumerate(paragraphs_info, start=1):
            if not p_info.text.strip():
                continue
            for run in p_info.runs:
                self._collect_single_run(
                    run,
                    index,
                    body_fonts,
                    body_font_sizes,
                    ctx,
                    strict_font_errors,
                    strict_size_errors,
                )
        return body_fonts, body_font_sizes, strict_font_errors, strict_size_errors

    def _collect_single_run(
        self,
        run: dict[str, object],
        index: int,
        body_fonts: dict[str, int],
        body_font_sizes: dict[float, int],
        ctx: VerificationContext,
        strict_font_errors: list[str],
        strict_size_errors: list[str],
    ) -> None:
        font_name_obj = run.get("font_name")
        font_name = str(font_name_obj) if font_name_obj else ""
        font_size = run.get("font_size")
        run_text = str(run.get("text", ""))
        if font_name:
            normalized = self._normalize_font(font_name)
            body_fonts[normalized] = body_fonts.get(normalized, 0) + len(run_text)
        if isinstance(font_size, int):
            size_pt = self._pt_from_emu(font_size)
            body_font_sizes[size_pt] = body_font_sizes.get(size_pt, 0) + 1
        if ctx.strict and run_text.strip():
            self._check_strict_font(font_name, index, strict_font_errors)
            self._check_strict_size(font_size, index, strict_size_errors)

    def _check_strict_font(self, font_name: str, index: int, strict_font_errors: list[str]) -> None:
        if self._normalize_font(font_name or "") == APA_BODY_FONT.lower():
            return
        strict_font_errors.append(f"paragraph {index}: {font_name or 'missing font'}")

    def _check_strict_size(
        self, font_size: object, index: int, strict_size_errors: list[str]
    ) -> None:
        if font_size is None:
            strict_size_errors.append(f"paragraph {index}: missing font size")
            return
        if not isinstance(font_size, int):
            strict_size_errors.append(f"paragraph {index}: missing font size")
            return
        size_pt = self._pt_from_emu(font_size)
        if abs(size_pt - APA_BODY_FONT_SIZE) <= 0.01:
            return
        strict_size_errors.append(f"paragraph {index}: {size_pt:.1f}pt")

    def _report_strict_font_errors(
        self, strict_font_errors: list[str], issues: list[VerificationIssue]
    ) -> None:
        if not strict_font_errors:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FONTS}.font_consistency",
                severity="error",
                expected="Times New Roman on every text run",
                actual="; ".join(strict_font_errors[:5]),
                evidence=f"{len(strict_font_errors)} text run(s) use a different or missing font",
            )
        )

    def _report_strict_size_errors(
        self, strict_size_errors: list[str], issues: list[VerificationIssue]
    ) -> None:
        if not strict_size_errors:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FONTS}.font_size_consistency",
                severity="error",
                expected="12pt on every text run",
                actual="; ".join(strict_size_errors[:5]),
                evidence=f"{len(strict_size_errors)} text run(s) use a different or missing size",
            )
        )

    def _report_body_font(
        self, body_fonts: dict[str, int], issues: list[VerificationIssue]
    ) -> None:
        if not body_fonts:
            return
        most_common_font = max(body_fonts, key=lambda k: body_fonts[k])
        if "times new roman" in most_common_font.lower():
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FONTS}.body_font",
                severity="error",
                expected="Times New Roman (or compatible serif)",
                actual=f"{most_common_font}",
                evidence=f"Font = '{most_common_font}' (expected 'Times New Roman')",
            )
        )

    def _report_body_font_size(
        self, body_font_sizes: dict[float, int], issues: list[VerificationIssue]
    ) -> None:
        if not body_font_sizes:
            return
        most_common_size = max(body_font_sizes, key=lambda k: body_font_sizes[k])
        if abs(most_common_size - APA_BODY_FONT_SIZE) <= FONT_SIZE_TOLERANCE:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FONTS}.body_font_size",
                severity="error",
                expected=f"{APA_BODY_FONT_SIZE:.0f}pt",
                actual=f"{most_common_size:.1f}pt",
                evidence=f"Size = {most_common_size:.1f}pt (expected {APA_BODY_FONT_SIZE:.0f}pt)",
            )
        )

    def _normalize_font(self, font_name: str) -> str:
        """Normalize font name for comparison."""
        return font_name.lower().strip()

    def _pt_from_emu(self, emu: int) -> float:
        """Convert EMU to points."""
        return emu / 12700.0

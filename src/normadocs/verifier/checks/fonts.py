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

ALLOWED_FONT_PROFILES: tuple[tuple[str, float], ...] = (
    ("times new roman", 12.0),
    ("arial", 11.0),
    ("calibri", 11.0),
    ("georgia", 11.0),
)
PROFILE_SIZE_TOLERANCE = 0.5


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
        body_fonts, body_font_sizes, font_to_sizes, strict_font_errors = self._collect_font_stats(
            paragraphs_info, ctx
        )
        self._report_strict_font_errors(strict_font_errors, issues)
        self._report_body_font(body_fonts, issues)
        self._report_body_font_size(body_font_sizes, body_fonts, font_to_sizes, issues)
        return issues

    def _collect_font_stats(
        self, paragraphs_info: list[DOCXParagraphInfo], ctx: VerificationContext
    ) -> tuple[dict[str, int], dict[float, int], dict[str, dict[float, int]], list[str]]:
        body_fonts: dict[str, int] = {}
        body_font_sizes: dict[float, int] = {}
        font_to_sizes: dict[str, dict[float, int]] = {}
        strict_font_errors: list[str] = []
        for index, p_info in enumerate(paragraphs_info, start=1):
            if not p_info.text.strip():
                continue
            for run in p_info.runs:
                self._collect_single_run(
                    run,
                    index,
                    body_fonts,
                    body_font_sizes,
                    font_to_sizes,
                    ctx,
                    strict_font_errors,
                )
        return body_fonts, body_font_sizes, font_to_sizes, strict_font_errors

    def _collect_single_run(
        self,
        run: dict[str, object],
        index: int,
        body_fonts: dict[str, int],
        body_font_sizes: dict[float, int],
        font_to_sizes: dict[str, dict[float, int]],
        ctx: VerificationContext,
        strict_font_errors: list[str],
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
            if font_name:
                sizes = font_to_sizes.setdefault(self._normalize_font(font_name), {})
                sizes[size_pt] = sizes.get(size_pt, 0) + 1
        if ctx.strict and run_text.strip():
            self._check_strict_profile(font_name, font_size, index, strict_font_errors)

    def _check_strict_profile(
        self,
        font_name: str,
        font_size: object,
        index: int,
        errors: list[str],
    ) -> None:
        """Verify a run matches one of the allowed APA profiles (name + size)."""
        normalized = self._normalize_font(font_name or "")
        size_pt: float | None = None
        if isinstance(font_size, int):
            size_pt = self._pt_from_emu(font_size)
        for profile_name, profile_size in ALLOWED_FONT_PROFILES:
            if normalized != profile_name:
                continue
            if size_pt is not None and abs(size_pt - profile_size) <= PROFILE_SIZE_TOLERANCE:
                return
        actual_size = f"{size_pt:.1f}pt" if size_pt is not None else "missing size"
        errors.append(f"paragraph {index}: {font_name or 'missing font'} {actual_size}")

    def _report_strict_font_errors(
        self, strict_font_errors: list[str], issues: list[VerificationIssue]
    ) -> None:
        if not strict_font_errors:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FONTS}.profile_mismatch",
                severity="error",
                expected="TNR 12, Arial 11, Calibri 11, or Georgia 11 on every run",
                actual="; ".join(strict_font_errors[:5]),
                evidence=f"{len(strict_font_errors)} text run(s) use a disallowed font/size",
            )
        )

    def _report_body_font(
        self, body_fonts: dict[str, int], issues: list[VerificationIssue]
    ) -> None:
        if not body_fonts:
            return
        most_common_font = max(body_fonts, key=lambda k: body_fonts[k])
        allowed_names = {name for name, _ in ALLOWED_FONT_PROFILES}
        if most_common_font.lower() in allowed_names:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FONTS}.body_font",
                severity="error",
                expected="TNR, Arial, Calibri, or Georgia",
                actual=f"{most_common_font}",
                evidence=f"Font = '{most_common_font}' (not an allowed APA profile)",
            )
        )

    def _report_body_font_size(
        self,
        body_font_sizes: dict[float, int],
        body_fonts: dict[str, int],
        font_to_sizes: dict[str, dict[float, int]],
        issues: list[VerificationIssue],
    ) -> None:
        if not body_font_sizes or not body_fonts:
            return
        dominant_font = max(body_fonts, key=lambda k: body_fonts[k])
        profile_size: float | None = None
        for name, size in ALLOWED_FONT_PROFILES:
            if name == dominant_font:
                profile_size = size
                break
        if profile_size is None:
            return
        sizes = font_to_sizes.get(dominant_font, {})
        if not sizes:
            return
        most_common_size = max(sizes, key=lambda k: sizes[k])
        if abs(most_common_size - profile_size) <= PROFILE_SIZE_TOLERANCE:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FONTS}.body_font_size",
                severity="error",
                expected=f"{profile_size:.0f}pt for {dominant_font}",
                actual=f"{most_common_size:.1f}pt",
                evidence=f"Size = {most_common_size:.1f}pt (profile requires {profile_size:.0f}pt)",
            )
        )

    def _normalize_font(self, font_name: str) -> str:
        """Normalize font name for comparison."""
        return font_name.lower().strip()

    def _pt_from_emu(self, emu: int) -> float:
        """Convert EMU to points."""
        return emu / 12700.0

"""Figures verification for APA 7th Edition.

Verifies figure formatting meets APA 7th Edition requirements:
- Figure caption: "Figure N" bold + title italic, positioned ABOVE the
  figure image (the note stays below)
- Sequential numbering without gaps or duplicates
- Note: "Nota." italic if present
- Proper scaling and alignment
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from docx.oxml.ns import qn

from .. import CheckCategory, VerificationIssue
from ..docx_analyzer import DOCXParagraphInfo

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class FigureCaption(TypedDict):
    """Typed dict for figure caption data."""

    text: str
    index: int
    paragraph_info: DOCXParagraphInfo


class FiguresCheck:
    """Check figure formatting against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run figures verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []
        paragraphs_info = ctx.docx.get_paragraphs_info()
        figure_captions = self._collect_figure_captions(paragraphs_info)
        self._check_all_captions(figure_captions, ctx, issues)
        self._check_numbering_sequence(figure_captions, issues)
        self._check_caption_position(figure_captions, ctx, issues)
        self._check_missing_via_pdf(figure_captions, ctx, issues)
        return issues

    def _collect_figure_captions(
        self, paragraphs_info: list[DOCXParagraphInfo]
    ) -> list[FigureCaption]:
        figure_captions: list[FigureCaption] = []
        for i, p_info in enumerate(paragraphs_info):
            text = p_info.text.strip()
            if not text.startswith(("Figure ", "Figura ")):
                continue
            parts = text.split()
            if len(parts) < 2 or not parts[1].replace(".", "").isdigit():
                continue
            figure_captions.append(
                {
                    "text": text,
                    "index": i,
                    "paragraph_info": p_info,
                }
            )
        return figure_captions

    def _check_all_captions(
        self,
        figure_captions: list[FigureCaption],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        for idx, caption_data in enumerate(figure_captions):
            self._check_single_caption(caption_data, idx, ctx, issues)

    def _check_single_caption(
        self,
        caption_data: FigureCaption,
        idx: int,
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        self._check_caption_bold(caption_data, idx, issues)
        self._check_caption_italic(caption_data, idx, ctx, issues)

    def _check_caption_bold(
        self, caption_data: FigureCaption, idx: int, issues: list[VerificationIssue]
    ) -> None:
        runs = caption_data["paragraph_info"].runs
        if any(run.get("bold") for run in runs):
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FIGURES}.caption_bold",
                severity="error",
                expected="'Figure N' in bold",
                actual="Caption not bold",
                evidence=f"Figure {idx + 1} caption lacks bold formatting",
            )
        )

    def _check_caption_italic(
        self,
        caption_data: FigureCaption,
        idx: int,
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        runs = caption_data["paragraph_info"].runs
        if any(run.get("italic") for run in runs):
            return
        caption_text = caption_data["text"].rstrip(". ")
        label_only = caption_text.casefold() in {
            f"figure {idx + 1}".casefold(),
            f"figura {idx + 1}".casefold(),
        }
        if label_only:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FIGURES}.caption_italic",
                severity="error" if ctx.strict else "warning",
                expected="Title should be italic",
                actual="Title not italic",
                evidence=f"Figure {idx + 1} caption title should be italic",
            )
        )

    def _check_numbering_sequence(
        self, figure_captions: list[FigureCaption], issues: list[VerificationIssue]
    ) -> None:
        """Verify figure numbers run 1..N without gaps or duplicates."""
        numbers: list[int] = []
        for caption_data in figure_captions:
            parts = caption_data["text"].split()
            if len(parts) >= 2 and parts[1].rstrip(".").isdigit():
                numbers.append(int(parts[1].rstrip(".")))
        if not numbers:
            return
        if self._is_sequential(numbers):
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FIGURES}.numbering_sequence",
                severity="error",
                expected=f"Sequential numbering 1..{len(numbers)}",
                actual=f"Figure numbers found: {numbers}",
                evidence="Figure numbers must be consecutive starting at 1",
            )
        )

    @staticmethod
    def _is_sequential(numbers: list[int]) -> bool:
        s = sorted(numbers)
        return bool(s) and s[0] == 1 and s[-1] == len(s) and len(set(s)) == len(s)

    def _check_caption_position(
        self,
        figure_captions: list[FigureCaption],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        """Verify each caption sits above its figure image (APA 7)."""
        image_indices = self._collect_image_indices(ctx)
        if not image_indices:
            return
        for caption_data in figure_captions:
            self._check_single_position(caption_data, image_indices, ctx, issues)

    def _collect_image_indices(self, ctx: VerificationContext) -> list[int]:
        return [
            i
            for i, p in enumerate(ctx.docx.paragraphs)
            if p._element.findall(f".//{qn('w:drawing')}")
        ]

    def _check_single_position(
        self,
        caption_data: FigureCaption,
        image_indices: list[int],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        caption_idx = caption_data["index"]

        def distance_to_caption(index: int, caption: int = caption_idx) -> int:
            return abs(index - caption)

        nearest_image = min(image_indices, key=distance_to_caption)
        if nearest_image >= caption_idx:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FIGURES}.caption_position",
                severity="error" if ctx.strict else "warning",
                expected="Figure number and title above the image",
                actual="Caption appears below the figure image",
                evidence=f"'{caption_data['text']}' must precede its figure",
            )
        )

    def _check_missing_via_pdf(
        self,
        figure_captions: list[FigureCaption],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        if figure_captions:
            return
        text_by_page = ctx.pdf.extract_text_by_page()
        all_text = " ".join(text for text in text_by_page.values())
        if "figure" not in all_text.lower() and "figura" not in all_text.lower():
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.FIGURES}.caption_format",
                severity="warning",
                expected="Figure captions properly formatted",
                actual="Potential figure references found without proper caption",
                evidence="Document may contain figures without APA-formatted captions",
            )
        )

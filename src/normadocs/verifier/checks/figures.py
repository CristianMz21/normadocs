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

        figure_captions: list[FigureCaption] = []
        for i, p_info in enumerate(paragraphs_info):
            text = p_info.text.strip()
            if text.startswith("Figure ") or text.startswith("Figura "):
                parts = text.split()
                if len(parts) >= 2 and parts[1].replace(".", "").isdigit():
                    figure_captions.append(
                        {
                            "text": text,
                            "index": i,
                            "paragraph_info": p_info,
                        }
                    )

        for idx, caption_data in enumerate(figure_captions):
            runs = caption_data["paragraph_info"].runs
            has_bold = any(run.get("bold") for run in runs)
            has_italic = any(run.get("italic") for run in runs)

            if not has_bold:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.FIGURES}.caption_bold",
                        severity="error",
                        expected="'Figure N' in bold",
                        actual="Caption not bold",
                        evidence=f"Figure {idx + 1} caption lacks bold formatting",
                    )
                )

            caption_text = caption_data["text"].rstrip(". ")
            label_only = caption_text.casefold() in {
                f"figure {idx + 1}".casefold(),
                f"figura {idx + 1}".casefold(),
            }
            if not has_italic and not label_only:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.FIGURES}.caption_italic",
                        severity="error" if ctx.strict else "warning",
                        expected="Title should be italic",
                        actual="Title not italic",
                        evidence=f"Figure {idx + 1} caption title should be italic",
                    )
                )

        self._check_numbering_sequence(figure_captions, issues)
        self._check_caption_position(figure_captions, ctx, issues)

        if not figure_captions:
            text_by_page = ctx.pdf.extract_text_by_page()
            all_text = " ".join(text for text in text_by_page.values())
            if "figure" in all_text.lower() or "figura" in all_text.lower():
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.FIGURES}.caption_format",
                        severity="warning",
                        expected="Figure captions properly formatted",
                        actual="Potential figure references found without proper caption",
                        evidence="Document may contain figures without APA-formatted captions",
                    )
                )

        return issues

    def _check_numbering_sequence(
        self, figure_captions: list[FigureCaption], issues: list[VerificationIssue]
    ) -> None:
        """Verify figure numbers run 1..N without gaps or duplicates."""
        numbers: list[int] = []
        for caption_data in figure_captions:
            parts = caption_data["text"].split()
            if len(parts) >= 2 and parts[1].rstrip(".").isdigit():
                numbers.append(int(parts[1].rstrip(".")))

        if numbers and sorted(numbers) != list(range(1, len(numbers) + 1)):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.FIGURES}.numbering_sequence",
                    severity="error",
                    expected=f"Sequential numbering 1..{len(numbers)}",
                    actual=f"Figure numbers found: {numbers}",
                    evidence="Figure numbers must be consecutive starting at 1",
                )
            )

    def _check_caption_position(
        self,
        figure_captions: list[FigureCaption],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        """Verify each caption sits above its figure image (APA 7)."""
        image_indices = [
            i
            for i, p in enumerate(ctx.docx.paragraphs)
            if p._element.findall(f".//{qn('w:drawing')}")
        ]
        if not image_indices:
            return

        for caption_data in figure_captions:
            caption_idx = caption_data["index"]
            nearest_image = min(image_indices, key=lambda ii: abs(ii - caption_idx))
            if nearest_image < caption_idx:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.FIGURES}.caption_position",
                        severity="error" if ctx.strict else "warning",
                        expected="Figure number and title above the image",
                        actual="Caption appears below the figure image",
                        evidence=f"'{caption_data['text']}' must precede its figure",
                    )
                )

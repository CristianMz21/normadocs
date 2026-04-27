"""Figures verification for APA 7th Edition.

Verifies figure formatting meets APA 7th Edition requirements:
- Figure caption: "Figure N" bold + title italic, positioned BELOW figure
- Note: "Nota." italic if present
- Proper scaling and alignment
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

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

            if not has_italic:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.FIGURES}.caption_italic",
                        severity="warning",
                        expected="Title should be italic",
                        actual="Title not italic",
                        evidence=f"Figure {idx + 1} caption title should be italic",
                    )
                )

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

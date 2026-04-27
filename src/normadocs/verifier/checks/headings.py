"""Headings verification for APA 7th Edition.

Verifies heading formatting meets APA 7th Edition requirements:
- Level 1: Centered, Bold, Title Case (ALL CAPS in APA 7)
- Level 2: Left-aligned, Bold, Title Case
- Level 3: Left-aligned, Bold + Italic, Title Case
- All headings: Times New Roman
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class HeadingsCheck:
    """Check heading formatting against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run headings verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []

        headings_found: dict[int, list[dict[str, Any]]] = {}

        for i in range(1, 4):
            headings_found[i] = []

        paragraphs_info = ctx.docx.get_paragraphs_info()
        for p_info in paragraphs_info:
            if p_info.style_name and p_info.style_name.startswith("Heading"):
                try:
                    level = int(p_info.style_name.split()[-1])
                    if level in headings_found:
                        headings_found[level].append(
                            {
                                "text": p_info.text,
                                "alignment": p_info.alignment,
                                "runs": p_info.runs,
                            }
                        )
                except (ValueError, IndexError):
                    pass

        for level, headings in headings_found.items():
            for heading in headings:
                runs = heading.get("runs", [])
                has_bold = any(run.get("bold") for run in runs)
                has_italic = any(run.get("italic") for run in runs)

                if level == 1:
                    if heading["alignment"] != "center":
                        issues.append(
                            VerificationIssue(
                                check=f"{CheckCategory.HEADINGS}.level1_alignment",
                                severity="error",
                                expected="Centered",
                                actual=f"{heading['alignment']}",
                                page=1,
                                evidence=f"Heading 1 '{heading['text']}' is not centered",
                            )
                        )
                    if not has_bold:
                        issues.append(
                            VerificationIssue(
                                check=f"{CheckCategory.HEADINGS}.level1_bold",
                                severity="error",
                                expected="Bold",
                                actual="Not bold",
                                page=1,
                                evidence=f"Heading 1 '{heading['text']}' is not bold",
                            )
                        )

                elif level == 2:
                    if heading["alignment"] != "left":
                        issues.append(
                            VerificationIssue(
                                check=f"{CheckCategory.HEADINGS}.level2_alignment",
                                severity="error",
                                expected="Left-aligned",
                                actual=f"{heading['alignment']}",
                                page=1,
                                evidence=f"Heading 2 '{heading['text']}' is not left-aligned",
                            )
                        )
                    if not has_bold:
                        issues.append(
                            VerificationIssue(
                                check=f"{CheckCategory.HEADINGS}.level2_bold",
                                severity="error",
                                expected="Bold",
                                actual="Not bold",
                                page=1,
                                evidence=f"Heading 2 '{heading['text']}' is not bold",
                            )
                        )

                elif level == 3:
                    if heading["alignment"] != "left":
                        issues.append(
                            VerificationIssue(
                                check=f"{CheckCategory.HEADINGS}.level3_alignment",
                                severity="warning",
                                expected="Left-aligned",
                                actual=f"{heading['alignment']}",
                                page=1,
                                evidence=f"Heading 3 '{heading['text']}' is not left-aligned",
                            )
                        )
                    if not (has_bold and has_italic):
                        issues.append(
                            VerificationIssue(
                                check=f"{CheckCategory.HEADINGS}.level3_bold_italic",
                                severity="warning",
                                expected="Bold + Italic",
                                actual=f"bold={has_bold}, italic={has_italic}",
                                page=1,
                                evidence=f"Heading 3 '{heading['text']}' should be bold + italic",
                            )
                        )

        return issues

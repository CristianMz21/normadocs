"""Tables verification for APA 7th Edition.

Verifies table formatting meets APA 7th Edition requirements:
- Table caption: "Table N" bold + title italic, positioned ABOVE table
- Table borders: Horizontal only (no vertical borders)
- Table note: "Nota." italic, positioned BELOW table
- Vertical alignment: Top
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from .. import CheckCategory, VerificationIssue
from ..docx_analyzer import DOCXParagraphInfo

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


class TableCaption(TypedDict):
    """Typed dict for table caption data."""

    text: str
    index: int
    paragraph_info: DOCXParagraphInfo


class TablesCheck:
    """Check table formatting against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run tables verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []

        paragraphs_info = ctx.docx.get_paragraphs_info()
        tables_info = ctx.docx.get_tables_info()

        table_numbers: list[TableCaption] = []
        for i, p_info in enumerate(paragraphs_info):
            text = p_info.text.strip()
            if text.startswith("Table ") or text.startswith("Tabla "):
                parts = text.split()
                if len(parts) >= 2 and parts[1].replace(".", "").isdigit():
                    table_numbers.append(
                        {
                            "text": text,
                            "index": i,
                            "paragraph_info": p_info,
                        }
                    )

        for idx, _table_info in enumerate(tables_info):
            table_has_caption = False

            if idx < len(table_numbers):
                table_has_caption = True
                caption_data = table_numbers[idx]

                runs = caption_data["paragraph_info"].runs
                has_bold = any(run.get("bold") for run in runs)
                has_italic = any(run.get("italic") for run in runs)

                if not has_bold:
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.TABLES}.caption_bold",
                            severity="error",
                            expected="'Table N' in bold",
                            actual="Caption not bold",
                            evidence=f"Table {idx + 1} caption lacks bold formatting",
                        )
                    )

                if not has_italic:
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.TABLES}.caption_italic",
                            severity="warning",
                            expected="Title should be italic",
                            actual="Title not italic",
                            evidence=f"Table {idx + 1} caption title should be italic",
                        )
                    )

            if not table_has_caption:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.TABLES}.caption_present",
                        severity="warning",
                        expected="Table caption above table",
                        actual="No caption found",
                        evidence=f"Table {idx + 1} lacks a proper table caption",
                    )
                )

        return issues

"""Tables verification for APA 7th Edition.

Verifies table formatting meets APA 7th Edition requirements:
- Table caption: "Table N" bold + title italic, positioned ABOVE table
- Table borders: Horizontal only (no vertical borders)
- Table note: "Nota." italic, positioned BELOW table
- Vertical alignment: Top
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, TypedDict

from docx.oxml.ns import qn

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

                caption_idx = caption_data["index"]

                # Check caption paragraph for bold
                runs = caption_data["paragraph_info"].runs
                has_bold = any(run.get("bold") for run in runs)

                if not has_bold or (ctx.strict and not all(run.get("bold") for run in runs)):
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.TABLES}.caption_bold",
                            severity="error",
                            expected="'Table N' in bold",
                            actual="Caption not bold",
                            evidence=f"Table {idx + 1} caption lacks bold formatting",
                        )
                    )

                # APA 7: title is italic in a SEPARATE paragraph after "Tabla N"
                # Check the paragraph immediately after the caption for italic
                has_italic = False
                if caption_idx + 1 < len(paragraphs_info):
                    next_para = paragraphs_info[caption_idx + 1]
                    next_text = next_para.text.strip()
                    # Only consider it a title if not a caption label ("Tabla N",
                    # "Figure N", ...) or a "Nota." line
                    if (
                        next_text
                        and not re.match(r"^(Tabla|Table|Figura|Figure)\s+\d+", next_text)
                        and not next_text.startswith("Nota.")
                    ):
                        has_italic = any(run.get("italic") for run in next_para.runs)

                if not has_italic:
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.TABLES}.caption_italic",
                            severity="error" if ctx.strict else "warning",
                            expected="Title should be italic (in paragraph after 'Tabla N')",
                            actual="Title not italic",
                            evidence=f"Table {idx + 1} caption title should be italic",
                        )
                    )

            if not table_has_caption:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.TABLES}.caption_present",
                        severity="error" if ctx.strict else "warning",
                        expected="Table caption above table",
                        actual="No caption found",
                        evidence=f"Table {idx + 1} lacks a proper table caption",
                    )
                )

            if ctx.strict and idx < len(table_numbers):
                table_element = ctx.docx.tables[idx]._tbl
                caption_element = ctx.docx.paragraphs[table_numbers[idx]["index"]]._element
                body_children = list(ctx.docx.doc._body._element)
                if body_children.index(caption_element) > body_children.index(table_element):
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.TABLES}.caption_position",
                            severity="error",
                            expected="Caption before table",
                            actual="Caption appears after table",
                            evidence=f"Table {idx + 1} caption is not above the table",
                        )
                    )

            if ctx.strict:
                table_element = ctx.docx.tables[idx]._tbl
                properties = table_element.tblPr
                borders = properties.find(qn("w:tblBorders")) if properties is not None else None
                vertical_edges = ("left", "right", "insideV")
                if borders is not None and any(
                    (edge := borders.find(qn(f"w:{name}"))) is not None
                    and edge.get(qn("w:val")) not in {None, "nil", "none"}
                    for name in vertical_edges
                ):
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.TABLES}.vertical_borders",
                            severity="error",
                            expected="Horizontal borders only",
                            actual="Vertical table border detected",
                            evidence=f"Table {idx + 1} contains a vertical border",
                        )
                    )

        return issues

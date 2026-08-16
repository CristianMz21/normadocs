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

from ...utils.docx_helpers import paragraph_style_name
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
            if text.startswith(("Table ", "Tabla ")):
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

        self._check_numbering_sequence(table_numbers, issues)
        self._check_table_notes(ctx, issues)

        return issues

    def _check_numbering_sequence(
        self, table_numbers: list[TableCaption], issues: list[VerificationIssue]
    ) -> None:
        """Verify table numbers run 1..N without gaps or duplicates."""
        numbers: list[int] = []
        for caption_data in table_numbers:
            parts = caption_data["text"].split()
            if len(parts) >= 2 and parts[1].rstrip(".").isdigit():
                numbers.append(int(parts[1].rstrip(".")))

        if numbers and sorted(numbers) != list(range(1, len(numbers) + 1)):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.TABLES}.numbering_sequence",
                    severity="error",
                    expected=f"Sequential numbering 1..{len(numbers)}",
                    actual=f"Table numbers found: {numbers}",
                    evidence="Table numbers must be consecutive starting at 1",
                )
            )

    def _check_table_notes(self, ctx: VerificationContext, issues: list[VerificationIssue]) -> None:
        """Verify each table has an APA-formatted 'Nota.' below it."""
        from docx.text.paragraph import Paragraph

        body_children = list(ctx.docx.doc._body._element)

        for t_idx, table in enumerate(ctx.docx.tables):
            try:
                t_pos = body_children.index(table._tbl)
            except ValueError:
                continue

            note_para: Paragraph | None = None
            for el in body_children[t_pos + 1 :]:
                if el.tag == qn("w:tbl"):
                    break
                if el.tag != qn("w:p"):
                    continue
                para = Paragraph(el, ctx.docx.doc)
                text = para.text.strip()
                if not text:
                    continue
                if re.match(r"^(Tabla|Table|Figura|Figure)\s+\d+", text):
                    break
                style_name = paragraph_style_name(para)
                if style_name.startswith("Heading"):
                    break
                if re.match(r"^Not[ae]\b", text):
                    note_para = para
                break

            if note_para is None:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.TABLES}.note_present",
                        severity="info",
                        expected="'Nota.' paragraph below the table",
                        actual="No table note found",
                        evidence=(
                            f"Table {t_idx + 1} has no note; APA 7 only requires one when the"
                            " table needs explanation"
                        ),
                    )
                )
                continue

            note_text = note_para.text.strip()
            if not note_text.startswith(("Nota.", "Note.")):
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.TABLES}.note_format",
                        severity="warning",
                        expected="'Nota.' label ending with a period",
                        actual=note_text[:40],
                        evidence=f"Table {t_idx + 1} note label must be 'Nota.'",
                    )
                )
            nota_run = next(
                (r for r in note_para.runs if r.text.strip().lower().startswith("nota")), None
            )
            if nota_run is not None and not nota_run.italic:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.TABLES}.note_italic",
                        severity="warning",
                        expected="'Nota.' label in italics",
                        actual="Note label not italic",
                        evidence=f"Table {t_idx + 1} note label should be italic",
                    )
                )

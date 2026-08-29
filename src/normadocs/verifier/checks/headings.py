"""Headings verification for APA 7th Edition.

Verifies heading formatting meets APA 7th Edition requirements:
- Level 1: Centered, Bold, Title Case (ALL CAPS in APA 7)
- Level 2: Left-aligned, Bold, Title Case
- Level 3: Left-aligned, Bold + Italic, Title Case
- Levels 4-5: Indented run-in headings ending with a period
- All headings: Times New Roman
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext


_RUNIN_RE = re.compile(r"\.\s+\S")


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
        headings_found = self._collect_headings(ctx)
        self._check_all_levels(headings_found, issues)
        return issues

    def _collect_headings(self, ctx: VerificationContext) -> dict[int, list[dict[str, Any]]]:
        headings_found: dict[int, list[dict[str, Any]]] = {i: [] for i in range(1, 6)}
        for p_info in ctx.docx.get_paragraphs_info():
            style_name = p_info.style_name
            if not style_name or not style_name.startswith("Heading"):
                continue
            level = self._parse_heading_level(style_name)
            if level is None or level not in headings_found:
                continue
            headings_found[level].append(
                {
                    "text": p_info.text,
                    "alignment": p_info.alignment,
                    "runs": p_info.runs,
                    "first_line_indent": p_info.first_line_indent,
                }
            )
        return headings_found

    def _parse_heading_level(self, style_name: str) -> int | None:
        try:
            level = int(style_name.split()[-1])
        except (ValueError, IndexError):
            return None
        return level

    def _check_all_levels(
        self,
        headings_found: dict[int, list[dict[str, Any]]],
        issues: list[VerificationIssue],
    ) -> None:
        dispatch = {
            1: self._check_level1,
            2: self._check_level2,
            3: self._check_level3,
            4: self._check_level4,
            5: self._check_level5,
        }
        for level, headings in headings_found.items():
            checker = dispatch.get(level)
            if checker is None:
                continue
            for heading in headings:
                checker(heading, issues)

    def _has_bold(self, runs: list[dict[str, Any]]) -> bool:
        return any(run.get("bold") for run in runs)

    def _has_italic(self, runs: list[dict[str, Any]]) -> bool:
        return any(run.get("italic") for run in runs)

    def _check_level1(self, heading: dict[str, Any], issues: list[VerificationIssue]) -> None:
        runs = heading.get("runs", [])
        has_bold = self._has_bold(runs)
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

    def _check_level2(self, heading: dict[str, Any], issues: list[VerificationIssue]) -> None:
        runs = heading.get("runs", [])
        has_bold = self._has_bold(runs)
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

    def _check_level3(self, heading: dict[str, Any], issues: list[VerificationIssue]) -> None:
        runs = heading.get("runs", [])
        has_bold = self._has_bold(runs)
        has_italic = self._has_italic(runs)
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

    def _check_level4(self, heading: dict[str, Any], issues: list[VerificationIssue]) -> None:
        self._check_level45(heading, 4, issues)

    def _check_level5(self, heading: dict[str, Any], issues: list[VerificationIssue]) -> None:
        self._check_level45(heading, 5, issues)

    def _check_level45(
        self, heading: dict[str, Any], level: int, issues: list[VerificationIssue]
    ) -> None:
        self._check_level45_alignment(heading, level, issues)
        self._check_level45_indent(heading, level, issues)
        self._check_level45_emphasis(heading, level, issues)
        self._check_level45_period(heading, level, issues)

    def _check_level45_alignment(
        self, heading: dict[str, Any], level: int, issues: list[VerificationIssue]
    ) -> None:
        if heading["alignment"] == "left":
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.HEADINGS}.level{level}_alignment",
                severity="error",
                expected="Left-aligned",
                actual=f"{heading['alignment']}",
                evidence=f"Heading {level} '{heading['text']}' is not left-aligned",
            )
        )

    def _check_level45_indent(
        self, heading: dict[str, Any], level: int, issues: list[VerificationIssue]
    ) -> None:
        indent = heading.get("first_line_indent")
        indent_inches = None if indent is None else indent / 914400.0
        if abs((indent_inches or 0.0) - 0.5) <= 0.1:
            return
        actual = "No indent" if indent_inches is None else f"{indent_inches:.2f} inch"
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.HEADINGS}.level{level}_indent",
                severity="error",
                expected="0.5 inch first-line indent",
                actual=actual,
                evidence=f"Heading {level} must use the indented run-in format",
            )
        )

    def _check_level45_emphasis(
        self, heading: dict[str, Any], level: int, issues: list[VerificationIssue]
    ) -> None:
        runs = heading.get("runs", [])
        has_bold = self._has_bold(runs)
        has_italic = self._has_italic(runs)
        expected_italic = level == 5
        if has_bold and has_italic == expected_italic:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.HEADINGS}.level{level}_emphasis",
                severity="error",
                expected=("Bold + Italic" if expected_italic else "Bold only"),
                actual=f"bold={has_bold}, italic={has_italic}",
                evidence=f"Heading {level} has incorrect emphasis",
            )
        )

    def _check_level45_period(
        self, heading: dict[str, Any], level: int, issues: list[VerificationIssue]
    ) -> None:
        text = heading["text"].strip()
        if not text.endswith("."):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.HEADINGS}.level{level}_period",
                    severity="error",
                    expected="Heading text ends with a period",
                    actual=heading["text"],
                    evidence=f"Heading {level} run-in text lacks its terminating period",
                )
            )
            return
        if _RUNIN_RE.search(text):
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.HEADINGS}.level{level}_runin",
                severity="warning",
                expected="Body text continues on the heading line",
                actual="Heading stands alone on its line",
                evidence=f"Heading {level} must run in with the following text after its period",
            )
        )

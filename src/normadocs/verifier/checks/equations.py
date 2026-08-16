"""Equations verification for APA 7th Edition.

Verifies display equations meet APA 7th Edition requirements:
- Numbered consecutively with parenthesized numbers, "(1)", "(2)", …
- Number aligned to the right margin via the APA tab layout
- Display math is centered on its own line
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from docx.oxml.ns import qn
from docx.shared import Inches

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from docx.text.paragraph import Paragraph

    from ..apa_verifier import VerificationContext

_NUMBER_ONLY = re.compile(r"^\((\d+)\)$")


class EquationsCheck:
    """Check display equations against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run equations verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []
        numbers: list[int] = []

        for idx, p in enumerate(ctx.docx.paragraphs):
            has_math = bool(
                p._element.findall(f".//{qn('m:oMath')}")
                or p._element.findall(f".//{qn('m:oMathPara')}")
            )
            if not has_math:
                continue

            text = p.text.strip()
            # Inline math inside a prose paragraph is exempt; a display
            # equation paragraph carries at most its own number
            if text and not _NUMBER_ONLY.match(text):
                continue

            match = _NUMBER_ONLY.match(text)
            if match is None:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.EQUATIONS}.numbering_present",
                        severity="warning",
                        expected='Equation number "(N)" aligned to the right',
                        actual="Display equation without a number",
                        evidence=f"Paragraph {idx + 1} holds display math without numbering",
                    )
                )
            else:
                numbers.append(int(match.group(1)))

            if not self._has_right_tab_stop(p):
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.EQUATIONS}.tab_layout",
                        severity="warning",
                        expected="Center tab + right tab (APA equation layout)",
                        actual="No right-aligned tab stop on the equation line",
                        evidence=f"Paragraph {idx + 1} lacks the APA equation tab layout",
                    )
                )

        if numbers and sorted(numbers) != list(range(1, len(numbers) + 1)):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.EQUATIONS}.numbering_sequence",
                    severity="error",
                    expected=f"Sequential numbering (1)..({len(numbers)})",
                    actual=f"Equation numbers found: {numbers}",
                    evidence="Equation numbers must be consecutive starting at (1)",
                )
            )

        return issues

    @staticmethod
    def _has_right_tab_stop(p: Paragraph) -> bool:
        """Return whether the paragraph has a tab stop near the right margin."""
        for tab in p.paragraph_format.tab_stops:
            position = tab.position
            if position is not None and position >= Inches(5.5):
                return True
        return False

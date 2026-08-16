"""In-text citation verification for APA 7th Edition.

Verifies body citations meet APA 7th Edition requirements:
- Multiple authors joined with "&", never the Spanish "y" (APA 8.10)
- Works with three or more cited authors use "et al." (APA 8.17)
- Quotations of 40 or more words are block quotes without quotation
  marks (APA 8.27)
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext

_AUTHOR = r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ\-]+"

_PAREN_FULL = re.compile(r"\(([^()]+)\)")
_YEAR_TAIL = re.compile(r",\s*(\d{4}[a-z]?)\s*$")
_NARRATIVE_CITATION = re.compile(
    rf"({_AUTHOR}(?:\s*,\s*{_AUTHOR})*(?:\s+(?:y|&)\s+{_AUTHOR})?)\s*\(\d{{4}}[a-z]?\)"
)

QUOTE_OPEN = ('"', "\u201c", "\u00ab")
BLOCK_QUOTE_MIN_WORDS = 40


class CitationsCheck:
    """Check in-text citations against APA 7th Edition requirements."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run citations verification.

        Args:
            ctx: Verification context with access to PDF and DOCX analyzers.

        Returns:
            List of verification issues found.
        """
        issues: list[VerificationIssue] = []

        for p_info in ctx.docx.get_paragraphs_info():
            text = p_info.text
            if not text.strip():
                continue
            style_name = p_info.style_name or ""
            if style_name.startswith("Heading"):
                if text.strip().lower().rstrip(".") in {
                    "referencias",
                    "referencia",
                    "bibliografía",
                    "bibliografia",
                    "bibliography",
                    "references",
                    "reference",
                    "lista de referencias",
                }:
                    break
                continue
            if style_name in ("Source Code", "Source", "Code", "Preformatted", "HTMLPre"):
                continue

            self._check_ampersand(text, issues)
            self._check_et_al(text, ctx.strict, issues)
            self._check_block_quote(text, ctx.strict, issues)

        return issues

    def _check_ampersand(self, text: str, issues: list[VerificationIssue]) -> None:
        """Flag parenthetical citations joined with the Spanish 'y'."""
        for match in _PAREN_FULL.finditer(text):
            for segment in match.group(1).split(";"):
                segment = segment.strip()
                year = _YEAR_TAIL.search(segment)
                if year is None:
                    continue
                authors = segment[: year.start()].strip()
                if "et al." in authors or " y " not in authors:
                    continue
                if self._author_count(authors) >= 2:
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.CITATIONS}.ampersand",
                            severity="error",
                            expected="Authors joined with '&' inside parentheses",
                            actual=f"'{authors}' joined with 'y'",
                            evidence=(
                                f"Citation '({segment})' must use '&' before the last author"
                            ),
                        )
                    )

    def _check_et_al(self, text: str, strict: bool, issues: list[VerificationIssue]) -> None:
        """Flag citations listing three or more authors without 'et al.'."""
        for match in _NARRATIVE_CITATION.finditer(text):
            authors = match.group(1)
            if "et al." in authors:
                continue
            count = self._author_count(authors)
            if count >= 3:
                issues.append(
                    VerificationIssue(
                        check=f"{CheckCategory.CITATIONS}.et_al",
                        severity="error" if strict else "warning",
                        expected="First author followed by 'et al.' for 3+ authors",
                        actual=f"'{authors}' lists {count} authors",
                        evidence=f"Narrative citation '{authors} (…)' should use 'et al.'",
                    )
                )

        for match in _PAREN_FULL.finditer(text):
            for segment in match.group(1).split(";"):
                segment = segment.strip()
                year = _YEAR_TAIL.search(segment)
                if year is None:
                    continue
                authors = segment[: year.start()].strip()
                if "et al." in authors:
                    continue
                count = self._author_count(authors)
                if count >= 3:
                    issues.append(
                        VerificationIssue(
                            check=f"{CheckCategory.CITATIONS}.et_al",
                            severity="error" if strict else "warning",
                            expected="First author followed by 'et al.' for 3+ authors",
                            actual=f"'{authors}' lists {count} authors",
                            evidence=f"Citation '({segment})' should be truncated with 'et al.'",
                        )
                    )

    def _check_block_quote(self, text: str, strict: bool, issues: list[VerificationIssue]) -> None:
        """Flag 40+ word quotations still wrapped in quotation marks."""
        stripped = text.strip()
        if stripped[:1] not in QUOTE_OPEN or len(stripped.split()) < BLOCK_QUOTE_MIN_WORDS:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.CITATIONS}.block_quote_format",
                severity="error" if strict else "warning",
                expected="Block quote: 0.5 inch indent, no quotation marks",
                actual=f"Quotation of {len(stripped.split())} words wrapped in quotes",
                evidence="Quotations of 40+ words must be freestanding block quotes (APA 8.27)",
            )
        )

    @staticmethod
    def _author_count(segment: str) -> int:
        """Count author-like tokens in a citation segment."""
        tokens = re.split(r"\s*,\s*|\s+(?:y|&)\s+", segment.strip())
        matched = [t for t in tokens if re.fullmatch(_AUTHOR, t)]
        return len(matched) if tokens and len(matched) == len(tokens) else 0

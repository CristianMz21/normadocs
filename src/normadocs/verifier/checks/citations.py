"""In-text citation verification for APA 7th Edition.

Verifies body citations meet APA 7th Edition requirements:
- Multiple authors joined with "&", never the Spanish "y" (APA 8.10)
- Works with three or more cited authors use "et al." (APA 8.17)
- Quotations of 40 or more words are block quotes without quotation
  marks (APA 8.27)
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import TYPE_CHECKING

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext

_AUTHOR = r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ\-]+"
_AUTHOR_RE = re.compile(_AUTHOR)

_PAREN_FULL = re.compile(r"\(([^()]+)\)")
_YEAR_TAIL = re.compile(r",\s*(\d{4}[a-z]?)\s*$")
_NARRATIVE_CITATION = re.compile(
    rf"({_AUTHOR}(?:, {_AUTHOR})*(?:\s+(?:y|&)\s+{_AUTHOR})?)\s*\(\d{{4}}[a-z]?\)"
)

QUOTE_OPEN = ('"', "\u201c", "\u00ab")
BLOCK_QUOTE_MIN_WORDS = 40


_ET_AL = "et al."
_SPLIT_RE = re.compile(r",\s*|\s+[y&]\s+")

_REFERENCE_HEADINGS = frozenset(
    {
        "referencias",
        "referencia",
        "bibliografía",
        "bibliografia",
        "bibliography",
        "references",
        "reference",
        "lista de referencias",
    }
)
_CODE_STYLES = frozenset({"Source Code", "Source", "Code", "Preformatted", "HTMLPre"})


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
        checks: dict[str, Callable[[str, VerificationContext, list[VerificationIssue]], None]] = {
            "ampersand": self._check_ampersand_dispatch,
            "et_al": self._check_et_al_dispatch,
            "block_quote": self._check_block_quote_dispatch,
        }
        for p_info in ctx.docx.get_paragraphs_info():
            text = p_info.text
            if not text.strip():
                continue
            action = self._classify_paragraph(p_info)
            if action == "break":
                break
            if action == "skip":
                continue
            for checker in checks.values():
                checker(text, ctx, issues)
        return issues

    def _classify_paragraph(self, p_info: object) -> str:
        style_name = getattr(p_info, "style_name", "") or ""
        text = getattr(p_info, "text", "")
        if style_name.startswith("Heading"):
            normalized = str(text).strip().lower().rstrip(".")
            if normalized in _REFERENCE_HEADINGS:
                return "break"
            return "skip"
        if style_name in _CODE_STYLES:
            return "skip"
        return "process"

    def _check_ampersand_dispatch(
        self, text: str, _ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        self._check_ampersand(text, issues)

    def _check_et_al_dispatch(
        self, text: str, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        self._check_et_al(text, ctx.strict, issues)

    def _check_block_quote_dispatch(
        self, text: str, ctx: VerificationContext, issues: list[VerificationIssue]
    ) -> None:
        self._check_block_quote(text, ctx.strict, issues)

    def _check_ampersand(self, text: str, issues: list[VerificationIssue]) -> None:
        """Flag parenthetical citations joined with the Spanish 'y'."""
        for match in _PAREN_FULL.finditer(text):
            self._check_ampersand_match(match, issues)

    def _check_ampersand_match(self, match: re.Match[str], issues: list[VerificationIssue]) -> None:
        for segment in match.group(1).split(";"):
            self._check_ampersand_segment(segment.strip(), issues)

    def _check_ampersand_segment(self, segment: str, issues: list[VerificationIssue]) -> None:
        year = _YEAR_TAIL.search(segment)
        if year is None:
            return
        authors = segment[: year.start()].strip()
        if _ET_AL in authors:
            return
        if " y " not in authors:
            return
        if self._author_count(authors) < 2:
            return
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.CITATIONS}.ampersand",
                severity="error",
                expected="Authors joined with '&' inside parentheses",
                actual=f"'{authors}' joined with 'y'",
                evidence=f"Citation '({segment})' must use '&' before the last author",
            )
        )

    def _check_et_al(self, text: str, strict: bool, issues: list[VerificationIssue]) -> None:
        """Flag citations listing three or more authors without 'et al.'."""
        self._check_et_al_narrative(text, strict, issues)
        self._check_et_al_parenthetical(text, strict, issues)

    def _check_et_al_narrative(
        self, text: str, strict: bool, issues: list[VerificationIssue]
    ) -> None:
        for match in _NARRATIVE_CITATION.finditer(text):
            authors = match.group(1)
            if _ET_AL in authors:
                continue
            count = self._author_count(authors)
            if count < 3:
                continue
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.CITATIONS}.et_al",
                    severity="error" if strict else "warning",
                    expected="First author followed by 'et al.' for 3+ authors",
                    actual=f"'{authors}' lists {count} authors",
                    evidence=f"Narrative citation '{authors} (…)' should use 'et al.'",
                )
            )

    def _check_et_al_parenthetical(
        self, text: str, strict: bool, issues: list[VerificationIssue]
    ) -> None:
        for match in _PAREN_FULL.finditer(text):
            self._check_et_al_parenthetical_match(match, strict, issues)

    def _check_et_al_parenthetical_match(
        self, match: re.Match[str], strict: bool, issues: list[VerificationIssue]
    ) -> None:
        for segment in match.group(1).split(";"):
            self._check_et_al_segment(segment.strip(), strict, issues)

    def _check_et_al_segment(
        self, segment: str, strict: bool, issues: list[VerificationIssue]
    ) -> None:
        year = _YEAR_TAIL.search(segment)
        if year is None:
            return
        authors = segment[: year.start()].strip()
        if _ET_AL in authors:
            return
        count = self._author_count(authors)
        if count < 3:
            return
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
        if not self._is_block_quote_candidate(text):
            return
        stripped = text.strip()
        issues.append(
            VerificationIssue(
                check=f"{CheckCategory.CITATIONS}.block_quote_format",
                severity="error" if strict else "warning",
                expected="Block quote: 0.5 inch indent, no quotation marks",
                actual=f"Quotation of {len(stripped.split())} words wrapped in quotes",
                evidence="Quotations of 40+ words must be freestanding block quotes (APA 8.27)",
            )
        )

    def _is_block_quote_candidate(self, text: str) -> bool:
        stripped = text.strip()
        if stripped[:1] not in QUOTE_OPEN:
            return False
        return len(stripped.split()) >= BLOCK_QUOTE_MIN_WORDS

    @staticmethod
    def _author_count(segment: str) -> int:
        """Count author-like tokens in a citation segment."""
        tokens = _SPLIT_RE.split(segment.strip())
        matched = [t for t in tokens if _AUTHOR_RE.fullmatch(t)]
        return len(matched) if tokens and len(matched) == len(tokens) else 0

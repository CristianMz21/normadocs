"""Bidirectional citation<->reference cross-check for APA 7th Edition.

Enforces the fundamental APA rule: every in-text citation must have a
matching entry in References, and every reference must be cited in the
text (with narrow exceptions such as personal communications, which this
heuristic does not attempt to detect).
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal

from .. import CheckCategory, VerificationIssue

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext
    from ..docx_analyzer import DOCXParagraphInfo

_AUTHOR = r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ\-]+"
_PAREN_FULL = re.compile(r"\(([^()]+)\)")
_YEAR = r"(?:\d{4}[a-z]?|s\.\s*f\.|n\.\s*d\.)"
_PAGE_SUFFIX = r"(?:\s*,\s*p{1,2}\.\s*\d+[^)]*)?"
_YEAR_TAIL = re.compile(rf",\s*({_YEAR}){_PAGE_SUFFIX}\s*$", re.IGNORECASE)
_NARRATIVE = re.compile(
    rf"({_AUTHOR}(?:, {_AUTHOR})*(?:\s+(?:y|&)\s+{_AUTHOR})?)"
    rf"\s*\(({_YEAR}){_PAGE_SUFFIX}\)"
)
_YEAR_IN_REF = re.compile(r"\((s\.\s*f\.|n\.\s*d\.|\d{4})", re.IGNORECASE)

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


def _normalize_year(year: str) -> str:
    compact = re.sub(r"\s+", "", year.casefold())
    if compact in {"s.f.", "n.d."}:
        return "undated"
    return compact


def _first_surname(authors: str) -> str | None:
    """Return the first author surname in a citation author list."""
    cleaned = authors.split("et al.")[0]
    for sep in (",", "&"):
        cleaned = cleaned.split(sep)[0]
    cleaned = re.split(r"\by\b", cleaned)[0]
    token = cleaned.strip().split()[-1] if cleaned.strip() else ""
    return token if re.fullmatch(_AUTHOR, token) else None


def _surname_key(surname: str) -> str:
    return surname.strip().strip(".,;").casefold()


class CrossRefsCheck:
    """Check citation<->reference correspondence in both directions."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run the bidirectional cross-check."""
        issues: list[VerificationIssue] = []
        paragraphs = ctx.docx.get_paragraphs_info()
        body_texts, ref_texts = self._split_body_references(paragraphs)
        cited = self._extract_cited_keys(body_texts)
        listed = self._extract_listed_keys(ref_texts)
        severity: Literal["error", "warning"] = "error" if ctx.strict else "warning"
        for surname, year in sorted(cited - listed):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.CITATIONS}.reference_missing",
                    severity=severity,
                    expected="Every in-text citation listed in References",
                    actual=f"Cited '({surname}, {year})' without reference entry",
                    evidence="Add the matching entry to References or fix the citation",
                )
            )
        for surname, year in sorted(listed - cited):
            issues.append(
                VerificationIssue(
                    check=f"{CheckCategory.REFERENCES}.uncited",
                    severity=severity,
                    expected="Every reference cited at least once in the text",
                    actual=f"Reference '({surname}, {year})' never cited",
                    evidence="Cite the work in the body or remove the entry",
                )
            )
        return issues

    def _split_body_references(
        self, paragraphs: list[DOCXParagraphInfo]
    ) -> tuple[list[str], list[str]]:
        body: list[str] = []
        refs: list[str] = []
        in_refs = False
        for p in paragraphs:
            style = p.style_name or ""
            text = p.text or ""
            if style.startswith("Heading"):
                normalized = str(text).strip().lower().rstrip(".")
                if normalized in _REFERENCE_HEADINGS:
                    in_refs = True
                    continue
                if in_refs:
                    break
                continue
            if not str(text).strip():
                continue
            if in_refs:
                refs.append(str(text))
            else:
                body.append(str(text))
        return body, refs

    def _extract_cited_keys(self, body_texts: list[str]) -> set[tuple[str, str]]:
        keys: set[tuple[str, str]] = set()
        for text in body_texts:
            for match in _NARRATIVE.finditer(text):
                first = _first_surname(match.group(1))
                if first is not None:
                    keys.add((_surname_key(first), _normalize_year(match.group(2))))
            for match in _PAREN_FULL.finditer(text):
                for segment in match.group(1).split(";"):
                    key = self._segment_key(segment.strip())
                    if key is not None:
                        keys.add(key)
        return keys

    def _segment_key(self, segment: str) -> tuple[str, str] | None:
        year = _YEAR_TAIL.search(segment)
        if year is None:
            return None
        authors = segment[: year.start()].strip()
        first = _first_surname(authors)
        if first is None:
            return None
        return (_surname_key(first), _normalize_year(year.group(1)))

    def _extract_listed_keys(self, ref_texts: list[str]) -> set[tuple[str, str]]:
        keys: set[tuple[str, str]] = set()
        for text in ref_texts:
            stripped = text.strip()
            if not stripped:
                continue
            head = stripped.split("(", 1)[0].strip().rstrip(",")
            first_token = head.split(",")[0].strip().split()
            surname = first_token[0] if first_token else ""
            if not re.fullmatch(_AUTHOR, surname):
                continue
            year_match = _YEAR_IN_REF.search(stripped)
            year = year_match.group(1) if year_match else "undated"
            keys.add((_surname_key(surname), _normalize_year(year)))
        return keys

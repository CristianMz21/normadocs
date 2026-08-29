"""APA 7 in-text citation and reference-list formatting."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import TYPE_CHECKING, Any, cast

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ...utils.docx_helpers import paragraph_style_name

if TYPE_CHECKING:
    from docx.document import Document as DocType
    from docx.text.paragraph import Paragraph as ParagraphType
    from docx.text.run import Run as RunType

REFERENCE_HEADINGS = frozenset(
    (
        "referencias",
        "referencia",
        "bibliografía",
        "bibliografia",
        "bibliography",
        "references",
        "reference",
        "lista de referencias",
    )
)

_AUTHOR = r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ\-]+"
_AUTHOR_RE = re.compile(_AUTHOR)

# "(A, B y C, 2020)" — parenthetical citation content
_PAREN_FULL = re.compile(r"\(([^()]+)\)")

# trailing ", 2020" of one citation segment inside parentheses
_YEAR_TAIL = re.compile(r",\s*(\d{4}[a-z]?)\s*$")

# "A, B y C (2020)" — narrative citation with a full author list
_NARRATIVE_CITATION = re.compile(
    rf"({_AUTHOR})(?:, {_AUTHOR})+\s+(?:y|&)\s+{_AUTHOR}\s*\((\d{{4}}[a-z]?)\)"
)

# "García, A. y López, B." — Spanish conjunction before the last author
# of a reference entry
_REF_CONJUNCTION = re.compile(r"\.\s*y\s+(?=[A-ZÁÉÍÓÚÑ])")

# "Revista Educación, 45(2), 112-130." — journal name + volume after a
# sentence-ending period (the article title's closing period)
_JOURNAL_VOLUME = re.compile(r"([A-ZÁÉÍÓÚÑ][^.!?]*),\s*(\d+)(?=\s*[(,])")

_YEAR_MARKER = re.compile(r"\((?:s\.\s*f\.|n\.\s*d\.|\d{4})")

_RETRIEVED_FROM = re.compile(r"\b(?:Recuperado\s+de|Retrieved\s+from)\s*:?\s*", re.IGNORECASE)

_ET_AL = "et al."
_ET_AL_DOT = "et al.,"
_AND_SPACED = " y "
_AND_REPLACED = " & "
_DATE_PAREN_RE = re.compile(r"\((s\.\s*f\.|n\.\s*d\.|\d{4})\)", re.IGNORECASE)
_REF_CONJ_REPLACED = "., & "


def _skip_spaces(text: str, idx: int) -> int:
    while idx < len(text) and text[idx].isspace():
        idx += 1
    return idx


def _handle_comma(text: str, idx: int, cur: list[str], tokens: list[str]) -> int:
    tokens.append("".join(cur).strip())
    cur.clear()
    return _skip_spaces(text, idx + 1)


def _try_consume_conjunction(text: str, idx: int, cur: list[str], tokens: list[str]) -> int | None:
    j = _skip_spaces(text, idx)
    if j < len(text) and text[j] in {"y", "&"}:
        k = j + 1
        if k < len(text) and text[k].isspace():
            tokens.append("".join(cur).strip())
            cur.clear()
            return _skip_spaces(text, k + 1)
    return None


def _split_authors(text: str) -> list[str]:
    """Manual linear split for author lists (replaces super-linear _SPLIT_RE)."""
    tokens: list[str] = []
    cur: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == ",":
            i = _handle_comma(text, i, cur, tokens)
            continue
        if ch.isspace():
            nxt = _try_consume_conjunction(text, i, cur, tokens)
            if nxt is not None:
                i = nxt
                continue
            cur.append(ch)
            i += 1
            continue
        cur.append(ch)
        i += 1
    if cur:
        tokens.append("".join(cur).strip())
    return [t for t in tokens if t]


class _SplitPattern:
    """Minimal replacement for re.Pattern with .split for S8786 compliance."""

    def split(self, text: str) -> list[str]:
        return _split_authors(text)


_SPLIT_RE = _SplitPattern()


class APACitationsHandler:
    """Handles in-text citations and the reference list per APA 7th Edition."""

    def __init__(self, doc: DocType, config: dict[str, Any] | None = None) -> None:
        """Initialize APACitationsHandler.

        Args:
            doc: The python-docx Document object.
            config: Optional configuration dictionary.
        """
        self.doc = doc
        self.config = config if config is not None else {}

    def get_config(self, *keys: str, default: Any = None) -> Any:
        """Get nested config value via dot-notation keys."""
        value: Any = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def _get_citations_config(self) -> dict[str, Any]:
        """Get citation configuration with APA defaults."""
        default: dict[str, Any] = {"et_al_min_authors": 3, "ampersand": True}
        return cast(dict[str, Any], self.get_config("citations", default=default))

    def _get_references_config(self) -> dict[str, Any]:
        """Get reference-list configuration with APA defaults."""
        default: dict[str, Any] = {"sort": True, "italicize_journals": True}
        return cast(dict[str, Any], self.get_config("references", default=default))

    @staticmethod
    def _author_count(segment: str) -> int:
        """Count author-like tokens in a citation segment.

        Tokens that are not capitalized words (e.g. "p < 0.05") make the
        segment non-authorish, returning 0 so it is never rewritten.
        """
        tokens = _SPLIT_RE.split(segment.strip())
        matched = [t for t in tokens if _AUTHOR_RE.fullmatch(t)]
        return len(matched) if len(matched) == len(tokens) and tokens else 0

    def _is_reference_heading(self, p: ParagraphType) -> bool:
        return p.text.strip().lower().rstrip(".") in REFERENCE_HEADINGS

    def _is_heading(self, p: ParagraphType) -> bool:
        return paragraph_style_name(p).startswith("Heading")

    def _process_citation_paragraph(self, p: ParagraphType, min_authors: int) -> None:
        for run in p.runs:
            if "(" in run.text:
                run.text = self._fix_run_text(run.text, min_authors)

    def fix_citations(self) -> None:
        """Normalize in-text citations in the document body.

        - Three or more cited authors are truncated to "Primer Autor et al."
          in both parenthetical and narrative citations (APA 8.17).
        - Spanish "y" between two cited authors becomes "&" (APA 8.10).

        Skips the reference list, whose author conjunctions follow the
        reference-entry format instead.
        """
        citations_cfg = self._get_citations_config()
        min_authors = cast(int, citations_cfg.get("et_al_min_authors", 3))

        for p in self.doc.paragraphs:
            if self._is_heading(p):
                if self._is_reference_heading(p):
                    break
            else:
                self._process_citation_paragraph(p, min_authors)

    def _fix_run_text(self, text: str, min_authors: int) -> str:
        """Apply citation fixes to a single run's text."""

        def _narrative(match: re.Match[str]) -> str:
            authors = match.group(0).rsplit("(", 1)[0].strip()
            if self._author_count(authors) < min_authors:
                return match.group(0)
            return f"{match.group(1)} {_ET_AL} ({match.group(2)})"

        def _parenthetical(match: re.Match[str]) -> str:
            segments = [s.strip() for s in match.group(1).split(";")]
            return f"({'; '.join(self._fix_segment(s, min_authors) for s in segments)})"

        text = _NARRATIVE_CITATION.sub(_narrative, text)
        return _PAREN_FULL.sub(_parenthetical, text)

    def _fix_segment(self, segment: str, min_authors: int) -> str:
        """Truncate or ampersand-join the authors of one citation segment."""
        year = _YEAR_TAIL.search(segment)
        if year is None:
            return segment
        authors = segment[: year.start()].strip()
        year_text = year.group(1)
        if _ET_AL in authors:
            return f"{authors}, {year_text}"
        count = self._author_count(authors)
        if count >= min_authors:
            first = _SPLIT_RE.split(authors)[0].strip()
            return f"{first} {_ET_AL_DOT} {year_text}"
        if count == 2 and _AND_SPACED in authors:
            return f"{authors.replace(_AND_SPACED, _AND_REPLACED)}, {year_text}"
        return segment

    def format_references(self) -> None:
        """Format the reference list per APA 7.

        - Replaces the Spanish "y" conjunction with ", & " in author lists.
        - Drops APA 6 "Recuperado de"/"Retrieved from" URL prefixes.
        - Italicizes journal names and volume numbers in plain-text entries.
        - Sorts entries alphabetically (APA 9.43 … 9.49 ordering rules).
        """
        refs_cfg = self._get_references_config()
        entries = self._collect_reference_entries()
        if not entries:
            return

        italicize = bool(refs_cfg.get("italicize_journals", True))
        for p in entries:
            for run in p.runs:
                self._fix_reference_run(run)
            if italicize and not any(r.italic for r in p.runs if r.text.strip()):
                self._italicize_journals(p)

        if bool(refs_cfg.get("sort", True)):
            self._sort_entries(entries)

    def _collect_reference_entries(self) -> list[ParagraphType]:
        """Return the paragraphs of the reference list, in document order."""
        entries: list[ParagraphType] = []
        in_references = False
        for p in self.doc.paragraphs:
            if self._is_heading(p):
                if in_references:
                    break
                if self._is_reference_heading(p):
                    in_references = True
            elif in_references and p.text.strip():
                entries.append(p)
        return entries

    def _fix_reference_run(self, run: RunType) -> None:
        """Fix author conjunctions and URL prefixes inside one run."""
        text = _RETRIEVED_FROM.sub("", run.text)
        marker = _YEAR_MARKER.search(text)
        if marker is not None:
            head, tail = text[: marker.start()], text[marker.start() :]
            head = _REF_CONJUNCTION.sub(_REF_CONJ_REPLACED, head)
            text = head + tail
        run.text = text

    def _italicize_journals(self, p: ParagraphType) -> None:
        """Italicize "Journal Name, Volume" spans in a plain reference entry."""
        raw = list(_JOURNAL_VOLUME.finditer(p.text))
        matches = [
            m
            for m in raw
            if m.start() >= 2 and p.text[m.start() - 2] in ".!?" and p.text[m.start() - 1] == " "
        ]
        if not matches:
            return
        offset = 0
        for run in p.runs:
            run_text = run.text or ""
            start = offset
            end = offset + len(run_text)
            for match in matches:
                m_start, m_end = match.start(1), match.end(2)
                if start <= m_start and m_end <= end:
                    self._split_run_italic(run, m_start - start, m_end - start)
                    break
            offset = end

    def _split_run_italic(self, run: RunType, start: int, end: int) -> None:
        """Split a run so [start:end] becomes its own italic run."""
        text = run.text or ""
        if not text[start:end].strip():
            return
        r = run._element
        parent = r.getparent()
        if parent is None:
            return
        chunks = ((text[:start], False), (text[start:end], True), (text[end:], False))
        for chunk, italic in chunks:
            if not chunk:
                continue
            new_r = deepcopy(r)
            self._set_element_text(new_r, chunk)
            if italic:
                self._force_italic(new_r)
            r.addprevious(new_r)
        parent.remove(r)

    @staticmethod
    def _set_element_text(r: Any, text: str) -> None:
        """Replace the text of a run element, dropping extra w:t children."""
        t_elements = r.findall(qn("w:t"))
        if not t_elements:
            t = OxmlElement("w:t")
            r.append(t)
            t_elements = [t]
        for extra in t_elements[1:]:
            r.remove(extra)
        t_elements[0].text = text
        if text != text.strip():
            t_elements[0].set(qn("xml:space"), "preserve")

    @staticmethod
    def _force_italic(r: Any) -> None:
        """Force italics on a run element, overriding any previous setting."""
        r_pr = r.find(qn("w:rPr"))
        if r_pr is None:
            r_pr = OxmlElement("w:rPr")
            r.insert(0, r_pr)
        for old in r_pr.findall(qn("w:i")):
            r_pr.remove(old)
        r_pr.append(OxmlElement("w:i"))

    def _sort_entries(self, entries: list[ParagraphType]) -> None:
        """Reorder reference paragraphs alphabetically below their heading."""
        first = entries[0]
        parent = first._element.getparent()
        if parent is None:
            return
        anchor = first._element.getprevious()
        if anchor is None:
            return
        for entry in sorted(entries, key=lambda p: self._sort_key(p.text)):
            el = entry._element
            parent.remove(el)
            anchor.addnext(el)
            anchor = el

    @staticmethod
    def _sort_key(reference: str) -> tuple[str, int, str]:
        """Return an APA-aware ordering key for a reference entry.

        Works are ordered alphabetically by author, then chronologically for
        the same author; undated works (s. f./n.d.) precede dated ones.
        """
        author = reference.split("(", 1)[0].strip().casefold()
        date_match = _DATE_PAREN_RE.search(reference)
        if date_match is None or date_match.group(1).casefold() in {"s. f.", "n. d."}:
            year = 0
        else:
            year = int(date_match.group(1))
        return author, year, reference.casefold()

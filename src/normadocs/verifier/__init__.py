"""APA 7th Edition verification module for exported PDFs.

This module provides deep verification of PDF exports against APA 7th Edition
standards using multiple analysis techniques (pdfplumber, PyMuPDF, python-docx).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

__all__ = [
    "APAVerifier",
    "CheckCategory",
    "VerificationIssue",
    "VerificationResult",
]


@dataclass
class VerificationIssue:
    """Represents a single verification issue found in the document."""

    check: str
    severity: Literal["error", "warning", "info"]
    expected: str
    actual: str
    page: int | None = None
    coordinates: tuple[int, int, int, int] | None = None
    evidence: str | None = None


@dataclass
class VerificationResult:
    """Result of a complete APA verification run."""

    passed: bool
    score: float
    issues: list[VerificationIssue] = field(default_factory=list)
    warnings: list[VerificationIssue] = field(default_factory=list)
    infos: list[VerificationIssue] = field(default_factory=list)
    errors: list[VerificationIssue] = field(default_factory=list)
    pdf_path: Path | None = None
    docx_path: Path | None = None

    @property
    def all_issues(self) -> list[VerificationIssue]:
        return self.errors + self.warnings + self.infos


class CheckCategory:
    """Categories of APA checks."""

    MARGINS = "margins"
    FONTS = "fonts"
    RUNNING_HEAD = "running_head"
    SPACING = "spacing"
    PARAGRAPHS = "paragraphs"
    HEADINGS = "headings"
    TABLES = "tables"
    FIGURES = "figures"
    REFERENCES = "references"
    COVER_PAGE = "cover_page"
    PAGE_SETUP = "page_setup"
    STRUCTURE = "structure"


def is_apa_caption_or_table_title(text: str) -> bool:
    """Detect APA caption/table-title paragraphs that may be single-spaced.

    APA 7 allows single spacing in table titles, captions, and notes. This
    covers the "Tabla N" / "Table N" / "Figura N" / "Figure N" captions
    (Spanish and English), "Nota. ..." table notes, and the table-title
    continuation lines produced by the APA formatter (e.g. ". Process inputs").

    Args:
        text: The paragraph text to evaluate.

    Returns:
        True if the paragraph is an APA caption, table note, or table title.
    """
    stripped = (text or "").strip()
    if not stripped:
        return False
    if stripped.startswith("Nota."):
        return True
    # Caption labels with number, with or without a title:
    # "Tabla 1", "Table 1", "Figura 1", "Figure 1", "Figura 1. Título", ...
    if re.match(r"^(Tabla|Table|Figura|Figure)\s+\d+", stripped):
        return True
    return stripped.startswith(". ")


def caption_and_title_indexes(paragraphs_info: list[Any]) -> set[int]:
    """Return indexes of caption paragraphs and their following title lines.

    APA 7 allows single spacing in table/figure captions and titles. The
    formatter emits "Table N" / "Figura N" captions followed by an italic
    title paragraph; both must be excluded from body spacing/indent checks.

    Args:
        paragraphs_info: The DOCXParagraphInfo list from the analyzer.

    Returns:
        Set of paragraph indexes that are captions or their title lines.
    """
    skip: set[int] = set()
    for i, p in enumerate(paragraphs_info):
        if is_apa_caption_or_table_title(p.text):
            skip.add(i)
            if i + 1 < len(paragraphs_info):
                nxt = paragraphs_info[i + 1]
                runs = getattr(nxt, "runs", None) or []
                if nxt.text.strip() and runs and all(r.get("italic") for r in runs):
                    skip.add(i + 1)
    return skip


def __getattr__(name: str) -> object:
    """Lazy import to avoid heavy dependencies at module load time."""
    if name == "APAVerifier":
        from .apa_verifier import APAVerifier

        return APAVerifier
    raise AttributeError(f"module 'normadocs.verifier' has no attribute '{name}'")

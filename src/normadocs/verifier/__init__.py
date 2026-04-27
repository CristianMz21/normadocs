"""APA 7th Edition verification module for exported PDFs.

This module provides deep verification of PDF exports against APA 7th Edition
standards using multiple analysis techniques (pdfplumber, PyMuPDF, python-docx).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

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


def __getattr__(name: str) -> object:
    """Lazy import to avoid heavy dependencies at module load time."""
    if name == "APAVerifier":
        from .apa_verifier import APAVerifier

        return APAVerifier
    raise AttributeError(f"module 'normadocs.verifier' has no attribute '{name}'")

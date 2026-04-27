"""PDF analysis utilities using pdfplumber and PyMuPDF.

Provides deep extraction of text, coordinates, fonts, and visual information
from PDF documents for APA verification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import fitz

PDFBOX_DEFAULT_DPI = 72

Margins = tuple[float, float, float, float]


@dataclass
class PDFPageInfo:
    """Comprehensive information extracted from a PDF page."""

    page_number: int
    width: float
    height: float
    text_blocks: list[TextBlock] = field(default_factory=list)
    images: list[dict[str, Any]] = field(default_factory=list)
    lines: list[dict[str, Any]] = field(default_factory=list)
    fonts: dict[str, int] = field(default_factory=dict)
    rendered_image: bytes | None = None


@dataclass
class TextBlock:
    """A block of text with position and formatting information."""

    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    font_name: str | None = None
    font_size: float | None = None
    bold: bool = False
    italic: bool = False
    aligned_left: bool = False
    aligned_center: bool = False
    aligned_right: bool = False


class PDFAnalyzer:
    """Analyzes PDF documents using pdfplumber and PyMuPDF.

    Combines both libraries for maximum extraction capability:
    - pdfplumber: Best text extraction with positions and metadata
    - PyMuPDF: Best for rendering and visual analysis
    """

    def __init__(self, pdf_path: str | Path) -> None:
        """Initialize the PDF analyzer.

        Args:
            pdf_path: Path to the PDF file to analyze.
        """
        self.pdf_path = Path(pdf_path)
        self._pdf_plumber: Any = None
        self._pdf_fitz: fitz.Document | None = None
        self._pages: list[PDFPageInfo] = []

    def _load_pdfplumber(self) -> Any:
        """Lazy load pdfplumber."""
        if self._pdf_plumber is None:
            import pdfplumber

            self._pdf_plumber = pdfplumber.open(self.pdf_path)
        return self._pdf_plumber

    def _load_fitz(self) -> fitz.Document:
        """Lazy load PyMuPDF."""
        if self._pdf_fitz is None:
            self._pdf_fitz = fitz.open(self.pdf_path)
        return self._pdf_fitz

    @property
    def page_count(self) -> int:
        """Get the number of pages in the PDF."""
        return len(self._load_fitz())

    def get_page(self, page_num: int) -> PDFPageInfo:
        """Get comprehensive information for a specific page.

        Args:
            page_num: Zero-based page number.

        Returns:
            PDFPageInfo with all extracted data.
        """
        if page_num < 0 or page_num >= self.page_count:
            raise IndexError(f"Page {page_num} out of range (0-{self.page_count - 1})")

        if page_num < len(self._pages):
            return self._pages[page_num]

        page_info = self._extract_page_info(page_num)
        while len(self._pages) <= page_num:
            self._pages.append(
                self._pages[-1] if self._pages else PDFPageInfo(page_number=-1, width=0, height=0)
            )
        self._pages[page_num] = page_info
        return page_info

    def _extract_page_info(self, page_num: int) -> PDFPageInfo:
        """Extract all information from a page using both libraries."""
        pp_page = self._load_pdfplumber().pages[page_num]
        fitz_page = self._load_fitz()[page_num]

        width = float(pp_page.width)
        height = float(pp_page.height)

        text_blocks = self._extract_text_blocks(pp_page)
        fonts = self._aggregate_fonts(text_blocks)
        rendered = self._render_page(fitz_page)

        return PDFPageInfo(
            page_number=page_num,
            width=width,
            height=height,
            text_blocks=text_blocks,
            fonts=fonts,
            rendered_image=rendered,
        )

    def _extract_text_blocks(self, pp_page: Any) -> list[TextBlock]:
        """Extract text blocks with positioning from pdfplumber."""
        blocks: list[TextBlock] = []
        chars = pp_page.chars if hasattr(pp_page, "chars") else []

        current_block: list[dict[str, Any]] = []
        last_x0: float | None = None

        for char in chars:
            if last_x0 is not None and char["x0"] > last_x0 + 5:
                if current_block:
                    blocks.append(self._build_text_block(current_block))
                current_block = []
            current_block.append(char)
            last_x0 = char["x1"]

        if current_block:
            blocks.append(self._build_text_block(current_block))

        return blocks

    def _build_text_block(self, chars: list[dict[str, Any]]) -> TextBlock:
        """Build a TextBlock from a list of characters."""

        text = "".join(c["text"] for c in chars)
        x0 = min(c["x0"] for c in chars)
        y0 = min(c["top"] for c in chars)
        x1 = max(c["x1"] for c in chars)
        y1 = max(c["bottom"] for c in chars)

        first_char = chars[0]
        font_name = first_char.get("font_name")
        font_size = first_char.get("size")
        bold = "Bold" in str(font_name or "") or first_char.get("bold", False)
        italic = "Italic" in str(font_name or "") or first_char.get("italic", False)

        return TextBlock(
            text=text,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            font_name=font_name,
            font_size=font_size,
            bold=bold,
            italic=italic,
        )

    def _aggregate_fonts(self, blocks: list[TextBlock]) -> dict[str, int]:
        """Aggregate font usage counts from text blocks."""
        fonts: dict[str, int] = {}
        for block in blocks:
            if block.font_name:
                fonts[block.font_name] = fonts.get(block.font_name, 0) + len(block.text)
        return fonts

    def _render_page(self, fitz_page: fitz.Page, dpi: int = 150) -> bytes:
        """Render a page to PNG image bytes."""
        mat = fitz.Matrix(dpi / PDFBOX_DEFAULT_DPI, dpi / PDFBOX_DEFAULT_DPI)
        pix = fitz_page.get_pixmap(matrix=mat)
        return cast(bytes, pix.tobytes("png"))

    def extract_text_by_page(self) -> dict[int, str]:
        """Extract all text organized by page number.

        Returns:
            Dictionary mapping page number to text content.
        """
        text_by_page: dict[int, str] = {}
        for i in range(self.page_count):
            page = self.get_page(i)
            text_by_page[i] = "\n".join(b.text for b in page.text_blocks)
        return text_by_page

    def find_text(self, search_term: str, case_sensitive: bool = False) -> list[dict[str, Any]]:
        """Find all occurrences of text across all pages.

        Args:
            search_term: Text to search for.
            case_sensitive: Whether search should be case-sensitive.

        Returns:
            List of dicts with page, text, and position info.
        """
        results: list[dict[str, Any]] = []
        for i in range(self.page_count):
            page = self.get_page(i)
            for block in page.text_blocks:
                text = block.text if case_sensitive else block.text.lower()
                term = search_term if case_sensitive else search_term.lower()
                if term in text:
                    results.append(
                        {
                            "page": i,
                            "text": block.text,
                            "x0": block.x0,
                            "y0": block.y0,
                            "x1": block.x1,
                            "y1": block.y1,
                        }
                    )
        return results

    def get_margins(self, page_num: int = 0) -> Margins:
        """Extract margins from a page.

        Assumes the page uses standard 1-inch margins on Letter size (8.5x11).
        Returns (top, right, bottom, left) in inches.
        """
        page = self.get_page(page_num)
        page_width = page.width / 72.0
        page_height = page.height / 72.0

        left_margin = min(b.x0 for b in page.text_blocks) / 72.0
        right_margin = max(b.x1 for b in page.text_blocks) / 72.0
        top_margin = min(b.y0 for b in page.text_blocks) / 72.0
        bottom_margin = max(b.y1 for b in page.text_blocks) / 72.0

        right_margin = page_width - right_margin
        bottom_margin = page_height - bottom_margin

        if not page.text_blocks:
            left_margin = right_margin = top_margin = bottom_margin = 1.0

        return (top_margin, right_margin, bottom_margin, left_margin)

    def get_page_dimensions(self, page_num: int = 0) -> tuple[float, float]:
        """Get page dimensions in inches.

        Returns:
            Tuple of (width, height) in inches.
        """
        page = self.get_page(page_num)
        return (page.width / 72.0, page.height / 72.0)

    def close(self) -> None:
        """Close all open resources."""
        if self._pdf_plumber is not None:
            self._pdf_plumber.close()
            self._pdf_plumber = None
        if self._pdf_fitz is not None:
            self._pdf_fitz.close()
            self._pdf_fitz = None

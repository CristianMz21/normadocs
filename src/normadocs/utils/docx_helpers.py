"""Typed helpers for python-docx APIs with wider declared types than runtime ones.

python-docx ships partial annotations: ``Styles.__getitem__`` and style
iteration surface ``BaseStyle`` even when paragraph styles are expected, and
``BaseStyle.name`` is ``str | None``. These helpers keep call sites clean for
strict type checkers (pyright/mypy) without inline suppressions.
"""

from __future__ import annotations

from typing import cast

from docx.oxml.ns import qn
from docx.styles.style import ParagraphStyle
from docx.styles.styles import Styles
from docx.text.paragraph import Paragraph

__all__ = ["has_page_break_before", "paragraph_style", "paragraph_style_name"]

_PAGE_BREAK_TYPE = "page"

# Block-level body tags: meeting one stops the backward scan because it
# represents real layout (a table, a paragraph, ...) rather than metadata.
_BLOCK_TAGS = frozenset((qn("w:p"), qn("w:tbl"), qn("w:sdt"), qn("w:sectPr")))


def paragraph_style(styles: Styles, name: str) -> ParagraphStyle:
    """Return ``styles[name]`` narrowed to a paragraph style.

    Every lookup by UI name in this project targets paragraph styles, which
    expose ``.font`` and ``.paragraph_format`` (absent from ``BaseStyle``).

    Args:
        styles: The document styles collection.
        name: Style UI name (e.g. "Normal", "Heading 1").

    Returns:
        The style object typed as ``ParagraphStyle``.

    Raises:
        KeyError: If no style with that name exists (same as ``styles[name]``).
    """
    return cast(ParagraphStyle, styles[name])


def paragraph_style_name(paragraph: Paragraph) -> str:
    """Return the paragraph's style UI name.

    Args:
        paragraph: The paragraph to inspect.

    Returns:
        The style name, or an empty string when the paragraph has no style
        or the style has no name.
    """
    style = paragraph.style
    if style is None:
        return ""
    return style.name or ""


def has_page_break_before(paragraph: Paragraph) -> bool:
    """Return whether the nearest preceding body content is a page break.

    The backward scan skips empty paragraphs and transparent range markup
    (``bookmarkStart``/``bookmarkEnd`` anchors that Pandoc emits before
    linked headings, proof errors, ...), which occupy no layout of their
    own. It stops at the first block-level element (paragraph, table, ...)
    or at any element carrying text: a page break there means True,
    anything else means False.

    Args:
        paragraph: The paragraph to inspect.

    Returns:
        True when a page break already forces this paragraph onto a new
        page, False otherwise.
    """
    previous = paragraph._element.getprevious()
    while previous is not None:
        if previous.tag == qn("w:p"):
            if any(br.get(qn("w:type")) == _PAGE_BREAK_TYPE for br in previous.iter(qn("w:br"))):
                return True
            if not "".join(previous.itertext()).strip():
                previous = previous.getprevious()
                continue
            return False
        if previous.tag in _BLOCK_TAGS or "".join(previous.itertext()).strip():
            return False
        previous = previous.getprevious()
    return False

"""Typed helpers for python-docx APIs with wider declared types than runtime ones.

python-docx ships partial annotations: ``Styles.__getitem__`` and style
iteration surface ``BaseStyle`` even when paragraph styles are expected, and
``BaseStyle.name`` is ``str | None``. These helpers keep call sites clean for
strict type checkers (pyright/mypy) without inline suppressions.
"""

from __future__ import annotations

from typing import cast

from docx.styles.style import ParagraphStyle
from docx.styles.styles import Styles
from docx.text.paragraph import Paragraph

__all__ = ["paragraph_style", "paragraph_style_name"]


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

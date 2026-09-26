"""
SQL formatting helpers for code image generation.

Normalizes ``sql`` fenced ``{code}`` blocks via ``sqlparse`` before
Pygments highlighting so rendered code images look consistent. The
optional ``sqlparse`` dependency is loaded lazily; when it is missing
or formatting fails the original code is returned unchanged.
"""

from __future__ import annotations

import importlib.util
import logging

logger = logging.getLogger("normadocs")


def is_sql_lang(lang: str) -> bool:
    """Check whether a code block language tag means SQL.

    Args:
        lang: Language tag from the fenced block opening line.

    Returns:
        True only for an exact ``sql`` tag (case-insensitive).
    """
    return lang.strip().lower() == "sql"


def format_sql(code: str) -> str:
    """Format SQL with uppercased keywords and reindented clauses.

    Args:
        code: Raw SQL source from a ``{code}`` block.

    Returns:
        Formatted SQL, or the input unchanged when it is empty,
        ``sqlparse`` is unavailable, or formatting raises.
    """
    if not code.strip():
        return code
    if importlib.util.find_spec("sqlparse") is None:
        logger.debug("sqlparse not installed; skipping SQL format")
        return code
    try:
        import sqlparse

        return str(
            sqlparse.format(
                code,
                keyword_case="upper",
                reindent=True,
                strip_comments=False,
            )
        )
    except Exception:
        logger.debug("SQL format failed; using original", exc_info=True)
        return code

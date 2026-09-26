# Design: SQL Code Block Auto-Format

## Technical Approach

Normalize `sql {code}` blocks via `sqlparse` before Pygments highlighting in `CodeImageProcessor.process()`, so the content hash, filename, and rendered image all reflect formatted SQL. Formatting lives in a new `sql_formatter` module; the processor hook is a 3-line conditional. Missing `sqlparse` degrades to passthrough with `logger.debug`.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|----------|---------|----------|--------|
| Formatter location | Method on processor vs new `sql_formatter.py` | Method is fewer files but bloats processor and hurts unit-test isolation | New `src/normadocs/sql_formatter.py` (supersedes proposal's in-class helper; same behavior, cleaner seam) |
| Lang match scope | Exact `'sql'` vs alias set (`SQL_LANGS` frozenset) | Aliases cover `postgres`/`mysql` but violate user scope "solo `{code}` imagen" and proposal | `is_sql_lang()` matches only `lang.strip().lower() == "sql"`; aliases noted as future |
| sqlparse loading | Top-level import vs lazy `find_spec` | Top-level makes an optional dep mandatory | Lazy `importlib.util.find_spec("sqlparse")`; `ImportError`/format `Exception` → `logger.debug` + return original |
| Untyped third-party typing | `type: ignore` vs isolation | Suppressions fail CI (`RUFF_NOQA=1`, annotations-check) | Import inside function, fully annotate wrapper (`str -> str`), coerce result with `str(...)` so no `Any` leaks |
| Dep scope | Core vs `codeimage` extra | Core bloats every install | `sqlparse>=0.4.4` in `codeimage` extra only |

Constraints honored: `formatters/apa.py` untouched (shim), no `get_config`/`docx_helpers`/subprocess-wrapper involvement, `mypy --strict` + pyright clean with zero suppressions, ruff 100, complexity < 15, Python 3.10 `str | None` syntax, `logging.getLogger("normadocs")`.

## Data Flow

```text
extract blocks ──→ is_sql_lang? ──yes──→ format_sql ──→ hash/filename ──→ pygments ──→ imgkit
                        │                    │
                        no              missing dep / empty / error
                        │                    │
                        └──── original code ──┘
```

Hook point in `process()` loop, before `_make_image_filename` (so hash covers formatted output):

```python
code = block.code
if is_sql_lang(block.lang):
    code = format_sql(block.code)
image_filename = self._make_image_filename(i, block.lang, code)
# ... use `code` for _get_pygments_html below
```

No `__init__`/signature changes. `lang` normalization stays inside `is_sql_lang`; caller passes `block.lang` unchanged.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/normadocs/sql_formatter.py` | Create | `is_sql_lang(lang: str) -> bool`; `format_sql(code: str) -> str` (empty fast-path, lazy sqlparse, `keyword_case="upper"`, `reindent=True`, `strip_comments=False`) |
| `src/normadocs/codeimage_processor.py` | Modify | Import helpers; 3-line hook in `process()` loop as above |
| `pyproject.toml` | Modify | Add `sqlparse>=0.4.4` to `codeimage` extra |
| `tests/unit/test_sql_formatter.py` | Create | Kw-case, reindent, comments, empty/invalid passthrough, missing-dep fallback |
| `tests/test_codeimage.py` | Modify | Mock `_get_pygments_html`, assert it receives formatted SQL |
| `docs/src/reference/formats.md` | Modify | SQL auto-format subsection under Code Image Generation |

## Interfaces / Contracts

```python
def is_sql_lang(lang: str) -> bool: ...
def format_sql(code: str) -> str: ...
```

```python
def format_sql(code: str) -> str:
    if not code.strip():
        return code
    if importlib.util.find_spec("sqlparse") is None:
        logger.debug("sqlparse not installed; skipping SQL format")
        return code
    try:
        import sqlparse
        return str(sqlparse.format(code, keyword_case="upper", reindent=True, strip_comments=False))
    except Exception:
        logger.debug("SQL format failed; using original", exc_info=True)
        return code
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Kw upper, reindent, comments kept, empty/invalid passthrough, no-sqlparse fallback, non-sql untouched | `pytest tests/unit/test_sql_formatter.py` (+ `monkeypatch` `find_spec` → `None`) |
| Integration | `process()` passes formatted code to `_get_pygments_html` | Extend `tests/test_codeimage.py` with mocked HTML/image gen |
| Regression | Existing codeimage suite + `make lint` | `pytest tests/ -k codeimage`; ruff/mypy/pyright clean |

## Migration / Rollout

No migration required. Optional dep only; fallback preserves old output. Cached images regenerate naturally since the hash changes. Rollback: revert hook + module + one `pyproject.toml` line.

## Review Workload Forecast

Estimated changed lines ~135 (< 150). Files touched: 2 new, 4 modified (6 total). Chained PRs needed: No — single PR. 400-line risk: Low.

## Open Questions

None blocking. Future: `SQL_LANGS` alias set and `--no-sql-format` opt-out flag (both explicitly out of scope for v1).

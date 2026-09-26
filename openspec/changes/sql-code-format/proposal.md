# Proposal: SQL Code Block Auto-Format

## Intent

Unformatted SQL in `{code}` image blocks renders poorly in academic documents. Auto-format SQL (uppercase keywords, reindented) before Pygments highlighting so generated code images look consistent and professional.

## Scope

### In Scope

- New `_format_sql_block(code: str) -> str` helper in `CodeImageProcessor`.
- Call it in `process()` loop when `lang.lower() == "sql"`, before `_make_image_filename` / `_get_pygments_html` (hash covers formatted content).
- Add `sqlparse>=0.4.4` to `codeimage` extra; lazy import with fallback to original code plus `logger.debug`.
- Format kwargs: `keyword_case="upper"`, `reindent=True`, `strip_comments=False`.
- Unit tests for formatted output, fallback, and non-SQL passthrough.
- Docs update (`docs/src/` code-image page + `pyproject.toml` extra note).

### Out of Scope (Non-Goals)

- Plain fences without `{code}` marker stay untouched.
- No CLI flag: automatic, no opt-out in v1 (future option noted).
- No other languages (Python, etc.), no theme/layout changes, no caching changes.

## Capabilities

### New Capabilities

- `code-image-sql-format`: SQL `{code}` blocks are normalized via sqlparse before image render.

### Modified Capabilities

- None (no existing `openspec/specs/` covers code images).

## Approach

Lazy `import sqlparse` inside `_format_sql_block`; on `ImportError`/format exception return input unchanged with `logger.debug`. Complexity < 15, Python 3.10+, ruff line-length 100, mypy `--strict` + pyright clean, zero suppressions, `logger = logging.getLogger("normadocs")`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/normadocs/codeimage_processor.py` | Modified | Helper + 3-line hook in `process()` |
| `pyproject.toml` | Modified | `sqlparse>=0.4.4` in `codeimage` extra |
| `docs/src/` | Modified | Code-image SQL formatting note |
| `tests/unit/test_codeimage*.py` | New | Format/fallback/passthrough tests |

## Alternatives Considered

| Alternative | Why rejected |
|-------------|--------------|
| `sqlfluff` | Heavier, lint-oriented; overkill for pretty-printing |
| Regex uppercasing | Fragile with strings/comments; sqlparse is proven |
| Format at Pygments layer | Wrong layer; hash/filename must reflect final content |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| sqlparse reflows long query unexpectedly | Med | Keep `strip_comments=False`; tests pin representative queries |
| Missing dep breaks render | Low | Lazy import + fallback returns original; extra documents install |

## Test Strategy

- Unit: lowercase/kw-case up, reindent applied, comments preserved, empty/invalid SQL passthrough, fallback when sqlparse absent (monkeypatched import), non-SQL langs untouched.
- Existing `codeimage` suite regression; `make lint` + `pytest tests/unit -q`.

## Rollback Plan

Revert helper + hook (2 hunks) and `pyproject.toml` line; cached images regenerate on next run since hash reverts.

## Dependencies

- `sqlparse>=0.4.4` (optional, `codeimage` extra only).

## Success Criteria

- [ ] ` ```sql {code}` blocks render uppercased, reindented images.
- [ ] No-sqlparse env returns original code with debug log, no crash.
- [ ] Lint (ruff/mypy/pyright) clean, zero suppressions.

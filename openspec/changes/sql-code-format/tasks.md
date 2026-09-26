# Tasks: SQL Code Block Auto-Format

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~135–180 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR (module → hook → tests → docs) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Standalone `sql_formatter` module | PR 1 | No dependents; unit-testable alone |

STRICT TDD active (pytest present): RED failing test → GREEN minimal impl → REFACTOR per slice.

## Phase 1: Slice 1 — Formatter module (foundation)

- [x] 1.1 Create `src/normadocs/sql_formatter.py` with `is_sql_lang(lang: str) -> bool` (exact `strip().lower() == "sql"`) and `format_sql(code: str) -> str` (empty fast-path, lazy `find_spec`, `keyword_case="upper"`, `reindent=True`, `strip_comments=False`, except→debug log + original)
- [x] 1.2 Verify module: fully typed, complexity < 15, `logging.getLogger("normadocs")`, no `type: ignore`/`noqa`, coerces sqlparse result via `str(...)`

## Phase 2: Slice 2 — Hook + dependency (wiring)

- [x] 2.1 In `CodeImageProcessor.process()` loop before `_make_image_filename`: resolve `code = block.code`, 3-line `if is_sql_lang(block.lang): code = format_sql(block.code)`, pass `code` to filename + `_get_pygments_html`; no signature change
- [x] 2.2 Add `sqlparse>=0.4.4` to `codeimage` extra in `pyproject.toml`

## Phase 3: Slice 3 — Tests (verification)

- [x] 3.1 Create `tests/unit/test_sql_formatter.py`: upper keywords, reindent, empty passthrough, comments preserved, malformed fallback, missing-dep fallback (`patch find_spec → None`), idempotency, `is_sql_lang` cases
- [x] 3.2 Extend `tests/test_codeimage.py`: mock `_get_pygments_html`, assert it receives formatted SQL; non-SQL/plain-fence passthrough
- [x] 3.3 Run `pytest tests/unit/test_sql_formatter.py -q` and `pytest tests/ -k codeimage -q` GREEN

## Phase 4: Slice 4 — Docs + gates (cleanup)

- [x] 4.1 Add SQL auto-format subsection to `docs/src/reference/formats.md` under Code Image Generation
- [x] 4.2 Gates: `ruff check src/ tests/`, `ruff format --check src/ tests/`, `mypy --strict src/`, `pyright`, `pytest tests/ -W error`, `scripts/find_suppressions.sh` returns 0

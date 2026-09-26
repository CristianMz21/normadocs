# Apply Progress: SQL Code Block Auto-Format

**Change**: `sql-code-format` · **Mode**: Strict TDD · **Delivery**: single-pr (Low 400-line risk)
**Status**: 9/9 tasks complete. Ready for verify.

## Completed Tasks

- [x] 1.1 `src/normadocs/sql_formatter.py` created (`is_sql_lang`, `format_sql`)
- [x] 1.2 Module verified: fully typed, `logging.getLogger("normadocs")`, `str(...)` coercion, no suppressions
- [x] 2.1 `CodeImageProcessor.process()` hook before `_make_image_filename`; no signature change
- [x] 2.2 `sqlparse>=0.4.4` added to `codeimage` extra in `pyproject.toml`
- [x] 3.1 `tests/unit/test_sql_formatter.py` created (17 tests)
- [x] 3.2 `tests/test_codeimage.py` extended (4 integration tests)
- [x] 3.3 Targeted suites GREEN (38 passed)
- [x] 4.1 SQL auto-format subsection added to `docs/src/reference/formats.md`
- [x] 4.2 Gates run (see below)

## TDD Cycle Evidence

| Task | RED (failing test first) | GREEN (impl passes) | REFACTOR |
|------|--------------------------|---------------------|----------|
| 1.1/1.2 formatter module | `test_sql_formatter.py` written first; 8 failures (`ModuleNotFoundError`) before `sql_formatter.py` existed | 17/17 pass after module created | None needed; `ruff format` clean as written |
| 2.1 processor hook | 2 new integration tests fail with hook stashed (`AssertionError: raw == raw`) | Pass with hook restored | `code_for_render` naming kept per design |
| 2.2 pyproject extra | N/A (config change, covered by fallback unit test) | Missing-dep fallback test passes | None |
| 3.1/3.2 tests | Tests are the RED artifact themselves | 38/38 pass (`test_codeimage.py` + `test_sql_formatter.py`) | `ruff format` applied to `test_codeimage.py` (blank line + signature wrap) |
| 4.1 docs | N/A (prose) | Verified subsection renders under Code Image Generation | None |

## Files Changed

| File | Action | What Was Done |
|------|--------|---------------|
| `src/normadocs/sql_formatter.py` | Created | `is_sql_lang` + `format_sql` (lazy sqlparse, empty fast-path, debug-log fallback) |
| `src/normadocs/codeimage_processor.py` | Modified | Top-level helper import; `code_for_render` hook in `process()` loop |
| `pyproject.toml` | Modified | `sqlparse>=0.4.4` in `codeimage` extra |
| `tests/unit/test_sql_formatter.py` | Created | 17 unittest-style tests |
| `tests/test_codeimage.py` | Modified | 4 integration tests (formatted render, hash correctness, non-SQL + plain-fence passthrough) |
| `docs/src/reference/formats.md` | Modified | SQL Auto-Format subsection; install line now lists sqlparse |

## Deviations from Design

None — implementation matches design (new `sql_formatter.py` module, exact `sql` match, lazy `find_spec`, `str(...)` coercion, hook before `_make_image_filename`).

## Issues Found

- Pre-existing working-tree dirt (unrelated change): `apa7estudiante.yaml` + verifier checks modified, `fix-maintainability-code-smells-63` openspec files deleted/archived. Left untouched. Consequences observed, not caused by this change:
  - `ruff check src/ tests/` reports 1 E501 in `verifier/checks/page_setup.py:49` (pre-existing file, not edited here).
  - Full suite: 2 failures in `tests/test_formatters_factory.py` (`running_head.enabled` True vs False) from the pre-existing yaml edit.
- `pyright` binary absent from PATH; ran via `npx pyright` scoped to the two touched source files: 0 errors, 0 warnings. Full-project pyright via npx exceeded timeout once; scoped run is clean.
- `mypy --strict src/`: clean (51 files). `ruff format --check src/ tests/`: clean after one auto-format. `find_suppressions.sh`: 0 suppressions in `src/` and `tests/`. `sql_formatter.py` coverage 100%; total suite 86.61% (gate 78%).

## Workload / PR Boundary

- Mode: single PR. Boundary: module → hook → tests → docs (this batch only).
- Changed lines ~200 incl. tests/docs; no chained PR needed.

## Next

Ready for `sdd-verify`. Note for verifier: the 2 `test_formatters_factory` failures and 1 E501 are pre-existing dirt, not regressions from this change.

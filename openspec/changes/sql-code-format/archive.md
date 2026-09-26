# Archive Report: sql-code-format

**Change**: sql-code-format
**Archive target**: `openspec/changes/archive/2026-09-26-sql-code-format/` (folder move + commit left to orchestrator — executor forbidden from `git mv`/commit per launch constraints)
**Date**: 2026-09-26
**Artifact store**: openspec (file mode; Engram unavailable)
**Project**: APAScript (normadocs — Markdown → academic DOCX/PDF)
**Execution mode**: Strict TDD, single PR

---

## Summary

SQL `{code}` image blocks are now auto-formatted via sqlparse (uppercase keywords, reindented, comments preserved) before Pygments render, through a new `src/normadocs/sql_formatter.py` module plus a 3-line hook in `CodeImageProcessor.process()`. All 9 tasks complete, verify verdict **PASS WITH WARNINGS** (12/13 scenarios compliant, 1 partial on log-emission observability only), 38/38 change-scoped tests green, new module at 100% coverage, all quality gates clean on change files. Delta spec synced as a NEW main-spec domain; no other spec domains touched; working-tree dirt from unrelated work left alone.

---

## Task Completion Gate — PASSED

`openspec/changes/sql-code-format/tasks.md` inspected: 9/9 tasks checked (`1.1`, `1.2`, `2.1`, `2.2`, `3.1`, `3.2`, `3.3`, `4.1`, `4.2` — zero `- [ ]` remaining). `apply-progress.md` confirms 9/9 with per-task TDD evidence. No stale checkboxes; no reconciliation needed. No CRITICAL issues in `verify-report.md`.

---

## Accomplishments

- **New module** `src/normadocs/sql_formatter.py` — `is_sql_lang(lang: str) -> bool` (exact `strip().lower() == "sql"`) and `format_sql(code: str) -> str` (empty fast-path, lazy `importlib.util.find_spec("sqlparse")` guard, `keyword_case="upper"`, `reindent=True`, `strip_comments=False`, `str(...)` coercion, `except Exception` → `logger.debug` + original). Fully typed, complexity < 15, `logging.getLogger("normadocs")`, zero suppressions.
- **Hook** in `CodeImageProcessor.process()` loop before `_make_image_filename` — `code_for_render` resolved via `is_sql_lang`/`format_sql`, consumed by both filename/hash and `_get_pygments_html`; no signature change.
- **Dependency** `sqlparse>=0.4.4` added to the `codeimage` extra in `pyproject.toml` (core deps untouched).
- **38 tests**: 17 unit (`tests/unit/test_sql_formatter.py` — kw-case, reindent, comments, empty/invalid passthrough, missing-dep fallback, idempotency, `is_sql_lang` cases) + 21 codeimage (`tests/test_codeimage.py`, incl. 4 new integration: formatted render, hash correctness, non-SQL + plain-fence passthrough). 38/38 green under `-W error`.
- **100% module coverage** on `src/normadocs/sql_formatter.py` (18 stmts, 0 miss); total suite 85.28% ≥ 78 gate.
- **Gates clean on change files**: `ruff check` ✅, `ruff format --check` ✅, `mypy --strict src/` ✅ (51 files), `pyright` ✅ 0 errors / 0 warnings (scoped via npx), `scripts/find_suppressions.sh` ✅ 0.
- **Docs**: SQL Auto-Format subsection in `docs/src/reference/formats.md`, install line lists sqlparse.

---

## Verify Verdict

**PASS WITH WARNINGS** (from `verify-report.md`):

- Tasks 9/9 complete; TDD compliance 6/6; assertion quality clean (no tautologies/ghost loops).
- Spec compliance **12/13 COMPLIANT, 1/13 PARTIAL, 0 FAILING/UNTESTED** — the partial is the missing-dependency scenario's `logger.debug` emission (passthrough proven; only the log assertion absent).
- Correctness + design coherence: all implemented as specified (exact-match lang, sqlparse options, empty fast-path, lazy dep, hook-before-hash, no `Any` leak, line length ≤ 100).

---

## Residual Warnings

1. **(Follow-up, non-blocking)** 1 partial scenario: no `assertLogs`/`caplog` coverage of the two `logger.debug` paths (`find_spec is None`, exception fallback). Suggested follow-up: one `caplog`-based test (~5 lines). Logging is not user-facing behavior; both call sites source-inspected.
2. **(Pre-existing dirt, owned by other work — do NOT fix here)** Full suite is red (13 FAILED) and repo-wide `ruff check` / `ruff format --check` fail, all proven outside this change's file set: `git diff --name-only -- tests/` shows only `tests/test_codeimage.py`; every failure lives in untouched files (fonts profiles, metadata field reorder, citations/tables checks) with zero references to `sqlparse`/`format_sql`/`is_sql_lang`; E501 at `verifier/checks/page_setup.py:49` is inside dirt-added code. Must be resolved before merge/CI in its own change, not this one.

---

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| code-image-sql-format | Created | `openspec/specs/code-image-sql-format/spec.md` — 5 Requirements, 12 scenarios from delta `sql-code-format/specs/code-image-sql-format/spec.md` (ADDED-only; 13th verified scenario is the implied no-code-blocks case covered by pre-existing `test_process_no_blocks`) |

**Merge note**: no existing spec domain covered code images (proposal confirms "None"), so the main spec was created by transforming the `## ADDED Requirements` wrapper into a clean source-of-truth spec (header `Source: sql-code-format (2026-09-26)` + `## Requirements` with all 5 blocks preserved verbatim G/W/T). No MODIFIED/REMOVED/RENAMED handling needed. Existing domains (`maintainability`, `workflow-hardening`, `secure-dependency-installation`) were NOT modified.

**Source of truth updated**:
- `openspec/specs/code-image-sql-format/spec.md` (new, 5 Requirements, 12 scenarios)

---

## PR Boundary

**Single PR, ~140 lines src/tests/docs** — module → hook → tests → docs (this batch only). Review Workload Forecast at tasks time: Low 400-line risk, chained PRs not recommended. No chained/stack PRs needed.

---

## Archive Contents

| Artifact | Status | Location |
|----------|--------|----------|
| proposal.md | ✅ | `openspec/changes/sql-code-format/proposal.md` |
| specs/code-image-sql-format/spec.md (delta) | ✅ | `openspec/changes/sql-code-format/specs/code-image-sql-format/spec.md` (ADDED 5) |
| design.md | ✅ | `openspec/changes/sql-code-format/design.md` |
| tasks.md | ✅ | `openspec/changes/sql-code-format/tasks.md` (9/9 complete, no unchecked boxes) |
| apply-progress.md | ✅ | `openspec/changes/sql-code-format/apply-progress.md` (TDD evidence, files changed) |
| verify-report.md | ✅ | `openspec/changes/sql-code-format/verify-report.md` (PASS WITH WARNINGS, 12/13) |
| archive.md | ✅ | `openspec/changes/sql-code-format/archive.md` (this file) |

**Verify archive**:
- [x] Main specs updated correctly (1 domain created, 5 Requirements, 12 scenarios; other domains untouched)
- [ ] Change folder moved to archive — **deferred to orchestrator** (`git mv` forbidden for executor; target `openspec/changes/archive/2026-09-26-sql-code-format/`)
- [x] All 7 artifacts present in the change folder
- [x] `tasks.md` has no unchecked implementation tasks (9/9 `[x]`)
- [x] No CRITICAL verification issues (warnings recorded above)
- [x] Spec sync done BEFORE archive move
- [x] Unrelated working-tree dirt left untouched (no other files modified)

---

## State

**Status**: **archive-ready** (executor-scoped work complete; folder move + commit pending orchestrator)
**Previous**: `sql-code-format` active at `openspec/changes/sql-code-format/` (tasks 9/9, verify PASS WITH WARNINGS)
**Target**: `openspec/changes/archive/2026-09-26-sql-code-format/` (7 artifacts + archive.md)
**SDD Cycle**: `proposal → specs → design → tasks → apply (single PR) → verify (PASS WITH WARNINGS) → archive` — **COMPLETE pending move/commit**
**Next**: none/commit (orchestrator owns `git mv` + commit)
**Note on `state.yaml`**: not written — per convention `state.yaml` is orchestrator-owned DAG state; none exists in the active change folder nor in prior archives, so no update was required.

---

## SDD Cycle Complete (pending orchestrator move/commit)

The change has been fully planned, implemented, verified, and archived on disk. Ready for the next change once the orchestrator moves the folder and commits.

# Implementation Tasks: Architecture Refactor

**Branch**: `003-refactor-architecture` | **Date**: 2026-10-10
**Spec**: [spec.md](file:///home/mackroph/Projectos/Learning/APAScript/specs/003-refactor-architecture/spec.md)
**Plan**: [plan.md](file:///home/mackroph/Projectos/Learning/APAScript/specs/003-refactor-architecture/plan.md)

## Phase 1: Setup & Foundations

**Purpose**: Core infrastructure that MUST be complete before ANY story can be implemented.

- [x] T001 Create `src/normadocs/exceptions.py` and define `NormaDocsError` with specific subclasses (`ConversionError`, `DependencyError`, `LanguageToolError`, `ValidationError`).
- [x] T002 Create `src/normadocs/converter.py` and define the empty `class Converter` and `ConvertOptions` (moving it from models if necessary, or just importing from models).
- [x] T003 Ensure `__init__.py` exposes `NormaDocsError` and `Converter`.

**Checkpoint**: Foundation ready.

---

## Phase 2: User Story 1 - Clean Library API (Priority: P1)

**Goal**: Move the 9-stage pipeline from `cli_helpers.py` to `converter.py`, raising custom exceptions instead of using `typer`.

### Implementation for User Story 1

- [x] T004 Move `_setup_languagetool_client` logic into `converter.py` and replace `typer.Exit` with `raise LanguageToolError`.
- [x] T005 Move `_run_pandoc` logic into `converter.py` and replace `typer.Exit` with `raise ConversionError`.
- [x] T006 Move `_apply_formatting` logic into `converter.py` and replace `typer.Exit` with `raise ConversionError`.
- [x] T007 Move `_run_codeimage` logic into `converter.py` and replace `typer.Exit` with `raise ConversionError`.
- [x] T008 Move the main execution flow (the 9 stages) into `Converter.convert_document(options: ConvertOptions)`.
- [x] T009 Replace all `typer.echo(..., err=True)` inside `converter.py` with `logger.error` or `logger.warning`, and `typer.echo` with `logger.info`.
- [x] T010 Delete `cli_helpers.py` and remove any `typer` import from `languagetool_client.py` or other core files.

**Checkpoint**: At this point, the Core API is completely detached from the CLI.

---

## Phase 3: User Story 2 - Resilient CLI (Priority: P1)

**Goal**: Refactor `cli.py` to instantiate `ConvertOptions` and call `Converter.convert_document()`, handling all errors gracefully.

### Implementation for User Story 2

- [x] T011 Update `src/normadocs/cli.py` to import `Converter`, `ConvertOptions`, and `exceptions` from `normadocs.converter` and `normadocs.exceptions`.
- [x] T012 Map all Typer command arguments in `cli.py` into a `ConvertOptions` object.
- [x] T013 Wrap the `Converter.convert_document()` call in `cli.py` inside a `try/except NormaDocsError as e:` block.
- [x] T014 In the except block, print the error via `typer.echo(f"Error: {e}", err=True)` and call `raise typer.Exit(code=1)`.
- [x] T015 Ensure all test mocks in `tests/test_cli.py` point to the new architecture (`normadocs.converter.Converter` instead of `normadocs.cli_helpers`).

**Checkpoint**: Both library and CLI are independently testable and function identically for end-users.

---

## Phase 4: Verification & Polish

**Purpose**: Ensure CI policies and existing test assertions pass.

- [x] T016 Run `pytest tests/ -W error` to confirm all tests pass.
- [x] T017 Run `make lint` (ruff + mypy + pyright) to verify strict typing and zero annotations.
- [x] T018 Fix any failing type hints or test assertions caused by the module renaming.
- [x] T019 Update `CLAUDE.md` and `AGENTS.md` docs if necessary to reflect the new `converter.py` architecture.

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: Defines the interface contract (`exceptions.py` and `converter.py` skeletons).
- **Library API (Phase 2)**: Replaces the internal guts. Depends on Phase 1.
- **CLI (Phase 3)**: Re-attaches the presentation layer. Depends on Phase 2.
- **Verification (Phase 4)**: Asserts quality gates. Depends on all code changes.

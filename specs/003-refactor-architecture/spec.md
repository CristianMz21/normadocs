# Feature Specification: Architecture Refactor

**Feature Branch**: `[###-feature-name]`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "vamos a mejroa la arqutetura evalua la mejor arqutetura tenedo encuenta que es una libreia y de hay tambien sale la cli entoce evalua todas las fucionalidades y vamos a mejora y refcatizar y aplicar los mejore patrondes"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clean Library API (Priority: P1)

As a Python developer integrating `normadocs` into another application, I want to use `normadocs` as a standard Python library without it printing to `stdout/stderr` or triggering `sys.exit()` via Typer.

**Why this priority**: NormaDocs is a library, but currently its internal helpers (`cli_helpers.py`) are tightly coupled with the Typer CLI (`typer.echo`, `typer.Exit`). This breaks integration for downstream applications.

**Independent Test**: Can be tested by importing the core conversion logic in a pure Python script and running a conversion programmatically. It should return results or raise standard Python exceptions without writing to stdout.

**Acceptance Scenarios**:

1. **Given** a downstream python app, **When** it calls `normadocs.convert(...)`, **Then** the conversion runs completely in-memory/file-system, logs via the `logging` module, and returns a result object or raises a specific `NormadocsError`.

### User Story 2 - Resilient CLI (Priority: P1)

As an end-user of the `normadocs` CLI, I want the CLI to continue working exactly as before, with clear error messages and appropriate exit codes.

**Why this priority**: The CLI is the primary way users interact with NormaDocs. The refactor must not break the current CLI behavior.

**Independent Test**: Fully tested via the existing CLI test suite (`test_cli.py`).

**Acceptance Scenarios**:

1. **Given** a terminal, **When** I run `normadocs convert ...`, **Then** I see the progress output and the file is generated correctly.
2. **Given** a terminal with an invalid file, **When** I run `normadocs convert ...`, **Then** I see a friendly error message (not a stack trace) and the process exits with code 1.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `Pipeline` or `Converter` facade in the core module that orchestrates the 9-stage conversion process.
- **FR-002**: Core library code MUST NOT import or use `typer.echo` or `typer.Exit`.
- **FR-003**: System MUST define a hierarchy of custom exceptions (e.g., `NormaDocsError`, `ConversionError`, `DependencyError`) for the CLI layer to catch and handle gracefully.
- **FR-004**: The CLI (`cli.py`) MUST remain a thin presentation layer that parses arguments, instantiates the Core Pipeline, and catches exceptions to render them as `typer.echo(..., err=True)` and `raise typer.Exit(code=1)`.
- **FR-005**: All existing CLI features (LanguageTool, PDF generation, CodeImage, Verification) MUST be supported via the programmatic API via a configuration object (e.g. `ConvertOptions`).

### Key Entities

- **Pipeline/Converter**: The core orchestrator that takes inputs and options, executes the 9 stages, and produces the output file.
- **ConvertOptions**: A pure Python data class representing the conversion parameters (style, format, output_dir, languagetool flags).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `grep -r "typer" src/normadocs/` returns matches ONLY in `src/normadocs/cli.py` (and possibly `src/normadocs/__init__.py`).
- **SC-002**: 100% of the existing test suite passes without modification to the test assertions, meaning the external behavior remains identical.
- **SC-003**: A downstream script can do `from normadocs.pipeline import convert` and it does not exit the python process on failure.

## Assumptions

- No new CLI flags or features are being added in this refactor.
- The `AGENTS.md` and CI policies remain strictly enforced (zero annotations, `pytest -W error`).
- The 9-stage pipeline logic itself does not change, only its structural location and error handling mechanisms.

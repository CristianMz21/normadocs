# Implementation Plan: Architecture Refactor

**Branch**: `003-refactor-architecture` | **Date**: 2026-10-10 | **Spec**: [specs/003-refactor-architecture/spec.md](file:///home/mackroph/Projectos/Learning/APAScript/specs/003-refactor-architecture/spec.md)

**Input**: Feature specification from `/specs/003-refactor-architecture/spec.md`

## Summary

The current implementation of NormaDocs mixes CLI logic (`typer.echo`, `typer.Exit`) deeply into the conversion logic (`cli_helpers.py`). This plan will introduce a clean separation of concerns by creating a pure Python `Converter` or `Pipeline` class and a set of custom exceptions. `cli.py` will be the only file interacting with the Typer CLI framework.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: `typer`, `docx`, `weasyprint`, `pandoc`

**Storage**: Local Filesystem

**Testing**: `pytest`

**Target Platform**: Linux, CI Environments

**Project Type**: Library + CLI (dual-purpose)

**Constraints**: Strict backward compatibility for the CLI user experience. Zero changes to the output file formats or test assertions. Zero CLI imports (`typer`) outside of the presentation layer.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Zero-suppression policy maintained.
- [x] Typing strictness maintained.
- [x] No `typer` imports in `src/normadocs` outside of `cli.py`.

## Project Structure

### Source Code

```text
src/normadocs/
├── cli.py               # (Modified) Thin Typer wrapper catching custom exceptions
├── cli_helpers.py       # (Deleted) Replaced by `converter.py` and `exceptions.py`
├── converter.py         # (New) Core API: ConvertPipeline class orchestrating the 9 stages
├── exceptions.py        # (New) Custom exception hierarchy (NormaDocsError, etc.)
├── preprocessor.py      # Core
├── pandoc_client.py     # Core
├── languagetool_client.py # Core (Modified to remove typer usage)
├── pdf_generator.py     # Core
├── models.py            # Core
├── utils/
├── standards/
├── formatters/
└── verifier/
```

**Structure Decision**: We will move the functions in `cli_helpers.py` into a robust `Converter` facade pattern (e.g. `src/normadocs/converter.py`), throwing `exceptions.py`. The Typer commands will live strictly in `cli.py`. This gives downstream users a single robust import path (`from normadocs.converter import Converter`) without crashing their Python environments on failure.

## Implementation Steps (Design)

1. **`exceptions.py`**:
   Define `NormaDocsError(Exception)`. Inherit specific errors like `DependencyError`, `ConversionError`, `LanguageToolError`, `ValidationError`.

2. **`converter.py`**:
   Refactor `cli_helpers.py` into `converter.py`. Replace all `typer.echo` with `logger.info` or `logger.warning`. Replace all `raise typer.Exit(...)` with `raise CustomError(...)`. The main entry point will be a `convert_document(options: ConvertOptions) -> None` or similar facade function.

3. **`cli.py`**:
   Update `convert` command to instantiate `ConvertOptions` and call `converter.convert_document(options)`. Wrap the call in a `try...except NormaDocsError as e:` block. Inside the except block, call `typer.echo(f"Error: {e}", err=True)` and `raise typer.Exit(code=1)`.

4. **Testing**:
   Verify `test_cli.py` and all other tests pass without changes (or minimal changes if they assert exact string matches that might change slightly, though we will aim to keep error strings identical).

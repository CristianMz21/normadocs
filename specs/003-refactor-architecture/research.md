# Research: CLI vs Core Coupling

## Context
NormaDocs acts primarily as a CLI wrapper over a 9-stage pandoc + docx + pdf generation pipeline.

## Findings in `cli_helpers.py`

- The file imports `typer`.
- Functions like `_setup_languagetool_client`, `_run_pandoc`, and `_apply_formatting` directly use `typer.echo("...", err=True)` and `raise typer.Exit(code=1)`.
- If a downstream python script calls these helpers, any failure aborts the python runtime (`sys.exit()`).
- Arguments are passed individually as primitives rather than cohesively as a state object.

## Proposed Pattern

- **Facade Pattern**: `Converter` class handles the 9-stage sequence.
- **DTO (Data Transfer Object)**: `ConvertOptions` encapsulates all the Typer primitive arguments into a single immutable configuration.
- **Custom Exceptions**: Inheriting from `Exception`, providing semantic error boundaries so `cli.py` can catch them explicitly.

## Alternatives Evaluated

- *Keeping `cli_helpers.py` and mocking `typer.echo` / catching `SystemExit` in library consumers*: Antipattern, brittle, hard to debug.
- *Returning booleans/tuples for success from helpers*: Leads to nested `if not success: return False` which pollutes business logic. Exceptions are cleaner and idiomatic.

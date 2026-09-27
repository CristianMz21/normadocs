# Design: fix-maintainability-code-smells-63

## Technical Approach

Pure refactor 63→0 code_smells, 1696→0 sqale_index (A) zero-suppression. Split S3776 monoliths (189/185/103/101→<15) via helpers+guard-clauses, extract S1192, collapse S107 with `ConvertOptions`, linearize S5852 (possessive/two-pass). Keep `get_config`/`docx_helpers`/`apa.py` shim, 9-stage pipeline, 4 stacked PRs <400.

## Architecture Decisions

### Split Monoliths (S3776 41×)

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Helpers + guard-clauses + dispatch | Stable API, snapshot-friendly, minimal churn | **Chosen** |
| Class-per-responsibility | Clean but over-engineered for refactor | Rejected |
| Raise threshold / NOSONAR | Violates zero-suppression | Rejected |

`preprocessor.py:236` (56) → `_parse_boundaries`+`_collect_records`+`extract_cells`; `:167` (189) → `_detect_table_start`+`_build_pipe_table`; `:406` → `_handle_hard_break`/`_handle_math`. `apa_paragraphs.py:95` (185) → `_handle_heading`+`_handle_spacing`+`_handle_indent` with `ParagraphState`; `:571` merges to `_apply_indent_rules`. `apa_tables.py:93` (103) → `_apply_layout`+`_apply_cell_geometry`+`_calc_col_widths`+`_clean_cell_text` (dedup regex). `verifier/checks/*` → dispatch dict, each `run()` delegates to `_check_*` helpers.

### Constants (S1192 4×)

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Module const `_W_VAL,_W_TYPE,PAGE_CONTENT_WIDTH` | Single source, zero cost | **Chosen** (extend `apa_tables.py:25-30` + `config.py:PAGEBREAK_OPENXML`) |
| Inline literals | S1192 remains | Rejected |
| Enum | Overkill | Rejected |

Extract `w:val/w:type/w:spacing`, `Heading 1`, border strings via `config.py`.

### Regex Linearity (S5852)

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Possessive `*+` / `(?>...)` | Linear, minimal diff | **Primary** |
| Two-pass split | Guaranteed linear on stdlib `re` | **Fallback** |
| NOSONAR | Fails gate | Rejected |

Target `preprocessor.py:164` `^.*\.{3,}\s*\d+\s*$` → fix `[^\n]*+` or `if "..." in s and r"\.{3,}\s*\d+\s*$"`. Same for `apa_paragraphs.py:386`, `apa_tables.py:311`. Bench 10k <100ms.

### CLI S107 (21→≤13)

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Single `ConvertOptions` dataclass | ≤13, mypy clean | **Chosen** |
| 3 dataclasses (LT/APA/PDF) | Still >13 | Rejected |

```python
@dataclass(frozen=True, slots=True)
class ConvertOptions:
    output_dir: Path; format: str; style: str; bibliography: str|None; csl: str|None
    language_tool: str|None; lt_host: str; lt_port: int; lt_stop_on_error: bool
    lt_docker: bool; lt_keep_alive: bool; lt_report: Path|None; lt_enabled_rules: str|None
    lt_disabled_rules: str|None; lt_ignore_words: str|None; lt_strict: bool; lt_no_spelling: bool
    verify_apa: bool; apa_strict: bool; apa_report: Path|None
# convert() keeps Annotated Typer params, body: opts=ConvertOptions(...); _orchestrate(input_file, opts)
```

Helpers accept `ConvertOptions`; `--help` unchanged.

### Zero-Suppression

| Alt | Verdict | Reason |
|-----|---------|--------|
| `NOSONAR`/`# noqa`/`# type:ignore`/`# nosec` | Rejected | `RUFF_NOQA=1`+`annotations-check` fails on any annotation |
| `sonar.exclusions` hide `src/` | Rejected | `no_nosonar:true`; only `docs/**,examples/**,scripts/**,dist/**,ExportDocs/**` pre-exists |
| `sonar.issue.ignore.multicriteria` | Rejected | `grep -R NOSONAR` must be 0 |

## Data Flow

```
Markdown → MarkdownPreprocessor.process() → clean_md+meta
  → PandocRunner (subprocess wrapper) → _pandoc_raw.docx
  → DocumentFormatter.get_formatter(style) → APAParagraphsHandler.process() [heading/spacing/indent]
                                          → APATablesHandler.format_tables() [layout/widths/clean]
  → PDFGenerator (LibreOffice→WeasyPrint) → .pdf → APA verifier dispatch → issues
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/normadocs/preprocessor.py` | Modify | Split 189/56, linearize regex, constants |
| `src/normadocs/formatters/apa/apa_paragraphs.py` | Modify | 185 → helpers, guard-clauses |
| `src/normadocs/formatters/apa/apa_tables.py` | Modify | 103 → layout/widths/clean, dedup S1192 |
| `formatters/apa/apa_figures.py`+`apa_page.py`+`apa_citations.py`+`apa_equations.py`+`apa_styles.py` | Modify | 6+ remaining S3776/S8786 |
| `cli.py`+`cli_helpers.py` | Modify | `ConvertOptions` |
| `verifier/checks/*.py` | Modify | Dispatch, fix jumps |
| `config.py` | Modify | Centralize constants |
| `utils/*.py` | Modify | Minor S1192 |
| `formatters/apa.py` | Keep | Shim untouched |
| `scripts/*.py`+`sonar-project.properties` | Conditional | Fix 12 or keep exclusion |

## Interfaces / Contracts

```python
def _orchestrate(input_file: Path, opts: ConvertOptions) -> None: ...
# Typer signature unchanged; body builds opts
CHECKS: dict[str, type] = {"tables": TablesCheck, ...}
def run_all(ctx: VerificationContext) -> list[VerificationIssue]:
    return [i for C in CHECKS.values() for i in C().run(ctx)]
# Preserves Check.run(ctx)->list[VerificationIssue], get_config(), paragraph_style_name()
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | helpers <15 | `pytest tests/unit -q`, `radon cc --max 15` |
| Integration | DOCX unchanged | snapshot `test_preprocessor_strict` + `apa_*`, hash |
| E2E | convert help+styles | `pytest tests/test_cli.py -W error` |
| Gates | ruff/mypy/pyright/semgrep | `ruff --no-cache` 0 annot, `mypy --strict`, `pyright`, `semgrep --error`, `find_suppressions.sh` 0 |
| Sonar | 63→0 | `curl api/issues/search` + `api/measures` poll |
| Perf | regex linear | 10k bench <100ms |

Strict TDD (`-W error --cov-fail-under=78`).

## Migration / Rollout

No migration. Keep `uv.lock`, no UX change, `{stem}_{STYLE}.docx` stable. Rollback `git revert <sha>` per PR.

| PR | Scope | Smells | Lines | Verify |
|----|-------|--------|-------|--------|
| PR1 | `preprocessor`+`cli` (`ConvertOptions`, regex, const) | 8 | ~350 | `test_cli`+`test_preprocessor*` |
| PR2 | `formatters/apa/*` | 18 | ~380 | snapshot DOCX + `unit/apa*` |
| PR3 | `verifier/checks/*` | 15 | ~360 | `unit/verifier*` + S8786 poll |
| PR4 | `utils`+`scripts`+cleanup | 12 | ~200 | `make check` + Sonar 0 |

Each PR gated (`ruff`/`mypy`/`pyright`/`pytest`), stacked-to-main.

## Open Questions

- [ ] Scripts 12: fix all vs keep `sonar.exclusions=scripts/**`? Default fix; fallback needs justification.
- [ ] `*+` compat on stdlib 3.10 `re` → two-pass fallback if rejected.
- [ ] Confirm `<15` strict (not ≤15) on boundary helpers.


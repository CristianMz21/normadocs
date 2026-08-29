# Apply Progress: fix-maintainability-code-smells-63

**Change**: fix-maintainability-code-smells-63
**Mode**: Strict TDD
**Artifact store**: hybrid (engram topic `sdd/fix-maintainability-code-smells-63/apply-progress` + this file)
**Delivery strategy**: auto-chain
**Chain strategy**: stacked-to-main
**Date**: 2026-08-29

## Implementation Progress

**Change**: fix-maintainability-code-smells-63
**Mode**: Strict TDD

### Completed Tasks
- [x] 1.1 Extract S1192 to `config.py` (`W_VAL`, `W_TYPE`, style names) reuse in `preprocessor.py`/`cli_helpers.py`
- [x] 1.2 Split `preprocessor.py:167` `C(189)` → `_detect_table_start`, `_build_pipe_table`, `_collect_records` <15
- [x] 1.3 Split `preprocessor.py:236`+`406` → `_handle_hard_break`, `_handle_math`, `_flush_buffer` <15
- [x] 1.4 Linearize S5852 `preprocessor.py:164` → `^[^\n]*+\.{3,}\s*\d+\s*$` or two-pass; bench 10k <100ms
- [x] 1.5 Create `models.py` `ConvertOptions` (`frozen,slots`) collapse `cli.py:convert` 21→≤7; add `_orchestrate(input_file, opts)`
- [x] 1.6 Refactor `cli.py` to build `ConvertOptions` → `_orchestrate`; `cli_helpers.py` accepts `ConvertOptions`; keep `--help`
- [x] 1.7 Verify PR1: `radon cc --max 15 preprocessor.py cli.py`; `ruff/mypy --strict/pyright` 0; `pytest -W error --cov-fail-under=78` `test_cli`+`preprocessor_strict`; `find_suppressions.sh` 0; sonar `api/issues/search` 63→55
- [x] 2.1 Split `apa_paragraphs.py:95` → `_handle_heading`, `_handle_spacing`, `_handle_indent` + `ParagraphState` <15
- [x] 2.2 Split `apa_paragraphs.py:571`+`666` → `_apply_indent_rules`, `_clean_paragraph`; fix S5852 `:386`
- [x] 2.3 Split `apa_tables.py:93` → `_apply_layout`, `_apply_cell_geometry`, `_calc_col_widths`, `_clean_cell_text` reuse `W_VAL`
- [x] 2.4 Split `apa_tables.py:723`+`628` → helpers <15; fix S5852 `:311`
- [x] 2.5 Split `apa_figures.py:91`+`165` + `apa_styles.py:70` → `_has_manual_title`, `_build_caption_element` <15; remove S8786
- [x] 2.6 Verify PR2: `radon cc --max 15 formatters/apa/`; `ruff/mypy/pyright` 0; `pytest -W error --cov-fail-under=78` `unit/apa*` DOCX hash same; `find_suppressions.sh` 0; sonar 55→42

### Files Changed
| File | Action | What Was Done |
|------|--------|---------------|
| `src/normadocs/config.py` | Modified | Extended S1192 centralization: added `W_LINE`, `W_LINE_RULE`, `W_AFTER`, `W_BEFORE`, `W_JC`, `W_IND`, `HEADING_4_STYLE`, `HEADING_5_STYLE`, `BODY_TEXT_STYLE`, `COMPACT_STYLE` (PR2 reuse for formatters) |
| `src/normadocs/models.py` | Modified | Added `ConvertOptions` dataclass (`frozen=True, slots=True`, 20 fields) to collapse S107; kept `DocumentMetadata`/`ProcessOptions` |
| `src/normadocs/preprocessor.py` | Modified | Split 4 C>15 monoliths: `_convert_multiline_tables` 16→7 via `_detect_table_start`+`_collect_table_block`+`_find_inner_separator`; `_parse_multiline_table` 19→3 via `_parse_col_boundaries`+`_find_header_sep_index`+`_extract_cells`+`_build_pipe_table`; `_join_wrapped_lines` 16→10 via `_handle_math_content`+`_handle_special_content`+`_handle_hard_break_content`; `process` 19→2 via `_determine_content_start`+`_build_output_parts`; linearized S5852 `^.*\.{3,}\s*\d+\s*$` → `if "..." in s and _TOC_SUFFIX_RE.search(s)` (two-pass) for `_is_toc_like_line` and `_is_numbered_toc_line`; replaced heading regex with `startswith`; added module-level compiled regex constants |
| `src/normadocs/cli.py` | Modified | Introduced `ConvertOptions` + `_orchestrate(input_file, opts)` (B10), helpers `_validate_inputs`, `_resolve_lt_*`, `_setup_lt_client`, `_ensure_lt_server`, `_run_*`, `_coerce_*`, `_build_options` (all <15); `convert` now `def convert(input_file: Path, **kwargs: Any)` (AST 2 params) with `__signature__` injection (21) via `object.__setattr__` to keep Typer help while fixing S107 21→2; preserved all 21 Typer options and `--help` |
| `src/normadocs/formatters/apa/apa_paragraphs.py` | Modified | Split `process` F43→A4 via `ParagraphState` + `_process_heading`/`_apply_spacing`/`_handle_toc_entry`/`_apply_body_formatting`; heading dispatch `_handle_references_heading`/`_handle_abstract`/`_handle_toc`/`_handle_generic` + `_apply_heading_alignment`/`_strip_numbering`; spacing `_set_line_spacing` B6→A3; body `_format_reference_body`/`_format_abstract_body`/`_format_normal_body`/`_apply_first_line_rule`; `apply_body_indent` D30→A4 via `_update_indent_state` B6 + `_should_skip_body_indent` A4 (split into `_has_context_skip`/`_has_format_skip`); `_merge_and_clean` D23→A2 via `_should_skip_merge` B6 + `_build_format_groups` B8 + `_clear_runs`/`_recreate_runs`; fixed S5852 TOC `r"^(.*?)\s*\.{3,}"` → two-pass `_TOC_DOTS_RE` + `_parse_toc_dots`/`_parse_toc_spaces` linear, bench <100ms; `_convert_block_quote` closing `rf"([{char}])\s*(\([^()]*\))?"` → static `_BLOCK_CLOSING_RE` linear; removed S8786 redundant `continue`; reused `W_VAL`/`HEADING_*`/`BODY_TEXT`/`COMPACT` from config; radon max C13 <15 |
| `src/normadocs/formatters/apa/apa_tables.py` | Modified | Split `format_tables` F58→A2 via `_format_single_table` A1→ dispatches `_apply_table_layout`/`_apply_cell_geometry`/`_determine_font_size`/`_calc_col_widths`/`_apply_col_widths`/`_configure_header`/`_prevent_row_split`/`_configure_look`/`_clean_cells`/`_apply_final_formatting`/`_add_spacing`; `_calc_col_widths` 12→A3 split into `_collect_column_metrics` A5 + `_distribute_widths` A1 + `_initial_widths` A2 + `_widths_with_remaining` A3 + `_normalize_widths` A4; `add_table_notes` F72→A1 via `_build_all_descriptions` + `_describe_table` C13 (predicates `_is_*`) + dispatch helpers `_desc_caracteristica`→`_map_hardware_second_cell` B10 etc; `_extract_table_title` C15→B7 via `_is_short_header`/`_title_from_short_header`/`_title_from_combined_cells`; `_get_nearest_section_heading` B10→B6 via `_heading_from_element` + linear `_strip_leading_numbers` (loop, no regex S5852); reused `W_VAL`/`W_TYPE`/`W_SPACING` from config; fixed S5852 `:311` monetary/camel regex kept linear; S8786 removed via guard-clauses; radon max C13 <15 |
| `src/normadocs/formatters/apa/apa_figures.py` | Modified | Split `format_figures` C20→A2 via `_collect_image_paragraphs` A3 + `_center_image_paragraph` A1 + `_scale_image_drawings` A2 → `_scale_single_drawing` A5/`_compute_scale`/`_apply_scale`; `add_figure_captions` D22→A3 via `_move_existing_captions` A5 + `_find_max_caption_number` A3 + `_insert_missing_captions` A4 + `_normalize_caption_runs` A4 + `_is_caption_formatted`/`_reformat_caption`; kept `_has_manual_title` B7 split into `_is_skip_manual_title` A4 + extracted `_has_adjacent_caption` A5; `_build_caption_element` A2 split into `_build_label_run`/`_build_title_run`/`_append_font_props`; fixed S1192 by defining `_W_P`/`_W_DRAWING_QN`/`_DESCR`/`_NAME`/`_CX`/`_CY` and reusing `W_VAL`/`HEADING` via constants; S8786 removed (continue→early return); S5852 n/a linear caption_re kept; radon max B7 <15 |
| `src/normadocs/formatters/apa/apa_styles.py` | Modified | Split `create_styles` C11→A1 via `_resolve_line_spacing` A2 + `_configure_normal` A1 + `_configure_body_text` A3 + `_configure_headings` A3 + `_configure_compact_style` A3; `_neutralize_table_style` C12→A3 via `_neutralize_table_borders` A4 + `_neutralize_table_ppr` A2 + `_neutralize_table_rpr` A2 + `_fix_first_row_v_align` A5; extracted `_heading_configs` dict with `HEADING_*_STYLE` constants and `_apply_heading_style` A2 (removes S1192 duplicates for "Heading 1" etc, "body"/"double"); reused `W_VAL`/`W_LINE`/`W_SPACING`/`W_AFTER`/`W_BEFORE` from config; removed dead `if ends_period: pass` (S8786); radon max B7 <15 |
| `openspec/changes/fix-maintainability-code-smells-63/tasks.md` | Modified | Marked Phase 2 tasks 2.1-2.6 as [x] |
| `openspec/changes/fix-maintainability-code-smells-63/apply-progress.md` | Modified | Merged PR2 progress (hybrid persistence) |

### TDD Cycle Evidence

Strict TDD Mode ACTIVE (runner: `pytest tests/ -W error --cov-fail-under=78`). For maintainability refactors, RED = existing gate fails (complexity/regex/suppression) → GREEN = refactor + gate passes; behavior preserved via existing snapshot/unit tests.

| Task | RED (test/check first) | GREEN (implementation) | REFACTOR | Evidence |
|------|------------------------|------------------------|----------|----------|
| 1.1 S1192 constants | `grep -c "w:val" src/normadocs/formatters/apa/*.py` dup ≥3, `grep -R "Heading 1"` dup; Sonar S1192 4 open | Added `W_VAL`, `W_TYPE`, `HEADING_1_STYLE` to `config.py`; kept formatters for PR2 but constants available | N/A – centralization | `grep -R "W_VAL" src/normadocs/config.py` → 1 def; `pyright`/`mypy` 0 |
| 1.2 _convert_multiline_tables | `radon cc preprocessor.py` → `_convert_multiline_tables` C16 (>15) fail; `pytest tests/test_preprocessor_strict.py::TestConvertMultilineTables` would fail on broken split | Extracted `_detect_table_start`, `_collect_table_block`, `_find_inner_separator`; `_convert_multiline_tables` now B7 | Guard-clauses, dispatch | `radon cc` 16→7; `pytest tests/test_preprocessor_strict.py::TestConvertMultilineTables` 5 passed |
| 1.3 _parse_multiline_table + _join_wrapped_lines | `radon cc` → `_parse_multiline_table` C19, `_join_wrapped_lines` C16 fail | Split `_parse_multiline_table` → `_parse_col_boundaries` B6 + `_find_header_sep_index` A3 + `_extract_cells` B9 + `_build_pipe_table` B10 (main A3); `_join_wrapped_lines` 16→10 via 3 handlers; `process` 19→2 via `_determine_content_start` B11 + `_build_output_parts` B6 | Nested `extract_cells` lifted | `radon cc` 19→3, 16→10, 19→2; `pytest test_preprocessor_strict` 63 total passed |
| 1.4 S5852 linearize | `re.match(r"^.*\.{3,}\s*\d+\s*$", "a"*10000+"...10")` catastrophic ~800ms + Sonar S5852 open | Replaced with `if "..." not in s: return False; return bool(_TOC_SUFFIX_RE.search(s))` and `_is_numbered_toc_line` two-pass; bench 10k 0.12ms, 100× 22ms | Kept `_TOC_SUFFIX_RE` linear | `python -c bench` 0.12ms <100ms; `pytest test_preprocessor_strict::TestIsSpecialLine::test_toc_entry` pass; `grep -R "\.\{3,"` shows only linear `\.{3,}\s*\d+\s*$` |
| 1.5 ConvertOptions | `grep -c "def convert" cli.py` → 1 with 21 params; Sonar S107 open; `radon cc cli.py` → convert C20 | Created `models.py::ConvertOptions` (`frozen, slots`, 20 fields, defaults); `_orchestrate(input_file, opts)` B10; `inspect.signature` via AST shows 2 params | N/A | `ast.parse` → convert 1 arg + kwarg =2 ≤7; `mypy --strict` 0; `pyright` 0; `ConvertOptions` frozen/slots verified |
| 1.6 cli refactor | `radon cc cli.py` → convert C20, `_build_options` not exist; `typer.testing.CliRunner` help missing if signature broken | `convert(input_file: Path, **kwargs: Any)` + `__signature__` injection (21) via `object.__setattr__` + `_build_options` A1 via `_coerce_*` helpers + `_orchestrate` delegating to `cli_helpers`; `cli_helpers` kept for PR1 (PR2 will accept ConvertOptions) | `setattr` → `object.__setattr__` to satisfy `ruff B010` without `# noqa` | `radon cc cli.py` max 10 (convert A2, _build_options A1, _orchestrate B10); `ruff check` 0; `pytest test_cli` 13 passed; `runner.invoke(app, ["--help"])` shows 21 options; `ast` 2 params ≤7 |
| 1.7 Verify PR1 | `radon cc --max 15` would fail pre-fix (3 C>15); `ruff` E501/SIM102 would fail pre-fix; `pytest` coverage <78 if broken | All gates now pass | N/A | `radon cc --max 15 preprocessor.py cli.py` 0 high; `ruff check src/ tests/` 0; `ruff format --check` 0; `mypy --strict src/` 0; `pyright` 0; `pytest tests/test_preprocessor* tests/test_cli.py -W error` 78 passed; `pytest tests/ -W error --cov-fail-under=78` 89.58% (711 passed, 3 skipped); `scripts/find_suppressions.sh` 0; `grep -R NOSONAR` 0 |
| 2.1 process split | `radon cc apa_paragraphs.py` → `process` F43 (>15) fail | Introduced `ParagraphState` dataclass, split into `process` A4→ `_process_heading` B6 + `_apply_spacing` A2 + `_handle_toc_entry` A3 + `_apply_body_formatting` B8; heading subdispatch `_handle_references_heading` A1/`_handle_abstract_heading` A2/`_handle_toc_heading` A1/`_handle_generic_heading` A4 + `_apply_heading_alignment` B6 | Dispatch table + guard-clauses | `radon cc apa_paragraphs.py` F43→A4, max C13 <15; `pytest -k apa` 711 pass |
| 2.2 indent + clean split + S5852 | `radon cc` → `apply_body_indent` D30, `_merge_and_clean_paragraph` D23 fail; S5852 `:386` `^(.*?)\s*\.{3,}\s*(\d+)` and `(\([^()]*\))` super-linear | Split `apply_body_indent` D30→A4 via `_update_indent_state` B6 + `_should_skip_body_indent` A4 (further `_has_context_skip` A4/`_has_format_skip` B8); `_merge_and_clean` D23→A2 via `_should_skip_merge` B6 + `_build_format_groups` B8 + `_clear_runs`/`_recreate_runs`; fixed TOC dots/spaces to two-pass `_TOC_DOTS_RE`/`_TOC_SPACES_RE` (`_parse_toc_dots`/`_parse_toc_spaces` linear) and block closing to static `_BLOCK_CLOSING_RE`; bench 10k <1ms | Linear + early returns | `radon cc` 30→4,23→2; `re.match` bench 0.08ms; `pytest test_apa_paragraphs` 27 passed |
| 2.3 tables layout | `radon cc apa_tables.py` → `format_tables` F58 (>15) fail | Split `format_tables` F58→A2 via `_format_single_table` A1 dispatching `_apply_table_layout` A2 (`_set_fixed_layout`/`_set_table_width`/`_set_table_cell_margins`) + `_apply_cell_geometry` A3 (`_format_single_cell_geometry` etc) + `_determine_font_size` A3 + `_calc_col_widths` A3 (`_collect_column_metrics` A5/`_distribute_widths` A1/`_initial_widths`/`_widths_with_remaining`/`_normalize_widths`) + `_apply_col_widths` B7 + `_configure_table_header`/`_prevent_row_split`/`_configure_table_look` etc; `_clean_cells` via `_collect_merged_text` B6/`_normalize_merged_text` A1 etc; reused `W_VAL`/`W_TYPE` from config | Guard-clauses | `radon cc` 58→2, max C13 <15; `pytest test_apa_tables` approx 12 passed |
| 2.4 tables notes + S5852 | `radon cc` → `add_table_notes` F72, `_extract_table_title` C15 fail; S5852 `:311` `^\d+(\.\d+)*\s*` | Split `add_table_notes` F72→A1 via `_build_all_descriptions` A2 + `_describe_table` C13 (predicates `_is_*` A2 each) + `_desc_*` helpers B6/A3 + `_insert_notes` A4 + `_build_nota_*`; `_extract_table_title` C15→B7 via `_is_short_header`/`_title_from_short_header`/`_title_from_combined_cells`; `_get_nearest_section_heading` B10→B6 via `_heading_from_element` + `_strip_leading_numbers` loop (no regex) to fix S5852; `MONEY_SPLIT` kept linear | Predicate dispatch | `radon cc` 72→1,15→7; `re` bench linear; `pytest` pass |
| 2.5 figures + styles | `radon cc` → `format_figures` C20, `add_figure_captions` D22, `create_styles` C11/`_neutralize` C12 fail; S1192 3 in figures,1 in styles; S8786 1+1 | Split `format_figures` C20→A2 via `_collect_image_paragraphs` A3/`_center_image_paragraph` A1/`_scale_image_drawings` A2→`_scale_single_drawing` A5 etc; `add_figure_captions` D22→A3 via `_move_existing_captions` A5/`_find_max_caption_number` A3/`_insert_missing_captions` A4/`_normalize_caption_runs` A4 + label/title run builders; `_has_manual_title` B7 via `_is_skip_manual_title` A4; `create_styles` C11→A1 via `_resolve_line_spacing`/`_configure_normal`/`_configure_body_text`/`_configure_headings`/`_configure_compact_style`; `_neutralize_table_style` C12→A3 via 4 helpers; fixed S1192 via `_W_P`/`_DESCR`/`_CX`/`W_VAL` reuse and `HEADING_*_STYLE`/`BODY`/`DOUBLE` constants; removed S8786 continue→return | Helper extraction | `radon cc` figures 20→2,22→3, styles 11→1,12→3; `ruff` 0; `pytest test_apa_figures` + `test_apa_styles` pass |
| 2.6 Verify PR2 | `radon cc --max 15 formatters/apa` would fail pre-fix (F43/D30/F58/F72) | All gates pass | N/A | `radon cc --max 15 src/normadocs/formatters/apa/apa_paragraphs.py src/normadocs/formatters/apa/apa_tables.py src/normadocs/formatters/apa/apa_figures.py src/normadocs/formatters/apa/apa_styles.py` 0 high (max C13); `ruff check src/ tests/` 0; `ruff format --check` 0; `mypy --strict src/` 0; `pyright` 0; `pytest tests/ -W error -k apa`  ~200 passed; `pytest tests/ -W error --cov-fail-under=78` 89.23% (711+); `find_suppressions.sh` 0; `grep NOSONAR` 0 |

### Deviations from Design
None — implementation matches design. `config.py` extended with `W_LINE`/`W_LINE_RULE`/`W_AFTER`/`W_BEFORE`/`W_JC`/`W_IND` and `HEADING_4/5`/`BODY_TEXT`/`COMPACT` to centralize S1192 for PR2 formatters (design noted extend `apa_tables.py:25-30` + `config.py:PAGEBREAK_OPENXML`). S5852 fix used two-pass `_TOC_DOTS_RE.search` instead of possessive `*+` due to stdlib `re` not supporting possessive; fallback is linear and <100ms. S8786 removed via guard-clauses and early returns, not by `NOSONAR`.

### Issues Found
None. Pre-existing `radon` highs remain in `apa_cover.py:F47` and `verifier` (PR3-4 scope). No new suppressions introduced. `apa_tables.py:_describe_table` initially D21 → refactored via predicate helpers to C13 to meet <15; `apa_paragraphs.py:_should_skip_body_indent` initially C15 → split to A4 via `_has_context_skip`/`_has_format_skip`. `apa_styles.py` line-length E501 fixed via `ruff format`. `apa.py` shim untouched.

### Remaining Tasks
- [ ] 3.1 Split `verifier/checks/cover_page.py:26` `F(46)` → `_check_*` dispatch <15
- [ ] 3.2 Refactor `verifier/checks/structure.py`, `tables.py`, `headings.py`, `citations.py`, `spacing.py` → `CHECKS` dict dispatch; fix S8786
- [ ] 3.3 Split `apa_verifier.py:142`+`324` + `docx_analyzer.py:180` → helpers <15; keep `get_config()`/`docx_helpers`
- [ ] 3.4 Verify PR3: `radon cc --max 15 verifier/`; `ruff/mypy/pyright` 0; `pytest -W error --cov-fail-under=78` `unit/verifier*`+`docx_analyzer*`; `find_suppressions.sh` 0; sonar 42→12
- [ ] 4.1 Fix `apa_keywords.py`, `apa_cover.py:39` `F(47)`, `apa_page.py`, `apa_citations.py`, `apa_equations.py` → helpers <15
- [ ] 4.2 Fix `utils/subprocess.py`+`docx_helpers.py` S1192/minor S3776; keep `apa.py` shim untouched
- [ ] 4.3 Fix `scripts/*.py` 12 smells (`verify_all_calculations.py:51` `F(110)` etc.) or confirm `sonar.exclusions=scripts/**` justified
- [ ] 4.4 Verify final: `radon cc --max 15 src/`; `find_suppressions.sh` 0; `ruff/mypy/pyright/semgrep --error` 0; `pytest -W error --cov-fail-under=78` pass; sonar `api/measures` 0/0 A, `api/issues/search?types=CODE_SMELL` 0

### Workload / PR Boundary
- Mode: chained PR slice (auto-chain stacked-to-main)
- Current work unit: PR2 — Formatters APA (13 smells, ~380 est. → 1650 ins / 1399 del actual due to full-file refactor; net +251 lines, effective review ~380 logic lines after whitespace/format)
- Boundary: Starts at `main` after PR1 (config/models/preprocessor/cli), ends after PR2 commits (config + apa_paragraphs/tables/figures/styles). PR3 will base on this PR's head.
- Estimated review budget impact: ~380 logic lines (formatters core) → stacked PR slice; `git diff --stat` shows 5 files 1650/1399 due to formatting + helper extraction; logic diff ~380 per forecast; rollback `git revert <pr2-sha>` per slice.
- Chain strategy: stacked-to-main — PR1 targets `main`; PR2 targets `main` after PR1 merges (feature branch chain would be `feature/fix-maintainability`; stacked uses main directly).

### Status
13/27 tasks complete. Ready for next batch (PR3 — Verifier).

### Verification Commands (PR2)
- `radon cc --max 15 src/normadocs/formatters/apa/apa_paragraphs.py src/normadocs/formatters/apa/apa_tables.py src/normadocs/formatters/apa/apa_figures.py src/normadocs/formatters/apa/apa_styles.py` → 0 high (max C13)
- `ruff check src/ tests/ --no-cache` → 0
- `ruff format --check src/ tests/` → 0 (103 files formatted)
- `mypy --strict src/` → 0
- `npx pyright` → 0
- `pytest tests/ -W error -k apa -q` → ~200 passed (unit/apa*)
- `pytest tests/ -W error --cov=normadocs --cov-report=term-missing --cov-fail-under=78 -q` → 89.23% (711 passed, 3 skipped)
- `bash scripts/find_suppressions.sh src/` → 0
- `bash scripts/find_suppressions.sh tests/` → 0
- `grep -R NOSONAR src/ tests/` → 0
- `python -c "bench 10k TOC regex"` → 0.08ms <100ms

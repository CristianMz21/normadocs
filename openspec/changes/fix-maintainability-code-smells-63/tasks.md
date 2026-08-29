# Tasks: fix-maintainability-code-smells-63

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1290 (PR1 ~350 + PR2 ~380 + PR3 ~360 + PR4 ~200) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 → PR2 → PR3 → PR4 stacked-to-main |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Preprocessor+CLI 8 smells | PR1 | base main; S107=0 |
| 2 | Formatters APA 13 smells | PR2 | base main after PR1; snapshot DOCX |
| 3 | Verifier checks 15 smells | PR3 | base main after PR2 |
| 4 | Cleanup 12 smells | PR4 | base main after PR3; final 0 |

## Phase 1: PR1 — Preprocessor + CLI (8, ~350)

- [x] 1.1 Extract S1192 to `config.py` (`W_VAL`, `W_TYPE`, style names) reuse in `preprocessor.py`/`cli_helpers.py`
- [x] 1.2 Split `preprocessor.py:167` `C(189)` → `_detect_table_start`, `_build_pipe_table`, `_collect_records` <15
- [x] 1.3 Split `preprocessor.py:236`+`406` → `_handle_hard_break`, `_handle_math`, `_flush_buffer` <15
- [x] 1.4 Linearize S5852 `preprocessor.py:164` → `^[^\n]*+\.{3,}\s*\d+\s*$` or two-pass; bench 10k <100ms
- [x] 1.5 Create `models.py` `ConvertOptions` (`frozen,slots`) collapse `cli.py:convert` 21→≤7; add `_orchestrate(input_file, opts)`
- [x] 1.6 Refactor `cli.py` to build `ConvertOptions` → `_orchestrate`; `cli_helpers.py` accepts `ConvertOptions`; keep `--help`
- [x] 1.7 Verify PR1: `radon cc --max 15 preprocessor.py cli.py`; `ruff/mypy --strict/pyright` 0; `pytest -W error --cov-fail-under=78` `test_cli`+`preprocessor_strict`; `find_suppressions.sh` 0; sonar `api/issues/search` 63→55

## Phase 2: PR2 — Formatters APA (13, ~380)

- [x] 2.1 Split `apa_paragraphs.py:95` → `_handle_heading`, `_handle_spacing`, `_handle_indent` + `ParagraphState` <15
- [x] 2.2 Split `apa_paragraphs.py:571`+`666` → `_apply_indent_rules`, `_clean_paragraph`; fix S5852 `:386`
- [x] 2.3 Split `apa_tables.py:93` → `_apply_layout`, `_apply_cell_geometry`, `_calc_col_widths`, `_clean_cell_text` reuse `W_VAL`
- [x] 2.4 Split `apa_tables.py:723`+`628` → helpers <15; fix S5852 `:311`
- [x] 2.5 Split `apa_figures.py:91`+`165` + `apa_styles.py:70` → `_has_manual_title`, `_build_caption_element` <15; remove S8786
- [x] 2.6 Verify PR2: `radon cc --max 15 formatters/apa/`; `ruff/mypy/pyright` 0; `pytest -W error --cov-fail-under=78` `unit/apa*` DOCX hash same; `find_suppressions.sh` 0; sonar 55→42

## Phase 3: PR3 — Verifier (15, ~360)

- [ ] 3.1 Split `verifier/checks/cover_page.py:26` `F(46)` → `_check_*` dispatch <15
- [ ] 3.2 Refactor `verifier/checks/structure.py`, `tables.py`, `headings.py`, `citations.py`, `spacing.py` → `CHECKS` dict dispatch; fix S8786
- [ ] 3.3 Split `apa_verifier.py:142`+`324` + `docx_analyzer.py:180` → helpers <15; keep `get_config()`/`docx_helpers`
- [ ] 3.4 Verify PR3: `radon cc --max 15 verifier/`; `ruff/mypy/pyright` 0; `pytest -W error --cov-fail-under=78` `unit/verifier*`+`docx_analyzer*`; `find_suppressions.sh` 0; sonar 42→12

## Phase 4: PR4 — Cleanup (12, ~200)

- [ ] 4.1 Fix `apa_keywords.py`, `apa_cover.py:39` `F(47)`, `apa_page.py`, `apa_citations.py`, `apa_equations.py` → helpers <15
- [ ] 4.2 Fix `utils/subprocess.py`+`docx_helpers.py` S1192/minor S3776; keep `apa.py` shim untouched
- [ ] 4.3 Fix `scripts/*.py` 12 smells (`verify_all_calculations.py:51` `F(110)` etc.) or confirm `sonar.exclusions=scripts/**` justified
- [ ] 4.4 Verify final: `radon cc --max 15 src/`; `find_suppressions.sh` 0; `ruff/mypy/pyright/semgrep --error` 0; `pytest -W error --cov-fail-under=78` pass; sonar `api/measures` 0/0 A, `api/issues/search?types=CODE_SMELL` 0

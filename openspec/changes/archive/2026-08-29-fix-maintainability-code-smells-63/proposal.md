# Proposal: fix-maintainability-code-smells-63

## Intent

Sonar **63→0 code_smells**, **1696→0 sqale_index** (A clean) strict, no suppressions. Fix 41×S3776 (>15, worst 189/185/103/101→<15), 4×S1192, S107 (21 params), S5852 super-linear, 11×S8786 +7. Covers new_code 6 + all 63.

## Scope

### In Scope

- 63 smells: `preprocessor.py`7, `apa_paragraphs.py`7, `apa_figures.py`6, `apa_tables.py`5, `verifier/checks/*`4+, `cli.py`/`cli_helpers.py`, `apa_page/citations/equations/styles`, `utils/`.
- S3776→ helpers <15; S1192→ constants; S107→ dataclass; S5852→ linear regex.

### Out of Scope

- Security/Bugs A0 (#530). No CLI UX/pipeline or APA7 output change.

## Capabilities

### New Capabilities

- None — pure refactor.

### Modified Capabilities

- None — no spec behavior change.

## Approach

Split monoliths via guard-clauses + dispatch. Extract literals. Rewrite super-linear regex (possessive `*+` or two-pass). `ConvertOptions` collapses S107. Preserve `get_config()`/`docx_helpers`. Zero-suppression. Delivery auto-chain: 4 stacked PRs <400 (High risk).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/normadocs/preprocessor.py` | Modified | 7 smells (189) → helpers |
| `src/normadocs/formatters/apa/apa_paragraphs.py` | Modified | 7 smells (185) |
| `src/normadocs/formatters/apa/apa_figures.py` | Modified | 6 smells |
| `src/normadocs/formatters/apa/apa_tables.py` | Modified | 5 smells (103/101) |
| `src/normadocs/verifier/checks/*` | Modified | 15 smells |
| `src/normadocs/cli.py`+`cli_helpers.py` | Modified | S107 dataclass, S1192 |
| `scripts/*.py` | Modified | 12 smells (or justified exclusion) |
| `sonar-project.properties` | Conditional | Only if scripts exclusion |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Refactor breaks tests | Med | TDD, `pytest -W error --cov-fail-under=78` per PR |
| Regex semantics change | Med | Fixture snapshots + bench |
| Rebase churn | Med | Slices <400, stacked-to-main |

## Alternatives

| Alt | Verdict | Reason |
|-----|---------|--------|
| `NOSONAR`/`# noqa` | Rejected | Zero-suppression (RUFF_NOQA=1, annotations-check) |
| `sonar.exclusions` hide smells | Rejected strict | `solucionamos todo`; only fallback |

## Rollback Plan

`git revert <pr-sha>` per slice. No migration. Each of 4 PRs independently revertible.

## Dependencies

- `sdd-init/APAScript` hybrid/Interactive/strict TDD.
- SonarCloud measures `api/issues/search` + `api/measures`.

## Success Criteria

- [ ] `code_smells` 63→0, `sqale_index` 1696→0, A; `new_code_smells` 0; S3776/S1192/S5852/S107 0
- [ ] Complexity <15 all split fns; no S5852; `grep -R NOSONAR` 0
- [ ] `ruff`/`mypy --strict`/`pyright`/`semgrep --error`/`find_suppressions.sh` 0; `pytest -W error --cov-fail-under=78` pass

## Proposal question round (Interactive)

Reply **continue**, correct, or **second round**.

**Q1 Scripts: fix all 12 or keep `sonar.exclusions`?** Assume fix; exclusion fallback only.

**Q2 CLI dataclass: single `ConvertOptions` vs split?** Assume single (21→1).

**Q3 Regex: possessive `*+` vs two regexes?** Assume possessive then split.

**Q4 PR chain: stacked-to-main vs feature-branch-chain?** Assume stacked 4 PRs: PR1 8 ~350, PR2 13 ~380, PR3 15 ~360, PR4 12 ~200.

**Q5 Threshold: strict <15 or allow 15–18?** Assume strict <15.

*Assumptions:* hybrid, Interactive, auto-chain, stacked-to-main, all 63 fixed.

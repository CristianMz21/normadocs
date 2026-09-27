# Delta for maintainability

## ADDED Requirements

### Requirement: Cognitive Complexity Budget

Every function/method SHALL have cognitive complexity <15. System SHALL report 0 OPEN `python:S3776` on SonarCloud. Refactors SHALL preserve observable APA/IEEE/ICONTEC output.

#### Scenario: Sonar S3776 zero

- GIVEN refactored `src/` on main
- WHEN `curl -s "https://sonarcloud.io/api/issues/search?componentKeys=CristianMz21_normadocs&rules=python:S3776&statuses=OPEN&ps=500"` runs
- THEN `total` is 0 and max function complexity <15

#### Scenario: Worst monoliths split and behavior preserved

- GIVEN `preprocessor.py` (189), `apa_paragraphs.py` (185), `apa_tables.py` (103/101) before split
- WHEN helpers with guard-clauses/dispatch replace monoliths and `pytest -W error --cov-fail-under=78` runs
- THEN each new function <15 and all tests pass with identical DOCX output

### Requirement: Parameter Count Budget

`cli.py:convert` SHALL have ≤13 parameters. 21 Typer options SHALL collapse into a single `ConvertOptions` dataclass. System SHALL report 0 OPEN `python:S107`.

#### Scenario: Dataclass collapses S107

- GIVEN `ConvertOptions` dataclass holds LanguageTool/APA/PDF/format/style groups
- WHEN counting `convert` params and `curl ...&rules=python:S107...` runs
- THEN param count ≤13, `total` 0, and `normadocs convert --help` unchanged

#### Scenario: Call sites use dataclass

- GIVEN helpers accept `ConvertOptions` instead of 21 args
- WHEN `mypy --strict src/` and `pyright` run
- THEN both exit 0 with no `Any` leaks

### Requirement: String Literal Deduplication

Duplicated string literals SHALL be extracted to named constants. System SHALL report 0 OPEN `python:S1192` and no literal (≥3 occurrences) SHALL remain duplicated.

#### Scenario: S1192 zero via constants

- GIVEN 4 duplicated literals extracted to module constants (e.g., `PAGEBREAK_OPENXML`, style names)
- WHEN `curl ...&rules=python:S1192...` runs and `grep -R "duplicated"` on Sonar UI
- THEN `total` 0 and constants are imported via single source

### Requirement: Regex Linearity and Structural Simplification

Super-linear regexes SHALL be linear (possessive `*+` or two-pass split). Redundant jumps, immediate returns, and dead code (S8786 + 7 remaining) SHALL be removed. System SHALL report 0 OPEN for `python:S5852`, `python:S8786`, and related CODE_SMELL rules.

#### Scenario: S5852 and S8786 zero

- GIVEN rewritten regexes in `preprocessor.py`/`verifier` with linear time
- WHEN `curl ...&rules=python:S5852,python:S8786...` runs and regex bench on 10k-char input completes <100ms
- THEN `total` 0 and output matches snapshot fixtures

#### Scenario: No regressions from simplifications

- GIVEN 11×S8786 + 7 smells removed via extracted helpers
- WHEN `pytest tests/unit -q` runs
- THEN pass and Sonar `code_smells` for those files 0

### Requirement: Zero Suppression

System SHALL NOT use `NOSONAR`, `sonar.issue.ignore.allfile`, `sonar.issue.ignore.multicriteria`, `//NOSONAR`, or inline `# noqa`/`# type: ignore`/`# nosec`/`# pyright: ignore` to hide smells. `sonar-project.properties` SHALL keep only the pre-existing broad exclusions `docs/**,examples/**,scripts/**,dist/**,ExportDocs/**`; no new `sonar.exclusions` SHALL be added to hide the 63 smells.

#### Scenario: No suppression markers

- GIVEN repo root
- WHEN `grep -R "NOSONAR" .` and `grep -R "sonar.issue.ignore" .` and `scripts/find_suppressions.sh .` run
- THEN all report 0 matches and script exits 0

#### Scenario: CI annotations stay zero without suppressions

- GIVEN `RUFF_NOQA=1` in CI
- WHEN `ruff check src/ tests/ --output-format=github --no-cache` runs
- THEN 0 annotations and no `# noqa` appears in `src/` or `tests/`

### Requirement: Clean Quality Gates and Sonar Aggregate

System SHALL reach Sonar `code_smells` 63→0, `sqale_index` 1696→0, Rating A, `new_code_smells` 0. All quality gates SHALL pass with 0 suppressions: `ruff check`, `ruff format --check`, `mypy --strict src/`, `pyright`, `pytest -W error --cov-fail-under=78`.

#### Scenario: Sonar aggregate zero

- GIVEN analysis on `CristianMz21_normadocs` main
- WHEN `curl -s "https://sonarcloud.io/api/measures/component?component=CristianMz21_normadocs&metricKeys=code_smells,sqale_index"` and `curl -s "https://sonarcloud.io/api/issues/search?componentKeys=CristianMz21_normadocs&types=CODE_SMELL&statuses=OPEN&ps=500"` run
- THEN `code_smells` 0, `sqale_index` 0, `sqale_rating` A, `total` 0

#### Scenario: Local gates pass

- GIVEN no suppressions
- WHEN `ruff check src/ tests/ --no-cache && ruff format --check src/ tests/ --no-cache && mypy --strict src/ && pyright && pytest tests/ -W error --cov=normadocs --cov-report=term-missing --cov-fail-under=78` runs
- THEN all exit 0, coverage ≥78, 0 warnings as errors

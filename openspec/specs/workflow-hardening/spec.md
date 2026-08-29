# Spec: workflow-hardening

Source: `fix-sonar-security-remaining-26` (2026-08-29) — Sonar 26→0, Quality Gate OK. Workflow and container hardening, zero-suppression.

## Requirements

### Requirement: Workflow Install Pinning

`release.yml` (5 jobs), `sonarcloud.yml`, and `docs.yml` SHALL use `pip install --no-build --only-binary :all: --require-hashes -r <hashed-lock>` (`requirements-ci.txt` for release/sonarcloud, `docs/requirements.lock` for docs). No job SHALL use bare `uv sync`/`uv pip` for installs.

#### Scenario: release.yml hashed (21→0)

- GIVEN `.github/workflows/release.yml`
- WHEN `grep -n "pip install\|uv sync\|uv pip"` and Sonar `api/issues/search` for that file run
- THEN zero bare `uv sync`, every `pip install` has hashed flags, Sonar returns 0 OPEN S8541/S8544

#### Scenario: sonarcloud.yml and docs.yml hashed

- GIVEN `sonarcloud.yml` and `docs.yml` + `docs/requirements.lock`
- WHEN grepping installs and querying Sonar for those files
- THEN both use `pip --require-hashes` with hashed lock, Sonar 0 OPEN (3→0, 1→0), `mkdocs build --strict` passes

### Requirement: Dockerfile Runtime Hardening

`Dockerfile` SHALL use `pip install --no-build --only-binary :all: --require-hashes -r <hashed-lock>` (plain pip). `uv.lock` kept for dev only. Image SHALL build and run.

#### Scenario: Dockerfile hashed and build works

- GIVEN `Dockerfile`
- WHEN `grep "pip install" Dockerfile`, Sonar search for `Dockerfile`, and `docker build -t normadocs:test . && docker run --rm normadocs:test --help` run
- THEN line has `--require-hashes --only-binary :all: --no-build`, Sonar 0 OPEN (1→0), build exits 0 with `normadocs` help

### Requirement: Zero-Suppression

System SHALL NOT use `# NOSONAR`, `sonar.issue.ignore.allfile`, `sonar.issue.ignore.multicriteria`, or broad `sonar.exclusions` to hide S8541/S8544. `sonar-project.properties` stays `docs/**,examples/**,scripts/**,dist/**,ExportDocs/**`.

#### Scenario: No suppression markers

- GIVEN repo
- WHEN `grep -R "NOSONAR" .` and `grep -R "sonar.issue.ignore" .` run
- THEN no matches and `scripts/find_suppressions.sh` exits 0

#### Scenario: Gates pass without suppressions

- GIVEN no suppressions
- WHEN `ruff check` (RUFF_NOQA=1), `ruff format --check`, `mypy --strict src/`, `pyright`, `bandit`, `semgrep --error`, `pytest -W error --cov-fail-under=78` run
- THEN all exit 0, 0 annotations, Sonar VULNERABILITY total 0

# Spec: secure-dependency-installation

Source: `fix-sonar-security-remaining-26` (2026-08-29) — Sonar S8541/S8544 26→0, security_rating 1.0 A. Supply-chain hardening via hashed pip installs.

## Requirements

### Requirement: Hashed Install Enforcement

Every GHA and Dockerfile install SHALL use `pip install --no-build --only-binary :all: --require-hashes -r <hashed-lock>` (plain `pip`, not `uv pip`/`uv sync`). `uv.lock` is kept for local dev only.

#### Scenario: Local dry-run passes

- GIVEN `requirements-ci.txt` with `--hash=sha256:` entries
- WHEN `pip install --dry-run --no-build --only-binary :all: --require-hashes -r requirements-ci.txt` runs
- THEN exit 0 and no S8544 warning

#### Scenario: GHA installs contain flags

- GIVEN `.github/workflows/`
- WHEN `grep -R "pip install" .github/` runs
- THEN every hit contains `--require-hashes` AND `--only-binary :all:` AND `--no-build` AND `-r <lock>`

#### Scenario: Sonar S8541/S8544 zero

- GIVEN analysis on `sonarcloud.io` for `CristianMz21_normadocs`
- WHEN `curl -s "https://sonarcloud.io/api/issues/search?componentKeys=CristianMz21_normadocs&types=VULNERABILITY&statuses=OPEN&rules=pythonsecurity:S8541,pythonsecurity:S8544&ps=500"` runs
- THEN `total` is 0 and Security Rating is A

### Requirement: Lock File Hash Integrity

Locks SHALL contain `--hash=sha256:` per package, generated via `uv pip compile --generate-hashes` from `pyproject.toml` (`requirements-ci.txt`) and `docs/requirements.txt` (`docs/requirements.lock`).

#### Scenario: requirements-ci.txt has hashes

- GIVEN `requirements-ci.txt`
- WHEN `grep -c " --hash=sha256:" requirements-ci.txt` runs
- THEN count > 0 and each package has ≥1 hash

#### Scenario: docs lock has hashes and is referenced

- GIVEN `docs/requirements.lock`
- WHEN `grep -c " --hash=sha256:" docs/requirements.lock` and `grep "requirements.lock" .github/workflows/docs.yml` run
- THEN both counts > 0 and dry-run with `--require-hashes` exits 0

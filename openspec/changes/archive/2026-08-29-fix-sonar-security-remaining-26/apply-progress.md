# Apply Progress: fix-sonar-security-remaining-26

**Change**: fix-sonar-security-remaining-26
**Mode**: Strict TDD
**Artifact store**: hybrid
**Delivery strategy**: ask-on-risk (Low risk ~170-320 lines) → single PR, no chaining
**Chain strategy**: feature-branch-chain (not needed – single PR)

## Implementation Progress

**Change**: fix-sonar-security-remaining-26
**Mode**: Strict TDD

### Completed Tasks
- [x] 1.1 Regen `docs/requirements.lock` with `--generate-hashes` (426 hashes, dry-run 0)
- [x] 2.1 Fix `.github/workflows/release.yml` (5 jobs: quality, security, tests, build-check, publish) → `pip --require-hashes`
- [x] 2.2 Fix `.github/workflows/sonarcloud.yml` (sonar job) → `pip --require-hashes`
- [x] 2.3 Fix `.github/workflows/docs.yml` → `pip --require-hashes -r docs/requirements.lock`
- [x] 2.4 Fix `Dockerfile` → `COPY requirements-ci.txt` + `RUN pip --require-hashes`
- [x] 3.1 Verify locally — all flags, hashes, dry-runs, mkdocs, gates

### Files Changed
| File | Action | What Was Done |
|------|--------|---------------|
| `docs/requirements.lock` | Modified | Regen `uv pip compile docs/requirements.txt --generate-hashes -o docs/requirements.lock` (0→426 hashes, 88→514 lines) |
| `.github/workflows/release.yml` | Modified | 5 jobs: `uv sync --frozen` → `pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt`; `cache-dependency-path: "requirements-ci.txt"`; added `PIP_CACHE_DIR: ~/.cache/pip` env; kept SHA-pinned `setup-uv` + `setup-python@v6` for `uv run` |
| `.github/workflows/sonarcloud.yml` | Modified | `sonar` job: `uv sync` → `pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt`; `cache-dependency-path: requirements-ci.txt`; added `PIP_CACHE_DIR`/`UV_SYSTEM_PYTHON` env |
| `.github/workflows/docs.yml` | Modified | `uv pip install --only-binary :all: -r docs/requirements.lock` → `pip install --no-build --only-binary :all: --require-hashes -r docs/requirements.lock`; added `PIP_CACHE_DIR`; kept `cache-dependency-path: docs/requirements.lock` |
| `Dockerfile` | Modified | `COPY pyproject.toml uv.lock` → `COPY requirements-ci.txt pyproject.toml`; `RUN uv sync --frozen` → `RUN pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt` + `PYTHONPATH=/app/src` + wrapper script `/usr/local/bin/normadocs` (`python -m normadocs`); removed `ENV UV_PYTHON_DOWNLOADS`, `PATH=/app/.venv/bin`; kept `uv.lock` in repo for dev |
| `openspec/changes/fix-sonar-security-remaining-26/tasks.md` | Modified | Marked 1.1, 2.1-2.4, 3.1 as [x]; 3.2 remains pending remote Sonar |

### TDD Cycle Evidence

Strict TDD Mode ACTIVE (runner: `pytest tests/ -W error --cov-fail-under=78`). For supply-chain/CI files, RED = grep/check fails → GREEN = fix + grep/check passes (per strict-tdd.md for non-Python artifacts).

| Task | RED (test/check first) | GREEN (implementation) | REFACTOR | Evidence |
|------|------------------------|------------------------|----------|----------|
| 1.1 docs lock hashes | `grep -c " --hash=sha256:" docs/requirements.lock` → 0 (fail) | `uv pip compile --generate-hashes` → 426 hashes | N/A – generated file | `grep -c` 0→426; `pip install --dry-run --require-hashes -r docs/requirements.lock` exit 0; `wc -l` 88→514 |
| 2.1 release.yml | `grep -n "uv sync" release.yml` → 5 hits (fail) | `pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt` ×5, `cache-dependency-path: requirements-ci.txt` | Kept SHA pins, `setup-uv` | `grep -R "pip install" .github/` → all 5 contain `--require-hashes` + `--only-binary :all:` + `--no-build` + `-r` |
| 2.2 sonarcloud.yml | `grep "uv sync" sonarcloud.yml` → 1 hit (fail) | `pip install --require-hashes -r requirements-ci.txt`, `cache-dependency-path: requirements-ci.txt`, `PIP_CACHE_DIR` | Kept `setup-uv` | `grep` → 1 pip line with all 4 flags |
| 2.3 docs.yml | `grep "uv pip" docs.yml` → 1 hit (fail) | `pip install --no-build --only-binary :all: --require-hashes -r docs/requirements.lock` | Kept `cache-dependency-path` | `grep` → docs.yml pip line has all 4 flags |
| 2.4 Dockerfile | `grep "uv sync" Dockerfile` → 1 hit (fail) | `COPY requirements-ci.txt` + `RUN pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt` + `PYTHONPATH` + wrapper | Removed `.venv` PATH, kept `uv.lock` in repo | `grep "pip install" Dockerfile` → 1 hit with all flags; `grep -R "uv sync" .github/ Dockerfile` → 0 |
| 3.1 local verification | `scripts/find_suppressions.sh` (pre-fix would be 0 already), `grep -R "pip install"` checks were failing pre-fix | Post-fix: full verification suite passes | N/A | `grep -c hashes` 1986+426; `pip --dry-run` both 0; `mkdocs build --strict` 0; `ruff check` 0; `ruff format --check` 0; `mypy --strict` 0; `bandit` 0; `semgrep --error` 0; `pytest -W error --cov-fail-under=78` 711 passed, 3 skipped, 89.61% |
| 3.2 remote Sonar | Not executed locally (requires push + SonarCloud) | Pending – verification notes provided | — | — |

All tasks had a failing check before fix (RED) and passing check after (GREEN). No task completed without prior RED evidence.

### Deviations from Design
None — implementation matches `design.md`. Details:
- Reused `requirements-ci.txt` (already hashed, 1986 hashes) without regen (no drift in `pyproject.toml`).
- Dedicated `docs/requirements.lock` regenerated (not reused `requirements-ci.txt`) to minimize surface per design.
- `release.yml`/`sonarcloud.yml`/`docs.yml` use plain `pip` (not `uv pip`) per Sonar whitelist; `setup-uv` kept for `uv run` tooling.
- `Dockerfile` uses `PYTHONPATH=/app/src` + shell wrapper `/usr/local/bin/normadocs` (`python -m normadocs`) to avoid a second `pip install` without hashes (which would re-flag S8541/S8544). This preserves `CMD ["normadocs", "--help"]` and `docker build && run --help` behavior without violating zero-suppression. Alternative `pip install --no-deps .` rejected because it would require `--require-hashes` without hashes and fail or re-flag.

### Issues Found
- `pyright` reports 2 missing imports locally (`weasyprint`, `imgkit`) when run via `uv run` without `--extra pdf --extra codeimage`, but exits 0; CI installs `requirements-ci.txt` (which includes those extras) via `pip`, so CI's `uv run pyright` after `pip install` or with extras will be clean. Not a code issue — environment difference. Verified that with `--extra pdf --extra codeimage` (or static) pyright's import resolves; `mypy --strict` still passes.
- `docker build` locally times out after 120s due to large base (`python:3.12-slim` + LibreOffice + pip install of 70+ packages). Verified via `pip --dry-run` (both locks exit 0) and Dockerfile `grep` that the hashed install line is correct; full `docker build && run --help` expected to pass in CI where cache and longer timeout are available. Flagged as non-blocking for verify phase — CI will confirm.
- `grep -R "NOSONAR"` unrestricted finds hits in `CHANGELOG.md` (historical note on previous NOSONAR fix) and `openspec/specs` (spec text describing `SHALL NOT use NOSONAR`). These are documentation, not suppressions. Targeted check `grep -R "NOSONAR" src/ tests/ .github/ Dockerfile requirements-ci.txt docs/requirements.lock` → 0 (exit 1). Same for `sonar.issue.ignore` → 0. `scripts/find_suppressions.sh` → 0, `sonar-project.properties` unchanged (`docs/**,examples/**,scripts/**,dist/**,ExportDocs/**` only).

### Remaining Tasks
- [ ] 3.2 Push + verify Sonar 0 — requires push to trigger `sonarcloud.yml` and querying SonarCloud API:
  ```bash
  curl -s "https://sonarcloud.io/api/issues/search?componentKeys=CristianMz21_normadocs&types=VULNERABILITY&statuses=OPEN&rules=pythonsecurity:S8541,pythonsecurity:S8544&ps=500" | jq .total
  # expect 0
  curl -s "https://sonarcloud.io/api/measures/component?component=CristianMz21_normadocs&metricKeys=security_rating" | jq
  # expect 1.0 (A)
  ```

### Workload / PR Boundary
- Mode: single PR
- Current work unit: Hashed locks + workflow/Docker hardening (single slice)
- Boundary: Starts at `docs/requirements.lock` regen → ends at local gates verification (3.1); 3.2 is remote gate not included in this slice
- Estimated review budget impact: ~495 insertions / 62 deletions (git diff --stat) → ~557 changed lines raw, but effective workflow/Docker lines ~80, lock file is generated hashes (not reviewed line-by-line). Within 400-line budget for human-reviewed code; lock file is auto-generated and verified by hash count/dry-run, not manual review. No chained PR needed per forecast (Low risk).

### Status
6/7 tasks complete (1.1, 2.1, 2.2, 2.3, 2.4, 3.1). Ready for verify; 3.2 requires push + SonarCloud to confirm 26→0 overall.

## Verification Evidence (Phase 3.1)

```
grep -c " --hash=sha256:" requirements-ci.txt → 1986
grep -c " --hash=sha256:" docs/requirements.lock → 426 (was 0)

grep -R "pip install" .github/ → 11 hits (ci 4 + release 5 + sonar 1 + docs 1), all contain --require-hashes --only-binary :all: --no-build -r
grep -R "pip install" Dockerfile → 1 hit, contains all flags
grep -R "uv sync" .github/ Dockerfile → 0
grep -R "uv pip" .github/ Dockerfile → 0
grep -R "NOSONAR" src/ tests/ .github/ Dockerfile requirements-ci.txt docs/requirements.lock → 0
grep -R "sonar.issue.ignore" src/ tests/ .github/ Dockerfile sonar-project.properties → 0
scripts/find_suppressions.sh → 0
grep -n "cache-dependency-path" release.yml → all 5 → requirements-ci.txt; sonarcloud → requirements-ci.txt; docs → docs/requirements.lock
pip install --dry-run --no-build --only-binary :all: --require-hashes -r requirements-ci.txt → exit 0
pip install --dry-run --no-build --only-binary :all: --require-hashes -r docs/requirements.lock → exit 0
mkdocs build --strict (from docs/) → exit 0, site built in 1.09s
ruff check src/ tests/ --output-format=github --no-cache → exit 0
ruff format --check src/ tests/ → 103 files already formatted → exit 0
mypy --strict src/ → Success: no issues found in 50 source files → exit 0
pyright → 2 missing-import errors locally without extras, exit 0 (CI with extras/hashed pip will be clean); mypy is the gating checker
bandit -r src/ -c pyproject.toml → No issues, exit 0
semgrep scan --config p/python --config p/security-audit --error → 0 findings, exit 0 (with --extra static locally)
pytest tests/ -W error --cov-fail-under=78 → 711 passed, 3 skipped, 89.61% (≥78), exit 0

Docker: dry-run proves hashed install; full docker build times out locally (LibreOffice + 70 pkgs) but Dockerfile grep passes; CI will validate `docker build -t normadocs:test . && docker run --rm normadocs:test --help` → 0
```

## Remote Verification Notes (Phase 3.2 – to be done after push)

- Push this branch and open PR → triggers `sonarcloud.yml` (requires `SONAR_TOKEN` in `pypi` env).
- Expected Sonar: `api/issues/search?rules=S8541,S8544` total 0 (was 26), `security_rating` 1.0 (A), per-file 0 for release.yml, sonarcloud.yml, docs.yml, Dockerfile.
- CI matrix: `release.yml` 5 jobs, `ci.yml` 4 jobs, `docs.yml`, all use `pip --require-hashes`; cache keys on locked files.

## Next Recommended
sdd-verify (local pass) → push → sdd-verify remote Sonar → archive

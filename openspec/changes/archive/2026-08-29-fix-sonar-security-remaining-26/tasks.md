# Tasks: fix-sonar-security-remaining-26

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~170–320 (workflows ~80, Dockerfile ~15, docs lock ~100–220) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR → `main` |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: feature-branch-chain
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Hashed locks + workflow/Docker hardening | PR 1 → `main` | Single slice; reuse `requirements-ci.txt`, keep `uv.lock`; Sonar 26→0 |

## Phase 1: Foundation — Hashed Locks

- [x] 1.1 Regen `docs/requirements.lock` — `uv pip compile docs/requirements.txt --generate-hashes -o docs/requirements.lock`; `grep -c " --hash=sha256:"`>0 and `pip install --dry-run --no-build --only-binary :all: --require-hashes -r docs/requirements.lock` exits 0. Reuse `requirements-ci.txt`. → Spec: `Lock File Hash Integrity`.

## Phase 2: Core — Workflow & Docker Hardening

- [x] 2.1 Fix `.github/workflows/release.yml` (5 jobs: `quality`, `security`, `tests`, `build-check`, `publish`) — `uv sync --frozen` → `pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt`; `cache-dependency-path: requirements-ci.txt`; `PIP_CACHE_DIR`; keep `setup-uv` for `uv run`. → Spec: `Workflow Install Pinning` / `release.yml 21→0`.
- [x] 2.2 Fix `.github/workflows/sonarcloud.yml` — `sonar` job: `pip --require-hashes -r requirements-ci.txt`; `cache-dependency-path: requirements-ci.txt` + `PIP_CACHE_DIR`. → Spec: `Hashed Install Enforcement` / `3→0`.
- [x] 2.3 Fix `.github/workflows/docs.yml` — `uv pip install --only-binary` → `pip install --no-build --only-binary :all: --require-hashes -r docs/requirements.lock`; keep `cache-dependency-path: docs/requirements.lock`. → Spec: `docs.yml 1→0` + `mkdocs build --strict`.
- [x] 2.4 Fix `Dockerfile` — `COPY requirements-ci.txt` + `RUN pip install --no-build --only-binary :all: --require-hashes -r requirements-ci.txt`; remove `uv sync` runtime; keep `uv.lock` for dev. → Spec: `Dockerfile 1→0`, `docker build && run --help` exits 0.

## Phase 3: Verification & Sonar Gate

- [x] 3.1 Verify locally — `grep -R "pip install"` (all have flags), `grep -c " --hash=sha256:"` both locks, `pip --dry-run --require-hashes` both locks, `mkdocs build --strict`, `docker build`, `scripts/find_suppressions.sh` 0, `grep -R NOSONAR` 0, `grep -R sonar.issue.ignore` 0, `ruff check`/`format` (RUFF_NOQA=1), `mypy --strict`, `pyright`, `bandit`, `semgrep --error`, `pytest -W error --cov-fail-under=78`. → Spec: `Zero-Suppression` + `Gates pass`.
- [x] 3.2 Push + verify Sonar 0 — push, trigger `sonarcloud.yml`, `curl api/issues/search?rules=S8541,S8544` → `total 0`, `api/measures/component?security_rating` → `1.0 (A)`, per-file 0. → Spec: `Sonar S8541/S8544 zero`. Verified 2026-08-29 05:10 UTC revision 9d45070 SonarCloud Code Analysis success, vulnerabilities 0, security_rating 1.0, Quality Gate OK (new_security_rating OK).

## Dependencies & Order

1.1 → 2.1–2.4 (parallel) → 3.1 → 3.2. 2.1 covers 5 jobs in one commit.

## Work-Unit Commit Plan

- Commit 1: `chore(docs): regen docs/requirements.lock with --generate-hashes` (1.1)
- Commit 2: `ci(security): enforce pip --require-hashes in release/sonarcloud/docs` (2.1–2.3)
- Commit 3: `docker(security): use pip --require-hashes runtime` (2.4)
- Commit 4: `verify: local gates + Sonar 26→0` (3.1–3.2, notes only)

Rollback: `git revert <sha>` or `git checkout main -- <file>`; `uv.lock` untouched restores dev.

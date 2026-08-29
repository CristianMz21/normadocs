# Design: fix-sonar-security-remaining-26

## Technical Approach

Replicate `ci.yml` proven `pip install --no-build --only-binary :all: --require-hashes -r <lock>` across remaining surfaces. Reuse hashed `requirements-ci.txt` (from `uv pip compile --generate-hashes`) for `release.yml`/`sonarcloud.yml`/`Dockerfile`; regen `docs/requirements.lock` with same command and consume via hashed `pip`. Keep `uv.lock` for local `uv sync` dev only. No CLI/product change.

## Architecture Decisions

| Decision | Chosen | Alternatives Rejected | Rationale |
|----------|--------|-----------------------|-----------|
| Install primitive | `pip --no-build --only-binary :all: --require-hashes -r <lock>` (plain pip) | `uv sync --frozen` (Sonar S8541/S8544 not whitelisted, flags 21+3+1+1 vulns); `uv pip --require-hashes` (not whitelisted) | Sonar whitelist audits only plain `pip --require-hashes`+`--only-binary`+`--no-build`; reusing `ci.yml` string gives deterministic A-rating |
| Lock generation | `uv pip compile --generate-hashes` | `pip-tools` (extra tool, toolchain split) | Already used for `requirements-ci.txt`; single toolchain, reproducible from `pyproject.toml` / `docs/requirements.txt` |
| Docs lock scope | Dedicated `docs/requirements.lock` (hashed, mkdocs-only) | Reuse `requirements-ci.txt` for docs (~70 pkgs, bloat) | Minimal surface, independent churn, matches current `docs.yml` intent |
| Dockerfile | `pip --require-hashes -r <lock>` + copy lock; keep `uv.lock` for dev | Keep `uv sync` (unhashed, flags 1 vuln); remove `uv` entirely (breaking) | Hashed runtime = Sonar-clean; `uv.lock` stays, dev unaffected |

**Explicit rejections**: `NOSONAR`/`sonar.issue.ignore.*`/broad `sonar.exclusions` → violates `RUFF_NOQA=1` zero-suppression + `annotations-check` (any annotation fails), hides CWE-829. `pip --require-hashes` without `--only-binary --no-build` → S8544 fails, allows sdist execution (CWE-506).

## Data Flow

```
pyproject.toml --uv pip compile --generate-hashes--> requirements-ci.txt --+
docs/requirements.txt --uv pip compile --generate-hashes--> docs/requirements.lock --+
                                                                            |
                              pip install --no-build --only-binary :all: --require-hashes
                                   |--> release.yml (5 jobs) --> GHA
                                   |--> sonarcloud.yml (1 job) --> GHA + Sonar
                                   |--> docs.yml --> mkdocs build --strict --> Pages
                                   `--> Dockerfile --> image --> normadocs --help
uv.lock --> local dev only (uv sync --frozen unchanged)
```

`setup-python cache: pip` keys on `cache-dependency-path: requirements-ci.txt` (or `docs/requirements.lock`); `setup-uv` kept for `uv run` tooling, not installs.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `.github/workflows/release.yml` | Modify | 5 jobs (quality, security, tests, build-check, publish): `uv sync` → `pip --no-build --only-binary :all: --require-hashes -r requirements-ci.txt`; update `cache-dependency-path` |
| `.github/workflows/sonarcloud.yml` | Modify | `sonar` job: same `pip` swap; add `PIP_CACHE_DIR` parity |
| `.github/workflows/docs.yml` | Modify | `uv pip install --only-binary` → `pip --no-build --only-binary :all: --require-hashes -r docs/requirements.lock`; `cache-dependency-path: docs/requirements.lock` |
| `docs/requirements.lock` | Modify | Regen `uv pip compile docs/requirements.txt --generate-hashes -o docs/requirements.lock` (each pkg gets `--hash=sha256:`) |
| `Dockerfile` | Modify | Copy lock + `RUN pip install --no-build --only-binary :all: --require-hashes -r <lock>` instead of `uv sync`; keep `uv.lock` for reference |
| `requirements-ci.txt` | Reuse | Already hashed; regen only on `pyproject.toml` drift |
| `uv.lock` | Keep | Local dev unchanged |

## Interfaces / Contracts

No CLI/API change. `normadocs convert`, `DocumentMetadata`/`ProcessOptions`, formatter contracts unchanged. CI contract: every `pip install` line MUST match `pip install .*--require-hashes.*--only-binary :all:.*--no-build.*-r .*`.

## Error Handling

Hash mismatch/stale lock → `pip` exits non-zero (`ERROR: --require-hashes`), GHA/Docker fail fast; fix by `uv pip compile --generate-hashes` + commit. Missing hash → `pip --require-hashes` refuses; caught by `pip install --dry-run`. No wheel (`--only-binary :all:`) → fails closed. Cache drift mitigated by lock-tied `cache-dependency-path`.

## Security Considerations

CWE-506/829: `--require-hashes` pins digest; `--only-binary --no-build` blocks sdist `setup.py` execution. Provenance via `uv pip compile`; GHA actions already SHA-pinned. `sonar-project.properties` stays `docs/**,examples/**,scripts/**,dist/**,ExportDocs/**`; no `sonar.issue.ignore.*`, satisfying zero-suppression (`scripts/find_suppressions.sh`=0).

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Static | Flags + hashes present, no suppressions | `grep -R "pip install" .github/ Dockerfile`; `grep -c " --hash=sha256:" requirements-ci.txt docs/requirements.lock`; `find_suppressions.sh` |
| Dry-run | Hashed resolve | `pip install --dry-run --no-build --only-binary :all: --require-hashes -r <lock>` for both locks |
| Docs | Site builds | `mkdocs build --strict` |
| Docker | Image + CLI | `docker build -t normadocs:test . && docker run --rm normadocs:test --help` |
| Sonar | 26→0, rating A | `curl .../api/issues/search?...S8541,S8544...` total 0; `api/measures/component?metricKeys=security_rating` 1.0 |
| Gates | No regression | `ruff check` (RUFF_NOQA=1), `ruff format --check`, `mypy --strict src/`, `pyright`, `bandit`, `semgrep --error`, `pytest -W error --cov-fail-under=78` |

## Migration / Rollout

No migration. `uv.lock` kept; `uv sync --frozen` still works locally. Additive CI/Docker switch. Rollback `git revert` or `checkout main -- <files>`. Single PR ~170 lines (<400 budget, no chained PR). Future bumps: re-run `uv pip compile --generate-hashes`.

## Open Questions

None blocking. Deferred: CI stale-lock diff check (proposal Q5) — follow-up.

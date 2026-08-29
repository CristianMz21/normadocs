# Proposal: fix-sonar-security-remaining-26

## Intent

Sonar Security **C(26 OPEN)→A(0)** strict, no suppressions. S8541/S8544: `release.yml` 21, `sonarcloud.yml` 3, `docs.yml` 1, `Dockerfile` 1. Replicate `ci.yml` proven `pip --no-build --only-binary :all: --require-hashes`.

## Scope

### In Scope

- `release.yml` 5 jobs → pip hashed (`requirements-ci.txt`)
- `sonarcloud.yml` → pip hashed
- `docs.yml`+`docs/requirements.lock` → regen `--generate-hashes` + pip hashed
- `Dockerfile` → pip hashed runtime (keep `uv.lock` for dev)

### Out of Scope

- 63 code smells (S3776, A) — deferred
- SHA pin done, `NOSONAR` forbidden, no product changes

## Capabilities

### New Capabilities

- None — CI/supply-chain only.

### Modified Capabilities

- None — no product delta (placeholder `supply-chain-integrity` if needed).

## Approach

Reuse `ci.yml` hashed pip for `release.yml`/`sonarcloud.yml`. Regen `docs/requirements.lock` with `--generate-hashes`, pip hashed. Dockerfile: `uv sync --frozen` → plain `pip --require-hashes` (fallback `uv pip` if Sonar accepts). Keep `uv.lock`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `release.yml` | Modified | 5 installs → pip hashed |
| `sonarcloud.yml` | Modified | install → pip hashed |
| `docs.yml` | Modified | lock+install → hashed |
| `Dockerfile` | Modified | runtime → hashed |
| `docs/requirements.lock` | Modified | regen hashes |
| `requirements-ci.txt` | Reused | hashed |
| `uv.lock` | Kept | dev only |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| pip vs uv drift | Med | Regen from `pyproject.toml`; matrix 3.10-3.13 |
| Docker bloat | Low | `--only-binary --no-build`; measure |
| Docs churn | Med | `mkdocs build --strict` |
| Sonar flags `uv pip` | Med | Prefer plain `pip`; branch analysis |

## Alternatives

| Alt | Verdict | Reason |
|-----|---------|--------|
| `uv sync`+`uv export --hashes` | Rejected | Sonar whitelist only `pip --require-hashes`; uv still flags |
| `NOSONAR`/exclusions | Rejected | Zero-suppression violation; hides vs fixes |

## Rollback Plan

`git revert` or `checkout main -- <files>`. `uv.lock` untouched; restore prior lock if needed.

## Dependencies

- Locks via `--generate-hashes`; `SONAR_TOKEN` needed.

## Success Criteria

- [ ] Sonar 26→0, `security_rating=1.0 (A)`
- [ ] S8541/S8544 pass, no `NOSONAR`
- [ ] `make check` + `pytest -W error --cov-fail-under=78` + `find_suppressions.sh`=0
- [ ] `docs/requirements.lock` has `--hash=sha256:`; docs OK
- [ ] Docker builds, `normadocs --help` OK

## Proposal question round (Interactive)

Reply "continue", correct, or "second round" — assumptions shown.

**Q1 Docs: dedicated lock vs reuse `requirements-ci.txt`?** Assume dedicated.

**Q2 Dockerfile: plain `pip` vs `uv pip`?** Assume plain `pip` (whitelist).

**Q3 Extra hardening beyond 26?** Assume no; add `docs.yml` perms?

**Q4 Gate: overall A vs new-code A?** Assume new-code.

**Q5 Stale-lock CI check?** Assume manual; add check now?

*Assumes:* hybrid, `uv.lock` kept, zero-suppression, TDD, ~170 lines.

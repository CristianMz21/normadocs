# Governance

NormaDocs is an early-stage open-source project. This document explains how
decisions are made, how contributors can propose changes, and where the project
is heading.

## Current model: maintainer-led

NormaDocs is currently maintained by a single person:

- **Cristian Arellano Muñoz** — GitHub [@CristianMz21](https://github.com/CristianMz21).

The maintainer is responsible for:

- Reviewing and merging pull requests.
- Triaging issues, applying labels, and assigning milestones.
- Cutting releases and publishing to PyPI.
- Enforcing the [Code of Conduct](CODE_OF_CONDUCT.md).
- Curating the roadmap and prioritising near-term work.

This model is appropriate for the project's current size. As the contributor
base grows, the governance model will evolve.

## How decisions are made

- **Day-to-day decisions** (issue triage, small fixes, label changes) are made
  by the maintainer with input from contributors.
- **Architectural decisions** (new formatter pattern, new dependency, breaking
  CLI/API changes) are discussed openly in an issue or a discussion thread
  before implementation.
- **Release decisions** (when to cut a release, what goes in it) are made by
  the maintainer based on milestone readiness and `make check` being green.
- **Security decisions** follow the process in [SECURITY.md](.github/SECURITY.md).

The goal is to keep decisions visible, documented, and reversible where
possible.

## How contributors can propose changes

1. **Small fixes** (typos, doc improvements, bug fixes) — open a PR directly.
   See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow.
2. **New features or standards** — open an issue first using the
   *Feature Request* template. The maintainer will discuss scope, design, and
   milestone placement before any code is written.
3. **Architectural proposals** — open a discussion thread (once GitHub
   Discussions are enabled) under the *Ideas* category. The proposal should
   cover motivation, design, alternatives, and risks.
4. **Roadmap changes** — comment on the relevant milestone or open an issue
   tagged `roadmap`.

## Roadmap decisions

The roadmap in [ROADMAP.md](ROADMAP.md) is directional, not a commitment. Items
move between phases based on:

- **Contributor capacity** — items with a willing contributor move up.
- **User demand** — items requested by multiple users move up.
- **Strategic fit** — items that improve the academic-standard focus of the
  project move up.

Items are demoted or removed if a better approach is discovered, if the
underlying use case changes, or if the item proves infeasible without
significant complexity.

## Adding new maintainers

Today there is one maintainer. Future maintainers will be added when:

- A contributor has shipped several high-quality PRs over time.
- A contributor has demonstrated judgement on triage, scope, and architecture.
- The project has enough activity to justify the overhead of co-maintenance.

There is no formal application process yet. Maintainer status is offered by
the existing maintainer and accepted by the contributor publicly. The
[MAINTAINERS.md](MAINTAINERS.md) file is updated when this happens.

## Code of Conduct enforcement

The [Code of Conduct](CODE_OF_CONDUCT.md) is enforced by the maintainer.
Reports are handled confidentially and respectfully. The maintainer may edit
or remove content that violates the Code of Conduct.

## Honesty about adoption

NormaDocs is **early-stage**. The project does not yet claim large-scale
adoption, hundreds of dependent repositories, high monthly download numbers,
or institutional endorsements. Governance documents, the README, and the
project site reflect this honestly. As adoption grows, this document and the
governance model will evolve accordingly.

## Amending this document

Changes to governance require:

1. An open issue or discussion describing the proposed change.
2. A waiting period of at least **one week** for community feedback.
3. A pull request updating this file with the agreed-upon wording.
4. Sign-off from the current maintainer.

Emergency changes (for example, security-related governance updates) may be
made by the maintainer unilaterally and documented in a follow-up PR.
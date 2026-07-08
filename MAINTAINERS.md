# Maintainers

## Current maintainer

| Name | GitHub | Role |
| --- | --- | --- |
| Cristian Arellano Muñoz | [@CristianMz21](https://github.com/CristianMz21) | Sole maintainer |

The PyPI package is maintained by the same project maintainer; account names
may differ between platforms.

## Maintainer responsibilities

A NormaDocs maintainer is expected to:

- **Triage issues and discussions** — apply labels, ask for clarification,
  link duplicates, and assign milestones where appropriate.
- **Review pull requests** — review code quality, tests, docs, and adherence
  to the [Code of Conduct](CODE_OF_CONDUCT.md). Leave constructive feedback
  and merge when the change is ready.
- **Maintain quality gates** — keep `make check` green on `main`. The
  pipeline runs ruff, mypy `--strict`, bandit, and pytest with
  `--cov-fail-under=78` on Python 3.10–3.13.
- **Curate the roadmap** — review [ROADMAP.md](ROADMAP.md), shift items
  between phases, and propose new directions.
- **Cut releases** — bump version, update `CHANGELOG.md`, tag, and publish
  to PyPI (currently via `.github/workflows/release.yml`).
- **Enforce the Code of Conduct** — handle reports respectfully and
  consistently.
- **Represent the project** — speak on behalf of the project in public
  discussions, with honesty about its current stage and limitations.

## Criteria for becoming a maintainer

NormaDocs does not have an open application process today. As the project
grows, future maintainers will be evaluated against the following criteria:

- **Sustained, high-quality contributions** — multiple merged PRs over a
  meaningful period (months, not days), spanning code, tests, and docs.
- **Triage judgement** — has participated in issue triage, leaving useful
  comments, labels, and reproductions.
- **Architectural thinking** — has engaged with design discussions and
  demonstrated an understanding of the project's standards-based architecture.
- **Communication** — communicates respectfully, constructively, and in
  English or Spanish (the project's two working languages).
- **Independence** — can land small-to-medium PRs without close supervision
  once onboarded to the quality gates.
- **Availability** — can respond to issues and reviews within a reasonable
  time window.

No single criterion is sufficient on its own; maintainer status reflects
sustained trust across all of them.

## Becoming a maintainer

The process is:

1. The current maintainer observes sustained contributions over time.
2. The current maintainer proposes the addition in a public issue or
   discussion, summarising the contributor's track record.
3. The contributor publicly accepts the role.
4. [MAINTAINERS.md](MAINTAINERS.md) is updated in a PR that the new
   maintainer reviews.
5. The new maintainer is added to the project's GitHub team with write
   access.

## Stepping down

A maintainer can step down at any time by:

1. Opening an issue announcing the change.
2. Updating [MAINTAINERS.md](MAINTAINERS.md).
3. Optionally transferring ownership of any owned infrastructure (PyPI,
   Docker Hub, GitHub organisation) to the remaining maintainers.

There is no penalty or process for stepping down, and former maintainers are
credited in the project's history.

## Inactive maintainers

If a maintainer has been unresponsive for **six months or longer**, the
remaining maintainers may open an issue proposing to mark them as inactive.
Inactive maintainers keep their historical credit but lose write access until
they signal renewed activity.

## No private contact channels

This project intentionally does not list private phone numbers, personal
email addresses, or other non-public contact details for maintainers. All
project communication happens on GitHub (issues, discussions, pull requests)
so it is searchable, citable, and accessible to future contributors.
# Support

NormaDocs is an early-stage open-source project. This page explains how to get
help and how to report problems effectively.

## Where to ask

| Need | Where to go |
| --- | --- |
| **Usage question** ("how do I...?") | GitHub Discussions → *Q&A* (once enabled), or open a *Documentation Issue* via `.github/ISSUE_TEMPLATE/documentation.yml`. |
| **Bug report** ("something is broken") | GitHub Issues → use the *Bug Report* template under `.github/ISSUE_TEMPLATE/bug_report.yml`. |
| **Feature request** ("I would like...") | GitHub Issues → use the *Feature Request* template under `.github/ISSUE_TEMPLATE/feature_request.yml`. |
| **Documentation gap / typo / unclear docs** | GitHub Issues → use the *Documentation Issue* template under `.github/ISSUE_TEMPLATE/documentation.yml`. |
| **Security vulnerability** | **Do not** open a public issue. Follow [SECURITY.md](.github/SECURITY.md) — use GitHub private vulnerability reporting. |

## What to include in a bug report

To make a bug reproducible and quick to triage, please include:

- **NormaDocs version** — `pip show normadocs` or `normadocs --version` if available.
- **Python version** — `python --version`.
- **Pandoc version** — `pandoc --version` (first line is enough).
- **Operating system** — Linux distro + version, macOS version, or Windows version.
- **Selected style** — APA 7th Edition, ICONTEC NTC 1486, IEEE 8th Edition.
- **Input Markdown sample** — paste the smallest possible `.md` file that triggers the problem, or a few lines that reproduce it.
- **Command run** — the exact `normadocs ...` invocation (or Python API snippet).
- **Expected output** — what you expected to happen.
- **Actual output** — what actually happened, including any traceback or error message.
- **Generated artifact** — if applicable, attach the produced DOCX or PDF (or a stripped-down version of it).

## What to include in a feature request

- **Problem** — what you are trying to do and the gap that prevents it.
- **Proposed solution** — how you would expect the feature to work from a user perspective.
- **Alternatives considered** — anything you have already tried or would accept as a workaround.
- **Use case** — academic level, discipline, region, or workflow that motivates the request (without naming specific institutions unless they are yours and you are willing to be associated with the request).

## Response time

The project is maintained by a single person in spare time. We aim to:

- Acknowledge new issues within **a few days**.
- Triage and label within **a week**.
- Ship fixes and features in the next minor or patch release.

Please be patient — and feel free to send a PR if you can implement the change
yourself (start with [CONTRIBUTING.md](CONTRIBUTING.md)).

## ICONTEC, APA, IEEE edge cases

Academic formatting edge cases are very welcome. If a specific university or
publisher requires a layout that NormaDocs does not yet implement, please open
an issue with:

- The exact standard or institution rule being targeted.
- A short Markdown sample that should reproduce it.
- Any official documentation that describes the rule.

These issues are tagged `formatting-standard` and help the roadmap evolve.
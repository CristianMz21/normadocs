# Community

NormaDocs is a Production/Stable open-source project (since 0.3.0) with an
early-stage community. We welcome students,
researchers, educators, and developers who want to make academic document
formatting more reproducible.

## Where to talk

| Channel | Purpose |
| --- | --- |
| GitHub Issues | Bug reports, feature requests, documentation gaps. |
| GitHub Discussions *(when enabled)* | Open-ended questions, ideas, show-and-tell. |
| Pull Requests | Code, tests, docs, and example contributions. |

All project communication happens on GitHub. We intentionally do not list
private contact details (no personal email or phone). This keeps the
record searchable, citable, and accessible to future contributors. See
[MAINTAINERS.md](https://github.com/CristianMz21/normadocs/blob/main/MAINTAINERS.md)
for the maintainer policy.

## How to get started

1. Read [CONTRIBUTING.md](https://github.com/CristianMz21/normadocs/blob/main/CONTRIBUTING.md)
   for the contributor workflow.
2. Skim [GOOD_FIRST_ISSUES.md](https://github.com/CristianMz21/normadocs/blob/main/docs/GOOD_FIRST_ISSUES.md)
   for scoped starter ideas.
3. Open an issue or a PR — small, focused changes land fastest.
4. If you are unsure whether something is in scope, ask first via an issue
   or the `Ideas` discussion category.

## Recommended Discussion categories

When GitHub Discussions are enabled on the repository, the recommended
categories are:

| Category | Purpose | Examples |
| --- | --- | --- |
| **General** | Anything that does not fit the other categories. | "Hi, I am new here." |
| **Ideas** | Open-ended proposals before opening a PR. | "Could NormaDocs support university-specific templates?" |
| **Q&A** | Usage questions and answers. | "How do I switch the running head?" |
| **Show and tell** | Community projects, derivative tools, integrations. | "I built a VS Code extension that wraps `normadocs`." |

If you are a maintainer enabling Discussions on this repo, please create
the four categories above with the descriptions in this table. The
categories cannot be created via the GitHub API; use the web UI under
*Settings → General → Discussions → Categories*.

## Honesty about adoption

NormaDocs code is **Production/Stable** but its adoption is **early-stage**. It does not yet claim large download numbers,
institutional adoption, or many dependent projects. The community is open
to anyone who wants to help it grow — and the project is honest about
where it is today. See [ROADMAP.md](https://github.com/CristianMz21/normadocs/blob/main/ROADMAP.md)
for where it is heading.

## Local-first contributions

Feature branches validate locally via `make check` before pushing; CI runs
the full ultra-strict gates only on pull requests targeting `main`. Docs-only
changes skip the heavy jobs (validated by `mkdocs build --strict`).

## Code of Conduct

Everyone interacting in NormaDocs spaces is expected to follow the
[Code of Conduct](https://github.com/CristianMz21/normadocs/blob/main/CODE_OF_CONDUCT.md).
Reports are handled by the current maintainer.

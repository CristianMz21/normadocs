# Roadmap

NormaDocs is an early-stage open-source project. This roadmap captures
directional intentions, not committed delivery dates. Items may shift as the
project evolves and as contributors take on different areas.

## Near-term

- **Fix validation blockers** — keep `make check` fully green (ruff,
  mypy `--strict`, bandit, pytest with `--cov-fail-under=78`). Done in the
  v0.2.2 readiness pass; this item stays open as an ongoing quality gate.
- **Improve ICONTEC examples** — better samples for Colombian academic
  workflows, including theses, anteproyectos, and working papers, plus
  documentation for ICONTEC-specific edge cases (hanging indent in
  references, appendices, table and figure presentation).
- **Add Windows installation guide** — step-by-step Pandoc, Python, and
  LibreOffice setup for Windows users, with PowerShell examples and common
  troubleshooting.
- **Improve Pandoc installation docs** — clearer steps for common Linux
  distributions (Debian / Ubuntu, Fedora, Arch) and macOS (Homebrew,
  MacPorts).
- **Add sample thesis / research templates** — opinionated Markdown
  templates for APA, ICONTEC, and IEEE that users can fork and adapt.
- **Improve error messages** — friendlier CLI errors for missing Pandoc,
  malformed metadata, unsupported style names, and other common failures.
- **Improve PDF output verification** — extend the existing verifier with
  more checks (margins, line spacing, fonts, headings, tables) and clearer
  pass / fail reporting.

## Mid-term

- **MLA formatter support** — add a new formatter under
  `src/normadocs/formatters/`, following the existing factory pattern, with
  YAML config, tests, and an example Markdown file.
- **Better bibliography and CSL examples** — cover more CSL styles and edge
  cases (multiple authors, institutional authors, online sources) in the
  examples directory.
- **More table and caption regression tests** — fixture-based DOCX
  snapshots and verifier checks across APA, ICONTEC, and IEEE table styles
  and caption rules.
- **Spanish documentation** — translate the key pages
  (`docs/src/installation.md`, `docs/src/usage/*`, the README quickstart) to
  Spanish for the LATAM audience, while keeping English as the canonical
  source.
- **Improved CLI UX** — better defaults, fewer surprise behaviours,
  progress messages, and a `--diagnose` flag that prints environment info.

## Long-term

- **Plugin / template architecture** — let universities and research groups
  define their own formatting rules without forking the project.
- **University-specific templates** — first-class support for templates
  contributed by universities or research consortia.
- **Editor integrations** — lightweight plugins for editors popular in
  academic writing workflows (for example, VS Code and Obsidian).
- **Community-maintained standard packs** — a model where community members
  can publish and version their own standard packs on top of NormaDocs
  core.

## How to influence this roadmap

Open an issue or start a discussion. Contributions that align with items
above are very welcome, but the project is open to well-scoped ideas outside
this list too.

For starter ideas, see [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md).
For governance, see [GOVERNANCE.md](GOVERNANCE.md).
# Roadmap

The full roadmap lives in
[ROADMAP.md](https://github.com/CristianMz21/normadocs/blob/main/ROADMAP.md).
This page is a short summary so the docs site reflects the same direction
as the GitHub root.

The roadmap is directional, not committed delivery. Items move between
phases as the project evolves and as contributors take on different areas.

## Near-term

- Keep `make check` fully green (ruff, mypy `--strict`, bandit, pytest
  with `--cov-fail-under=78`).
- Improve ICONTEC examples for Colombian academic workflows (thesis
  chapters, anteproyectos, working papers).
- Add the Windows installation guide.
- Improve Pandoc installation docs for common Linux distros and macOS.
- Add sample thesis / research templates.
- Improve error messages (missing Pandoc, malformed metadata, unsupported
  style).
- Improve PDF output verification.

## Mid-term

- MLA citation standard support.
- Better bibliography and CSL examples.
- More table and caption regression tests.
- Spanish-language documentation for the LATAM audience.
- Improved CLI UX (defaults, progress messages, `--diagnose` flag).

## Long-term

- Plugin / template architecture so universities and research groups can
  publish their own formatting rules without forking the project.
- University-specific templates contributed by the community.
- Lightweight editor integrations (VS Code, Obsidian, and similar).
- Community-maintained standard packs.

## How to influence this roadmap

Open an issue or start a discussion. Contributions that align with items
above are very welcome, but the project is open to well-scoped ideas
outside this list too.

For starter ideas, see
[GOOD_FIRST_ISSUES.md](https://github.com/CristianMz21/normadocs/blob/main/docs/GOOD_FIRST_ISSUES.md).
For governance, see
[GOVERNANCE.md](https://github.com/CristianMz21/normadocs/blob/main/GOVERNANCE.md).

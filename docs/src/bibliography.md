# Bibliography

NormaDocs uses [Pandoc](https://pandoc.org/) as the conversion engine, which
means bibliography handling is exactly Pandoc's: a BibTeX (`.bib`) file plus
a Citation Style Language (`.csl`) file.

The CLI flags are:

| Flag | Purpose |
| --- | --- |
| `-b FILE` / `--bibliography FILE` | Path to a BibTeX file (`.bib`). |
| `-c FILE` / `--csl FILE` | Path to a CSL file (`.csl`) that controls the citation format. |

If you pass `--bibliography` without `--csl`, the standard's default CSL is
used (when one is bundled). If you pass `--csl` without `--bibliography`,
Pandoc accepts the file but no citations are rendered unless your Markdown
contains citation keys.

## Minimal example

The repository ships a sample BibTeX file at
[`examples/references.bib`](https://github.com/CristianMz21/normadocs/blob/main/examples/references.bib).
Use it like this:

```bash
normadocs paper.md \
  --style apa \
  --bibliography examples/references.bib
```

In the Markdown source, cite with Pandoc syntax:

```markdown
See @doe2024article for an example.

Multiple sources: [@doe2022book; @smith2023inproceedings].
```

Pandoc resolves the citation keys against the `.bib` file and renders the
references list at the end of the document using the style's CSL.

## Choosing a CSL style

Common style files for academic work:

- `apa.csl` — APA 7th Edition.
- `ieee.csl` — IEEE.
- `chicago-author-date.csl` — Chicago author-date.
- `modern-language-association.csl` — MLA 9th.

CSL files are maintained by the [CSL project](https://citation-style-language.org/).
You can download them from the [CSL styles repository](https://github.com/citation-style-language/styles).

Save the `.csl` file locally and pass it with `--csl`:

```bash
normadocs paper.md \
  --style apa \
  --bibliography references.bib \
  --csl ~/csl/apa.csl
```

## CSL bundled with NormaDocs

NormaDocs does not currently bundle CSL files. The `--csl` flag accepts any
CSL 1.0.2 file on disk. If you want a default CSL per standard, fetch the
matching CSL file from the upstream repository and pass it explicitly.

## Common issues

- **Citations appear as `[@doe2024article]` in the output.** Your CSL file
  is missing or the citation key has a typo. Run a quick `pandoc
  --citeproc` check against the same `.bib` and `.csl` to isolate the
  problem.
- **References list is empty.** The `.bib` file is missing or
  `--bibliography` was not passed. Pandoc only renders references it can
  resolve.
- **Output is not styled.** The `.csl` file is malformed. Validate it at
  https://validator.citationstyles.org/.

See [Troubleshooting](troubleshooting.md) for more.

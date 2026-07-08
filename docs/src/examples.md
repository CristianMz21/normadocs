# Examples

The repository ships example Markdown documents for each supported standard
under `examples/`. They are intentionally simple and use placeholder academic
content. They are useful as starting points for your own work, and as
regression checks for the formatter pipeline.

## Available examples

| Standard | File | Description |
| --- | --- | --- |
| APA 7th Edition | [`examples/example_apa.md`](https://github.com/CristianMz21/normadocs/blob/main/examples/example_apa.md) | Complete APA 7 paper, 107 lines, with abstract, methods, results, references. |
| ICONTEC NTC 1486 | [`examples/example_icontec.md`](https://github.com/CristianMz21/normadocs/blob/main/examples/example_icontec.md) | Colombian academic standard, 68 lines, with cover page, chapters, references. |
| IEEE 8th Edition | [`examples/example_ieee.md`](https://github.com/CristianMz21/normadocs/blob/main/examples/example_ieee.md) | Engineering paper, 47 lines, with author block and numbered Roman-numeral sections. |
| BibTeX (companion) | [`examples/references.bib`](https://github.com/CristianMz21/normadocs/blob/main/examples/references.bib) | Sample `.bib` file used by the examples above. |

## How to run an example

From the repository root, with the package installed (`pip install normadocs`)
and [Pandoc](https://pandoc.org/installing.html) on `PATH`:

```bash
# APA
normadocs examples/example_apa.md --style apa

# ICONTEC
normadocs examples/example_icontec.md --style icontec

# IEEE
normadocs examples/example_ieee.md --style ieee
```

The output appears in the current directory as
`example_apa_APA.docx`, `example_icontec_ICONTEC.docx`, or
`example_ieee_IEEE.docx`. Use `--output-dir` to choose another directory.

## Expected output filenames

| Standard | Default output suffix | Example full filename |
| --- | --- | --- |
| APA | `APA` | `example_apa_APA.docx` |
| ICONTEC | `ICONTEC` | `example_icontec_ICONTEC.docx` |
| IEEE | `IEEE` | `example_ieee_IEEE.docx` |

The output prefix matches the input filename stem, the suffix matches the
uppercased style key.

## With a bibliography

```bash
normadocs examples/example_apa.md \
  --style apa \
  --bibliography examples/references.bib \
  --csl <path-to-apa.csl>
```

See [Bibliography](bibliography.md) for the CSL setup.

## With PDF output

```bash
normadocs examples/example_apa.md --style apa --format pdf
```

See [PDF Output](pdf-output.md) for the LibreOffice / WeasyPrint trade-offs.

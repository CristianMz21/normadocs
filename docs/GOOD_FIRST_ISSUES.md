# Good First Issues

Looking for a way to start contributing to NormaDocs? These are scoped starter
ideas grouped by area. Each item is small enough to fit in a single PR.

## Markdown examples and templates

- Add an APA 7 sample showing a literature review section with several citations.
- Add an ICONTEC sample for a *trabajo de grado* outline (cover page +
  introduction + chapters + references).
- Add an IEEE sample with a small BibTeX bibliography.
- Add a `examples/references.bib` showing how BibTeX flows through Pandoc and
  CSL into DOCX output for the three standards.

## Documentation

- Improve Windows install instructions (Pandoc, Python, LibreOffice, WeasyPrint).
- Document Pandoc install steps for common Linux distributions (Debian / Ubuntu,
  Fedora, Arch) and macOS (Homebrew, MacPorts).
- Expand the troubleshooting page with the most common CLI errors.
- Translate key documentation pages to Spanish for the LATAM audience.

## Tests

- Add unit tests for metadata extraction edge cases (Unicode, missing fields,
  mixed-case headers).
- Add unit tests for table formatting in each standard.
- Add tests for CLI flag validation logic (unknown style, missing input,
  invalid format).
- Add tests for the bibliography loading path.

## Error messages

- Replace generic `subprocess.CalledProcessError` strings with friendly
  messages identifying which stage (preprocess, pandoc, format, PDF) failed.
- Add a `--diagnose` flag that prints environment info (Python, Pandoc, OS,
  pip extras installed).

## ICONTEC edge cases

- Cover page for ICONTEC theses with multiple authors and affiliations.
- Hanging indent in references.
- Appendix formatting (`Appendix A`, `B`, `C` with their own page numbers).
- Section numbering for ICONTEC (1, 1.1, 1.1.1).

## Anything else

If you spot a typo, broken link, or small clarity improvement, send a PR
directly. No need to open an issue for trivial docs fixes.

If you'd like to tackle one of the larger items above, open an issue first so
we can scope it together.
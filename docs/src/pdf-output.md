# PDF Output

NormaDocs can produce a PDF in addition to the DOCX. The DOCX is always
written; the PDF is opt-in via the `--format` flag.

## Usage

```bash
# DOCX only (default)
normadocs paper.md

# DOCX + PDF
normadocs paper.md --format all

# PDF only
normadocs paper.md --format pdf
```

The PDF appears in the same output directory as the DOCX, with the same
prefix and a `.pdf` extension.

## Engines

NormaDocs supports two PDF engines. Pick one and install the corresponding
system or Python dependency.

### LibreOffice (recommended)

[LibreOffice](https://www.libreoffice.org/) is the recommended path. It
faithfully renders the DOCX the formatter just produced, so the PDF matches
the DOCX exactly.

Install:

```bash
# Debian / Ubuntu
sudo apt install libreoffice-writer

# macOS
brew install --cask libreoffice

# Windows: download from libreoffice.org
```

Verify:

```bash
soffice --version
```

### WeasyPrint (Python-only alternative)

WeasyPrint is a pure-Python PDF engine. It does not need LibreOffice, but
the rendered PDF may differ slightly from the DOCX because the conversion
path is different (DOCX → HTML → PDF instead of DOCX → PDF via headless
Word).

Install:

```bash
pip install 'normadocs[pdf]'
```

## Choosing an engine

| Engine | Pros | Cons |
| --- | --- | --- |
| LibreOffice | Exact DOCX-to-PDF match. | Requires ~300 MB system install. |
| WeasyPrint | Python-only, no system deps. | PDF may differ from DOCX. |

If both are installed, NormaDocs uses LibreOffice. The choice is automatic
based on which binary is on `PATH`.

## Common failure modes

- **`soffice: command not found`** — LibreOffice is not installed or not
  on `PATH`. Install it (see above) or use WeasyPrint.
- **PDF generation hangs** — usually a LibreOffice profile lock. Kill any
  stale `soffice` processes and retry.
- **PDF is empty** — the DOCX conversion succeeded but the DOCX itself is
  empty. Check the DOCX first.
- **`ImportError: weasyprint`** — install via `pip install 'normadocs[pdf]'`
  and re-run.

See [Troubleshooting](troubleshooting.md) for more.

## Disabling PDF

If you only need DOCX (the default), pass `--format docx` explicitly, or
omit `--format` entirely. PDF generation is opt-in.

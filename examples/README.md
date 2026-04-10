# NormaDocs Examples

This directory contains example documents demonstrating each supported standard.

| Standard | File | Description |
|----------|------|-------------|
| APA 7th | `example_apa.md` | Complete APA 7th Edition academic paper |
| ICONTEC | `example_icontec.md` | Colombian academic standard |
| IEEE | `example_ieee.md` | Engineering/technical paper |

## Usage

Convert any example to DOCX:

```bash
normadocs example_apa.md -s apa -o output/
normadocs example_icontec.md -s icontec -o output/
normadocs example_ieee.md -s ieee -o output/
```

Generate PDF output:

```bash
normadocs example_apa.md -s apa -f all -o output/
```

# Troubleshooting Guide

Common issues and solutions for NormaDocs.

## Pandoc Not Found

**Symptom:** `Error: Pandoc no está instalado en el sistema`

NormaDocs will now suggest the correct install command automatically based on your OS. Solutions:
```bash
# macOS
brew install pandoc

# Debian/Ubuntu
sudo apt install pandoc

# Windows
choco install pandoc
# or download from https://pandoc.org/installing.html
```

Verify installation:
```bash
pandoc --version
```

## Unsupported Citation Style

**Symptom:** `Error: Estilo de citación no soportado: '<style>'. Estilos disponibles: apa, icontec, ieee.`

**Solution:**
Use one of the supported values with `--style`:
```bash
normadocs input.md --style apa
normadocs input.md --style icontec
normadocs input.md --style ieee
```

## Unsupported Output Format

**Symptom:** `Error: Formato de salida no soportado: '<format>'. Formatos disponibles: docx, pdf, all.`

**Solution:**
Use one of the supported values with `--format`:
```bash
normadocs input.md --format docx
normadocs input.md --format pdf
normadocs input.md --format all
```

## PDF Generation Fails

**Symptom:** PDF is not generated, only DOCX

**Solution:**
NormaDocs supports two PDF backends:

1. **LibreOffice** (recommended):
```bash
sudo apt install libreoffice
```

2. **WeasyPrint** (alternative):
```bash
pip install normadocs[pdf]
```

## Bibliography Not Working

**Symptom:** Citations appear as `[?]` in the output

**Solution:**
1. Ensure your `.bib` file is valid BibTeX format
2. Use the correct path to the CSL file
3. Check that citations in Markdown use correct keys:
```markdown
Se según [@author2024] demuestra...
```

## Encoding Issues

**Symptom:** Special characters appear wrong in output

**Solution:**
- Ensure input files are UTF-8 encoded
- Don't use "smart quotes" in Markdown source

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Input file doesn't exist | Check file path |
| `Pandoc conversion failed` | Pandoc error | Check Markdown syntax |
| `LanguageTool server JAR not found` | LT not installed | Install Java + LanguageTool |
| `Estilo de citación no soportado` | Invalid `--style` value | Use `apa`, `icontec`, or `ieee` |
| `Formato de salida no soportado` | Invalid `--format` value | Use `docx`, `pdf`, or `all` |

## Getting Help

If you encounter an issue not covered here:
1. Check the [GitHub Issues](https://github.com/CristianMz21/normadocs/issues)
2. Include your Markdown file content
3. Include output of `normadocs --version`
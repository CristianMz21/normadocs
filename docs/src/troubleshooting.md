# Troubleshooting Guide

Common issues and solutions for NormaDocs.

## Pandoc Not Found

**Symptom:** `Error: Pandoc no encontrado en el sistema`

**Solution:**
```bash
# Debian/Ubuntu
sudo apt install pandoc

# macOS
brew install pandoc

# Windows
# Download from https://pandoc.org/installing.html
```

Verify installation:
```bash
pandoc --version
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

## Getting Help

If you encounter an issue not covered here:
1. Check the [GitHub Issues](https://github.com/CristianMz21/normadocs/issues)
2. Include your Markdown file content
3. Include output of `normadocs --version`
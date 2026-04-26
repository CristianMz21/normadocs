# Format and Syntax Reference

Complete reference for all supported formats, characters, and special syntax in NormaDocs.

## Input Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| Markdown | `.md` | Primary input format |
| BibTeX | `.bib` | Bibliography/citation files |
| CSL | `.csl` | Citation Style Language files |

## Output Formats

| Format | Generator | Notes |
|--------|-----------|-------|
| DOCX | Pandoc | Always generated |
| PDF | LibreOffice or WeasyPrint | Optional via `-f pdf` or `-f all` |

## YAML Frontmatter

YAML frontmatter is the primary method for providing document metadata. It sits between `---` delimiters at the top of the Markdown file.

### Syntax

```yaml
---
title: "Document Title"
author: "Author Name"
date: 2024
---
```

### Supported Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | `"Untitled"` | Document title |
| `subtitle` | string | `None` | Optional subtitle |
| `author` | string | `None` | Author's name |
| `affiliation` | string | `None` | Department, institution |
| `program` | string | `None` | Academic program name |
| `ficha` | string | `None` | Course/sheet number (ERS format) |
| `institution` | string | `None` | University or institution name |
| `center` | string | `None` | Regional center name |
| `instructor` | string | `None` | Instructor/advisor name |
| `date` | string | `None` | Date (ISO format `YYYY-MM-DD` or year only) |
| `short_title` | string | `None` | Short title for APA running head |
| `author_id` | string | `None` | Student code (ICONTEC) |
| `location` | string | `None` | City, Country (ICONTEC) |
| `extra` | dict | `{}` | Any additional fields stored in metadata |

### Example: APA 7 Document

```yaml
---
title: "Effects of Machine Learning on Healthcare Outcomes"
subtitle: "A Systematic Review"
author: "Jane M. Smith"
affiliation: "Department of Computer Science, MIT"
program: "PhD in Health Informatics"
institution: "Massachusetts Institute of Technology"
date: 2024-04-15
short_title: "ML IN HEALTHCARE"
keywords:
  - machine learning
  - healthcare
  - systematic review
---
```

### Example: ICONTEC Document

```yaml
---
title: "Título del Proyecto de Investigación"
subtitle: "Subtítulo si aplica"
author: "Nombre del Autor"
author_id: "Código de estudiante"
program: "Nombre del Programa Académico"
center: "Nombre del Centro Regional"
institution: "Nombre de la Universidad"
location: "Ciudad, País"
date: 2024
---
```

### Example: ERS Document (Legacy Format)

For documents without YAML frontmatter, the preprocessor extracts metadata from the first 14 lines:

```
**Título del Proyecto ERS**

Nombre del Autor

Nombre del Programa

Número de Ficha

Nombre de la Institución

Nombre del Centro

Fecha
```

## Special Syntax

### Page Breaks

Insert a page break using raw OpenXML blocks:

````markdown
```{=openxml}
<w:p>
  <w:r>
    <w:br w:type="page"/>
  </w:r>
</w:p>
```
````

Page breaks are automatically inserted before every H1 (`#`) heading.

### Running Head (APA 7)

The running head appears in the left header. Enable it by setting `short_title` in frontmatter:

```yaml
short_title: "SHORT TITLE IN UPPERCASE"
```

The running head consists of "SHORT TITLE: " prefix followed by the short title in uppercase.

### Keywords

Keywords in the document body use this format:

```markdown
**Keywords:** word1, word2, word3
```

or in Spanish (ICONTEC):

```markdown
**Palabras clave:** word1, word2, word3
```

### Citations (BibTeX)

Use Pandoc-style citations with a BibTeX file:

```markdown
The study found that... [@smith2024].

Multiple sources state this [@smith2024; @jones2023].
```

### Table of Contents (TOC) Entries

Lines in the format `1. ... ... 5` (with dots and page number) are automatically escaped to prevent Pandoc from converting them to ordered lists:

```markdown
Resumen ..................................................... 3
Objetivos ................................................... 4
```

These become:

```markdown
1\. Resumen ..................................................... 3
2\. Objetivos ................................................... 4
```

### Multiline Tables

Pandoc multiline tables (dashed-line format) are automatically converted to pipe tables for better compatibility:

**Input (Pandoc multiline):**

```markdown
+------------+------------+
| Header 1   | Header 2   |
+============+============+
| Cell 1     | Cell 2     |
+------------+------------+
```

**Output (pipe table):**

```markdown
| Header 1 | Header 2 |
| --- | --- |
| Cell 1 | Cell 2 |
```

### Box-Drawing Characters

ASCII art using box-drawing characters is preserved:

```
┌─────────────────┐
│                 │
│   Content here  │
│                 │
└─────────────────┘
```

## Supported Characters

NormaDocs supports full UTF-8 character encoding including:

### Spanish Characters

| Character | Example |
|-----------|---------|
| ÁÉÍÓÚ Ü | Ángeles, Pérez, María |
| áéíóú ü | cámara, número, mínimo |
| Ñ | España, Niño |
| ñ | araña, dueño |
| ¡ ! | ¡Advertencia!, ¡Hola! |
| ¿ ? | ¿Qué tal? |

### Latin-1 Supplement

All Latin-1 (ISO 8859-1) characters are supported, including:

- French: àâäçéèêëîïôùûüÿœæ
- German: äöüß
- Portuguese: ãõñç
- Italian: àèéìíòóù
- Scandinavian: åæøÅÆØ

### Special Symbols

- Degree symbol: °
- Plus-minus: ±
- Multiply: ×
- Divide: ÷
- Bullet: •
- Trademark: ™ ® ©
- Currency: € £ ¥ $

### Math Symbols

- Greek letters: α β γ δ ε λ μ π σ Ω
- Operators: ≤ ≥ ≠ ≈ ∞ ± − × ÷
- Sets: ∈ ∉ ⊂ ⊃ ∪ ∩

## Code Image Generation (Optional)

NormaDocs can transform code blocks into beautifully styled images for academic documents. This uses the **monokai** theme by default with syntax highlighting.

### Syntax

Add `{code}` after the language identifier to mark a code block for image conversion:

```markdown
```python {code}
def hello():
    print("Hello, World!")
```
```

### Supported Languages

Pygments supports 300+ languages including: `python`, `javascript`, `typescript`, `java`, `c`, `cpp`, `csharp`, `go`, `rust`, `ruby`, `php`, `swift`, `kotlin`, `scala`, `sql`, `html`, `css`, `json`, `yaml`, `xml`, `bash`, `shell`, `markdown`, `latex`, and many more.

### How It Works

1. **Detection**: The preprocessor identifies `{code}` marked blocks
2. **Highlighting**: Pygments generates styled HTML with syntax highlighting
3. **Rendering**: imgkit converts the HTML to a PNG image
4. **Replacement**: The code block is replaced with a markdown image reference
5. **Embedding**: Pandoc embeds the image in the final DOCX

### Installation

```bash
pip install normadocs[codeimage]
```

This installs `pygments>=2.17.0` and `imgkit>=1.0.0`.

> **Note**: imgkit requires `wkhtmltopdf` system library:
> ```bash
> sudo apt install wkhtmltopdf      # Debian/Ubuntu
> sudo dnf install wkhtmltopdf      # Fedora
> brew install wkhtmltopdf          # macOS
> ```

### Example

**Input:**

````markdown
# Results

The implementation follows this pattern:

```python {code}
class DataProcessor:
    def __init__(self, config: dict):
        self.config = config
        self.cache = {}

    def process(self, data: list) -> list:
        return [self.transform(item) for item in data]
```
````

**Output:** A styled PNG image with syntax-highlighted Python code embedded in the DOCX.

### Theme

Code images use the **monokai** theme (dark background with colorful syntax highlighting). This provides excellent contrast and readability for printed documents.

### File Output

Generated images are saved to `./code_images/` directory next to the output DOCX, with names like:
- `code_image_001_python_a1b2c3d4.png`
- `code_image_002_javascript_e5f6g7h8.png`

Images are cached based on content hash, so repeated conversions of the same code don't regenerate the image.

## Preprocessing Features

### Hard-Wrapped Line Joining

The preprocessor joins consecutive lines that were hard-wrapped at approximately 72 characters into single paragraphs. This is transparent to the user.

**Before:**
```markdown
This is a very long paragraph that was originally
wrapped at 72 characters and needs to be joined
back together for proper formatting.
```

**After:**
```markdown
This is a very long paragraph that was originally wrapped at 72 characters and needs to be joined back together for proper formatting.
```

### HTML Entity Encoding

The `#` character in titles is encoded as `&#35;` to prevent Pandoc from interpreting it as a heading marker:

```markdown
Title with # hashtag
```

becomes safe content.

## Markdown Extensions

### OpenXML Blocks

Raw OpenXML can be inserted using the `openxml` output format:

````markdown
```{=openxml}
<w:p>
  <w:r>
    <w:br w:type="page"/>
  </w:r>
</w:p>
```
````

### Attributes on Blocks

Pandoc attributes syntax is supported for images and other elements:

```markdown
![Caption](image.png){width=50%}
```

## Validation

### LanguageTool Integration

NormaDocs can check grammar using LanguageTool:

```bash
# Basic check
normadocs document.md --language-tool

# Strict mode (fail on any error)
normadocs document.md --language-tool --lt-strict

# With Docker (auto-starts container)
normadocs document.md --language-tool --lt-docker

# Save errors to file
normadocs document.md --language-tool --lt-report errors.json
```

## Standards Comparison

| Feature | APA 7th | ICONTEC | IEEE 8th |
|---------|---------|---------|---------|
| Body font | Times New Roman 12pt | Arial 12pt | Times New Roman 10pt |
| Line spacing | Double | 1.5 | Single |
| Top/bottom margins | 1" | 3cm | 1" |
| Left margin | 1" | 3cm | 1" |
| Right margin | 1" | 2cm | 1" |
| Table caption prefix | Table | Tabla | Table |
| Figure caption prefix | Figure | Figura | Fig. |
| Running head | Yes | No | No |
| Abstract page | No | Yes | No |
| Keywords section | Yes | Yes | Yes |
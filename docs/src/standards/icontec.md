# ICONTEC NTC 1486 Standard

Complete reference for the ICONTEC NTC 1486 Colombian academic standard.

## Overview

ICONTEC (Instituto Colombiano de Normas Técnicas y Certificación) is the Colombian organization responsible for technical standards. The NTC 1486 standard defines the formatting rules for academic and technical documents in Colombia.

**NormaDocs** supports ICONTEC NTC 1486 for scientific and research documents.

## Default Configuration

```yaml
name: "ICONTEC (NTC 1486)"
version: "1.0"
citation_style: icontec

fonts:
  body:
    name: "Arial"
    size: 12
  headings:
    name: "Arial"
    level1:
      alignment: center
      bold: true
      uppercase: true

margins:
  unit: cm
  top: 3
  bottom: 2
  left: 3
  right: 2

spacing:
  line: 1.5
  paragraph_before: 0
  paragraph_after: 0

page_setup:
  page_numbers: true
  header: false
  first_page_number: 1

tables:
  borders: full
  caption_prefix: "Tabla"
  caption_above: true

figures:
  caption_prefix: "Figura"
```

## Formatting Rules

### Typography

| Element | Font | Size | Style |
|---------|------|------|-------|
| Body text | Arial | 12pt | Normal |
| Headings | Arial | 12pt | Bold, Uppercase for Level 1 |
| Captions | Arial | 11pt | Normal |

### Spacing

- **Line spacing**: 1.5 throughout the document
- **Paragraph spacing**: No additional space before or after paragraphs
- **Margins**: 3cm (top, bottom, left), 2cm (right)

### Page Layout

- Page numbers appear in the footer, centered
- No header on any page (including first page)
- First page number: 1
- No running head

### Tables

- **Borders**: Full grid borders on all tables
- **Caption position**: Above the table
- **Caption prefix**: "Tabla" (e.g., "Tabla 1. Descripción del sistema")
- **Caption style**: Normal weight, left-aligned caption

### Figures

- **Caption position**: Below the figure
- **Caption prefix**: "Figura" (e.g., "Figura 1. Arquitectura del sistema")
- **Caption style**: Normal weight, left-aligned caption

## Document Structure

### Cover Page

The cover page is generated automatically from YAML frontmatter metadata. The structure includes:

```
[Title - centered, bold, uppercase]
[Subtitle if present]
[Blank line]
[Author Name]
[Author ID / Student Code]
[Program Name]
[Regional Center Name]
[University Name]
[Location (City, Country)]
[Date - Year only]
```

### Required Sections

ICONTEC documents typically follow this structure:

1. **Resumen (Abstract)** - 150-250 words, single paragraph, no indentation
2. **Introducción (Introduction)** - Context and justification (no heading title)
3. **Marco Teórico (Theoretical Framework)**
   - Antecedentes (Background)
   - Planteamiento del Problema (Problem Statement)
4. **Metodología (Methodology)**
   - Diseño de Investigación (Research Design)
   - Población y Muestra (Population and Sample)
   - Instrumentos de Recolección de Datos (Data Collection Instruments)
5. **Resultados (Results)**
6. **Discusión (Discussion)**
7. **Conclusiones (Conclusions)**
8. **Recomendaciones (Recommendations)**
9. **Referencias (References)**
10. **Anexos (Annexes)** - Supplementary materials

### Keywords

Keywords appear after the abstract with the format:

```markdown
**Palabras clave:** word1, word2, word3
```

## YAML Frontmatter Fields

ICONTEC uses these specific frontmatter fields:

```yaml
---
title: "Research Project Title"
subtitle: "Subtitle if applicable"
author: "Author Name"
author_id: "Student Code"
program: "Academic Program Name"
center: "Regional Center Name"
institution: "University Name"
location: "City, Country"
date: 2024
---
```

| Field | Description | Required |
|-------|-------------|----------|
| `title` | Document title | Yes |
| `subtitle` | Optional subtitle | No |
| `author` | Author's full name | Yes |
| `author_id` | Student code or ID | Yes |
| `program` | Academic program name | Yes |
| `center` | Regional center name | Yes |
| `institution` | University name | Yes |
| `location` | City and country | Yes |
| `date` | Year of submission | Yes |

## Reference Format

ICONTEC uses a specific reference format:

### Book

```
Author, A. A., & Author, B. B. (Year). Title of book in italics. Publisher.
```

### Journal Article

```
Author, A. A., & Author, B. B. (Year). Article title. Journal Name, Volume(Number), pages. https://doi.org/xxxxx
```

### Online Resource

```
Author, A. A. (Year). Title of page. Website Name. https://url.com
```

## Comparison with APA 7

| Aspect | APA 7th | ICONTEC NTC 1486 |
|--------|---------|-------------------|
| Body font | Times New Roman 12pt | Arial 12pt |
| Heading font | Times New Roman | Arial |
| Line spacing | Double | 1.5 |
| Top/bottom margins | 1" (2.54cm) | 3cm |
| Left margin | 1" | 3cm |
| Right margin | 1" | 2cm |
| Table caption | Above, "Table X." | Above, "Tabla X." |
| Figure caption | Below, "Figure X." | Below, "Figura X." |
| Running head | Yes (left header) | No |
| Abstract language | English | Spanish |

## CLI Usage

```bash
# Convert Markdown to ICONTEC DOCX
normadocs document.md -s icontec

# Generate ICONTEC PDF
normadocs document.md -s icontec -f all

# With abstract keywords
normadocs document.md -s icontec --language-tool
```
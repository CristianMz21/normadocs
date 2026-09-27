# APA 7th Edition Standard

## Overview

The APA 7th Edition standard in NormaDocs applies automatic formatting and
strict structural validation for academic writing. For a deterministic
person-or-agent workflow, see the [AI agent guide](../ai-agent.md).

## Configuration

### Default Settings

```yaml
name: "APA 7th Edition"
version: "7.0"
citation_style: apa

fonts:
  body:
    name: "Times New Roman"
    size: 12
  headings:
    name: "Times New Roman"
    level1:
      alignment: center
      bold: true
    level2:
      alignment: left
      bold: true
    level3:
      alignment: left
      bold: true
      italic: true

margins:
  unit: inches
  top: 1
  bottom: 1
  left: 1
  right: 1

spacing:
  line: double
  paragraph_before: 0
  paragraph_after: 0

page_setup:
  page_numbers: true
  header: true
  first_page_number: 1

tables:
  borders: horizontal_only
  caption_prefix: "Table"
  caption_above: true
  note_suffix: "Author's elaboration."
  vertical_align: top

figures:
  caption_prefix: "Figure"
  title_above: true
  nota_prefix: "Nota."

running_head:
  enabled: true
  max_length: 50
```

### Student papers

Use `apa7estudiante` for essays, assignments, and other student papers. It is
the CLI default (`--style apa7estudiante`, alias `apa7`):

```bash
normadocs paper.md --format docx
```

This profile keeps the APA 7 student-paper requirements: 1-inch margins,
letter-size pages, double spacing, Times New Roman 12-point text, a centered
bold title page, page number 1 on the cover, page numbers on later pages, and
no optional running-head text (`running_head.enabled: false`). A `short_title`
in the front matter does not enable a running head in this profile. The generic
`apa` profile remains available for professional-style work and can use
`short_title` for a running head.

Allowed font profiles (0.3.0+): Times New Roman 12, Arial 11, Calibri 11,
Georgia 11.

## Strict validation

PDF and `all` conversions run the APA verifier in strict mode by default. A
single detectable violation is reported as an error; the verifier does not
accept a document merely because most paragraphs comply. Strict validation
checks every section's margins and page size, inherited font and spacing
styles, body indentation and alignment, all five heading levels, cover metadata
when supplied, page headers/footers, reference hanging indents and ordering,
and table/figure caption rules.

For the general academic-report profile, the structural validator requires a
cover, a repeated title, Introduction, a development section, Conclusions, and
References in that order. Abstracts and keywords are optional; when included,
the abstract must be at most 250 words and keywords must remain inside its
block. Only appendices may follow References.

Use `--no-verify-apa` only when validation is not applicable. The Python API
also defaults to strict verification; pass `strict=False` to `APAVerifier` only
for a compatibility report that keeps warnings separate from errors.

### Customization

Override defaults by passing a config dictionary to the formatter:

```python
from normadocs.formatters import get_formatter

formatter = get_formatter("apa", "document.docx", config={
    "fonts": {"body": {"name": "Arial", "size": 11}},
    "margins": {"top": 1.5, "bottom": 1.5, "left": 1.25, "right": 1.25}
})
```

---

## Formatting Rules

### Font

- **Body text**: Times New Roman, 12pt (allowed profiles: TNR 12, Arial 11,
  Calibri 11, Georgia 11)
- **Headings**: same family (see Heading Levels below)
- No other fonts are permitted in the main text

### Line Spacing

- **Body text**: Double spacing throughout
- **Tables**: Single spacing within cells
- **References**: Double spacing between entries, single spacing within entries
- **Block quotes**: Double spacing (0.5 inch indent on left)

### Margins

- 1 inch on all sides (top, bottom, left, right)

### Page Numbers

- Position: Top right of every page
- Format: Arabic numerals (1, 2, 3...)
- First page number: 1
- Font: Times New Roman 12pt

### Running Head (professional `apa` profile only)

- **Left header**: Short title in ALL CAPS (maximum 50 characters)
- **Right header**: Page number
- **Cover page**: No running head appears
- **Pages 2+**: Running head visible

The short title is extracted from the `short_title` field in YAML frontmatter metadata. If not provided, the running head is not added. The student profile `apa7estudiante` never renders a running head (`running_head.enabled: false`).

**Configuration**: To disable the running head, set `running_head.enabled: false` in the config:

```yaml
running_head:
  enabled: false
```

---

## Heading Levels (APA 7th Edition)

APA 7th Edition uses five levels of headings:

| Level | Format | Example |
|-------|--------|---------|
| **Level 1** | Centered, Bold, Title Case | `Introduction` |
| **Level 2** | Left-aligned, Bold, Title Case | `Literature Review` |
| **Level 3** | Left-aligned, Bold, Italic, Title Case | *Theoretical Framework* |
| **Level 4** | Indented 0.5in, Bold, Title Case, ends with period | `Sample.` The sample consisted of... |
| **Level 5** | Indented 0.5in, Bold, Italic, Title Case, ends with period | *Procedure.* Data were collected... |

**Note**: APA 7th Edition does not use numbered headings (1, 1.1, 1.1.1). Use only the five levels above.

---

## Cover Page

The cover page includes (centered, in this order):

1. **Title** (bold, centered in upper half of page)
2. **Author name** (centered, after exactly one blank double-spaced line)
3. **Program / department** (centered)
4. **Institution** (centered)
5. **Subject + code** (centered, e.g. `Análisis y Diseño de Sistemas (ADSO-2026)`)
6. **Instructor name** (centered, no prefix)
7. **Date** (centered)

No blank lines between items 2–7. The verifier warns (never rewrites) when the
title is not in Title Case.

### Example Frontmatter (YAML)

```yaml
---
title: "The Effects of Machine Learning on Higher Education Outcomes"
author: "Sarah M. Johnson"
program: "Computer Science"
institution: "State University"
subject: "Research Methods"
subject_code: "RES-2026"
instructor: "Dr. Smith"
date: "2026-04-10"
---
```

---

## Abstract

- Starts on page 2 in its own page (after cover page); when the document has
  no abstract, the body opens page 2 with the repeated title instead
- Heading "Resumen"/"Abstract" centered, bold
- Maximum 250 words (student papers) / 150 words (professional journals)
- Single block, no first-line indent
- Keywords stay inside the block (`Palabras clave:` / `Keywords:`)
- When an abstract exists and the title heading precedes it, NormaDocs moves
  the repeated title to open the body so the title never sits alone on page 2

### Keywords

- Label "Keywords:" in italics
- Keywords in regular text, left-indented 0.5 inches
- Separated by commas

Example:
```
Keywords: machine learning, higher education, adaptive learning, educational technology
```

---

## Page and line breaks

The whole document is double-spaced and continuous. NormaDocs enforces:

- **Cover**: exactly one blank double-spaced line between title and author;
  all other cover items on consecutive lines.
- **Page breaks**: only before the repeated title opening the body, before
  Referencias/References, and before each appendix. Internal sections
  (Marco teórico, Metodología, Resultados…) never open a new page.
- **Line breaks**: none extra — no blank lines between paragraphs, around
  headings, between table label/title/table/`Nota.`, or between list items.
  Ordered-list numbers share the line with their text (0.5-inch hanging).
- A dedicated `blank_lines` verifier check fails documents that break these
  rules (error in strict mode).

## Body Text

### First-Line Indent

- 0.5 inch first-line indent on all paragraphs
- **Exception**: First paragraph after a heading has NO indent

### Alignment

- Left-aligned (default)
- Do not justify text

### Paragraph Spacing

- Double spacing throughout
- No additional space before or after paragraphs

---

## References

- Start on new page after body
- Heading "References" centered, bold
- Alphabetical order by author's last name
- Hanging indent: 0.5 inch (first line flush left, subsequent lines indented)
- Double spacing between entries, single spacing within entries
- No heading styles within references section

### Example Entry

```
Smith, A. B., & Jones, C. D. (2024). Title of the article. Journal Name, 45(2), 112-130. https://doi.org/10.0000/journal.2024.0001
```

---

## Tables

### Caption Format

- "Tabla 1"/"Table 1" in bold, followed by title in italics on the next line
- Caption appears ABOVE the table
- Table number increments sequentially
- The student profile uses Spanish labels (`Tabla`, `Elaboración propia`)

Example:
```
Table 1
*Student Performance Metrics by Intervention Type*
```

### Formatting

- Centered on page
- Horizontal borders only (no vertical lines)
- Header row in bold
- Single spacing within cells
- Notes below table in italics, starting with "Nota."

### Note Example

```
Nota. Effect sizes represent Cohen's d values. CI = confidence interval.
```

---

## Figures

### Caption Format

- Caption appears BELOW the figure
- "Figure N" in bold, followed by title in italics
- Notes in italics, starting with "Nota."

Example:
```
Figure 1
*Student Engagement Trends Over Academic Year*

Nota. Data collected from Fall 2024 cohort (n = 245).
```

### Formatting

- Centered on page
- Image scaled to fit page width (max 6.5 inches)
- High resolution recommended

---

## Block Quotes

Quotes over 40 words are formatted automatically as a freestanding block:

- Indented 0.5 inch on the left, no first-line indent
- Double spaced (same as body text)
- No quotation marks; period before the parenthetical citation
- No blank lines before or after beyond standard double spacing

Example:
```
Smith (2024) explained this phenomenon:

    The implementation of adaptive learning systems requires
    significant institutional investment in both technology
    and faculty development.

(Smith, 2024, p. 45)
```

---

## Implemented Features

The following APA 7th Edition features are implemented in NormaDocs:

- Cover page with 7-field title block and Title Case warning
- 1-inch margins on all sides
- Allowed font profiles (TNR 12, Arial 11, Calibri 11, Georgia 11)
- Double line spacing, continuous body text
- Page numbers (top right)
- Running head in the professional `apa` profile only (short title left)
- Heading styles (5 levels)
- First-line indent (0.5 inch) for body paragraphs
- Abstract/Keywords block on its own page
- Ordered lists keep native numbering; no blank lines between items
- Table captions ("Tabla 1"/"Table 1" + italic title)
- Table formatting (horizontal borders only, header repeats on split)
- Table notes ("Nota.")
- Figure captions ("Figura 1"/"Figure 1")
- Hanging indent for references; journal-vs-book italics
- `blank_lines` check: no stray blank lines in the body
- Bidirectional citation↔reference cross-checks
- Foreign word italics (e.g., ad hoc, in vitro)
- Page breaks only before the body title, References, and appendices

---

## Missing Features

The following APA 7th Edition features are NOT yet implemented:

- Author notes (footnotes on cover page)
- DOI formatting in references

---

## Example Document

A complete example APA 7th Edition student document is available at `examples/informe_apa7_ejemplo.md` (also `examples/example_apa.md` for the professional profile).

### Example Usage

```bash
# Convert APA document
normadocs examples/example_apa.md -s apa7estudiante -o ./output

# With PDF output and strict validation
normadocs examples/example_apa.md -s apa7estudiante -f all -o ./output
```

### Python Library Usage

```python
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter

# Process markdown
processor = MarkdownPreprocessor()
clean_md, meta = processor.process(input_markdown)

# Convert to DOCX
PandocRunner().run(clean_md, "output.docx")

# Apply APA formatting
formatter = get_formatter("apa", "output.docx")
formatter.process(meta)
formatter.save("output_apa.docx")
```

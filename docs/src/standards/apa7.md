# APA 7th Edition Standard

## Overview

The APA 7th Edition standard in NormaDocs applies automatic formatting to produce documents that comply with the American Psychological Association's 7th Edition guidelines for academic writing.

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

- **Body text**: Times New Roman, 12pt
- **Headings**: Times New Roman (see Heading Levels below)
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

### Running Head

- **Left header**: Short title in ALL CAPS (maximum 50 characters)
- **Right header**: Page number
- **Cover page**: No running head appears
- **Pages 2+**: Running head visible

The short title is extracted from the `short_title` field in YAML frontmatter metadata. If not provided, the running head is not added.

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
2. **Author name** (centered)
3. **Institutional affiliation** (centered)
4. **Course number** (if applicable)
5. **Instructor name** (if applicable)
6. **Date** (centered)

### Example Frontmatter (YAML)

```yaml
---
title: "The Effects of Machine Learning on Higher Education Outcomes"
short_title: "Machine Learning Effects on Education"
author: "Sarah M. Johnson"
affiliation: "Department of Computer Science, State University"
institution: "State University"
date: "2026-04-10"
---
```

---

## Abstract

- Starts on page 2 (after cover page)
- Heading "Abstract" centered, bold
- Maximum 250 words (student papers) / 150 words (professional journals)
- No paragraph indent
- Keywords section follows immediately after abstract

### Keywords

- Label "Keywords:" in italics
- Keywords in regular text, left-indented 0.5 inches
- Separated by commas

Example:
```
Keywords: machine learning, higher education, adaptive learning, educational technology
```

---

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

- "Table N" in bold, followed by title in italics
- Caption appears ABOVE the table
- Table number increments sequentially

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

- Indented 0.5 inch on left
- Double spaced (same as body text)
- No quotation marks
- Attribution on new line below quote

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

- Cover page with title, author, institutional affiliation
- 1-inch margins on all sides
- Times New Roman 12pt font
- Double line spacing
- Page numbers (top right)
- Running head (short title left, page number right)
- Heading styles (5 levels)
- First-line indent (0.5 inch) for body paragraphs
- Abstract/Keywords formatting
- Table captions ("Table N")
- Table formatting (horizontal borders only)
- Table notes ("Nota.")
- Figure captions ("Figure N")
- Hanging indent for references
- Foreign word italics (e.g., ad hoc, in vitro)
- Page breaks before Conclusions and References sections

---

## Missing Features

The following APA 7th Edition features are NOT yet implemented:

- Author notes (footnotes on cover page)
- DOI formatting in references
- Appendices formatting
- Block quote formatting (indentation)
- Seriation within text (APA bulleted lists)
- Secondary temporal derivatives (e.g., "running heads are right-aligned" not implemented)

---

## Example Document

A complete example APA 7th Edition document is available at `examples/example_apa.md`.

### Example Usage

```bash
# Convert APA document
normadocs examples/example_apa.md -s apa -o ./output

# With PDF output
normadocs examples/example_apa.md -s apa -f all -o ./output
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

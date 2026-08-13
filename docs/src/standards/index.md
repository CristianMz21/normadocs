# Supported Standards

NormaDocs supports multiple academic formatting standards.

## APA 7th Edition

American Psychological Association format, commonly used in social sciences.

**Features:**
- Times New Roman 12pt
- Double line spacing (2.0)
- 1-inch (2.54cm) margins all sides
- Strict structural validation for academic reports
- Student cover page with page number and no running-head text by default
- Optional professional running head when using the generic `apa` profile
- Cover page, abstract and keywords support
- 5 heading levels with specific formatting
- First-line indent in body paragraphs
- Block quotes require manual review in the current formatter
- Tables with horizontal borders only
- Figures with label + title above, nota below

**Configuration:** `apa7.yaml`

For student assignments, use the dedicated `apa7estudiante` profile. It keeps
page numbers on every page and omits optional running-head text. This is the
CLI default. The generic `apa` profile remains available for professional-style
work and can use `short_title` for a running head.

**Student configuration:** `apa7estudiante.yaml`

**Example Document:** `examples/example_apa.md`

[See APA Configuration →](apa7.md)

## ICONTEC (NTC 1486)

NormaDocs provides automated formatting for ICONTEC. The project does not yet
ship a strict ICONTEC verifier, so inspect the generated DOCX/PDF against your
institution's NTC 1486 checklist before delivery.

Colombian technical and academic standard.

**Features:**
- Arial 12pt
- 1.5 line spacing
- 3cm margins (top, bottom, left), 4cm (right)
- Cover page with specific structure

**Configuration:** `icontec.yaml`

[See ICONTEC Configuration →](icontec.md)

## IEEE 8th Edition

NormaDocs provides automated IEEE formatting. Two-column final-paper layout
and a strict IEEE verifier are not currently implemented; manual review remains
required for those rules.

Institute of Electrical and Electronics Engineers format.

**Features:**
- Times New Roman 10pt
- Single line spacing
- 1-inch margins
- Page numbers in headers

**Configuration:** `ieee.yaml`

[See IEEE Configuration →](ieee.md)
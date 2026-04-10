# APA 7th Edition Configuration

## Default Configuration

The APA 7th Edition standard uses these default settings:

```yaml
fonts:
  body:
    name: "Times New Roman"
    size: 12
  headings:
    name: "Times New Roman"
    level1:
      size: 24
      bold: true
      alignment: "center"
    level2:
      size: 20
      bold: true
margins:
  unit: inches
  top: 1.0
  bottom: 1.0
  left: 1.0
  right: 1.0
spacing:
  line: double
tables:
  caption_prefix: "Tabla"
  caption_above: true
figures:
  caption_prefix: "Figura"
```

## Customization

Override defaults by passing a config dictionary:

```python
formatter = get_formatter("apa", "doc.docx", config={
    "fonts": {"body": {"name": "Arial"}}
})
```

## Formatting Rules

- Font: Times New Roman 12pt throughout
- Line spacing: Double throughout
- Margins: 1 inch on all sides
- Running head: Short title in uppercase header
- Page numbers: Top right header

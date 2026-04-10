# Library Usage

You can use NormaDocs programmatically in your Python applications.

## Basic Usage

```python
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter

# 1. Preprocess Markdown
processor = MarkdownPreprocessor()
md_content = open("document.md").read()
clean_md, meta = processor.process(md_content)

# 2. Convert to DOCX
runner = PandocRunner()
runner.run(clean_md, "output.docx")

# 3. Format with APA style
formatter = get_formatter("apa", "output.docx")
formatter.process(meta)
formatter.save("output_final.docx")
```

## With Bibliography

```python
runner.run(clean_md, "output.docx", bibliography="refs.bib", csl="apa.csl")
```

## Custom Configuration

```python
custom_config = {
    "fonts": {"body": {"name": "Arial", "size": 12}},
    "margins": {"top": 1.5, "bottom": 1.5}
}
formatter = get_formatter("apa", "doc.docx", config=custom_config)
```

## Available Standards

| Standard | String |
|----------|--------|
| APA 7th Edition | `"apa"` |
| ICONTEC NTC 1486 | `"icontec"` |
| IEEE 8th Edition | `"ieee"` |

## API Reference

See the source code docstrings for complete API documentation.

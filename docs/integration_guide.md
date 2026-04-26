# Web Framework Integration Guide

**NormaDocs** can be easily integrated into web applications such as **Django**, **FastAPI**, or **Flask** to generate academic documents on-demand.

## Installation

```bash
pip install normadocs

# With PDF support (WeasyPrint)
pip install normadocs[pdf]
```

> **Server requirement**: Pandoc must be installed on the system.
>
> ```bash
> sudo apt install pandoc              # Debian/Ubuntu
> sudo dnf install pandoc              # Fedora
> brew install pandoc                  # macOS
> ```

## Basic API

```python
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter
from normadocs.pdf_generator import PDFGenerator

# 1. Pre-process Markdown → extract metadata + cover page
processor = MarkdownPreprocessor()
clean_md, meta = processor.process(raw_markdown)

# 2. Convert to DOCX with Pandoc
runner = PandocRunner()
runner.run(clean_md, "output.docx")

# 3. Apply academic format (APA, ICONTEC)
formatter = get_formatter("apa", "output.docx")
formatter.process(meta)
formatter.save("output.docx")

# 4. (Optional) Generate PDF
PDFGenerator.convert("output.docx", "/tmp/output/", clean_md, "output.pdf")
```

### Available Styles

| Style           | Value       | Description                                      |
| --------------- | ----------- | ------------------------------------------------ |
| APA 7th Edition | `"apa"`     | Times New Roman 12pt, double spacing, 1" margins |
| ICONTEC NTC 1486 | `"icontec"` | Arial 12pt, 1.5 spacing, 3/2 cm margins        |
| IEEE 8th Edition | `"ieee"`    | Times New Roman 10pt, single spacing, 1" margins |

### Optional Pandoc Parameters

```python
# With BibTeX bibliography and CSL style
runner.run(
    clean_md,
    "output.docx",
    bibliography="references.bib",
    csl="apa.csl",
)
```

## Example: Django View

```python
import tempfile
from pathlib import Path

from django.http import FileResponse, HttpResponseServerError

from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter


def export_document(request, document_id):
    """Generate a formatted DOCX from a Markdown document."""
    doc = Document.objects.get(id=document_id)
    style = request.GET.get("style", "apa")  # ?style=icontec

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / f"doc_{document_id}.docx"

        # 1. Pre-process
        processor = MarkdownPreprocessor()
        clean_md, meta = processor.process(doc.markdown_content)

        # 2. Convert with Pandoc
        runner = PandocRunner()
        if not runner.run(clean_md, str(output_path)):
            return HttpResponseServerError("Pandoc error")

        # 3. Apply format
        formatter = get_formatter(style, str(output_path))
        formatter.process(meta)
        formatter.save(str(output_path))

        # 4. Return file
        response = FileResponse(
            open(output_path, "rb"),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = f'attachment; filename="{meta.title}.docx"'
        return response
```

## Example: FastAPI Endpoint

```python
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter

app = FastAPI()


class ConvertRequest(BaseModel):
    markdown: str
    style: str = "apa"


@app.post("/convert")
async def convert_document(req: ConvertRequest):
    """Convert Markdown to a formatted DOCX file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.docx"

        # Pipeline
        processor = MarkdownPreprocessor()
        clean_md, meta = processor.process(req.markdown)

        runner = PandocRunner()
        if not runner.run(clean_md, str(output_path)):
            raise HTTPException(status_code=500, detail="Pandoc conversion failed")

        formatter = get_formatter(req.style, str(output_path))
        formatter.process(meta)
        formatter.save(str(output_path))

        return FileResponse(
            path=str(output_path),
            filename=f"{meta.title}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
```

## Example: Flask

```python
import tempfile
from pathlib import Path

from flask import Flask, request, send_file

from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter

app = Flask(__name__)


@app.route("/convert", methods=["POST"])
def convert():
    """Convert Markdown to formatted DOCX."""
    md_content = request.json.get("markdown", "")
    style = request.json.get("style", "apa")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.docx"

        processor = MarkdownPreprocessor()
        clean_md, meta = processor.process(md_content)

        runner = PandocRunner()
        if not runner.run(clean_md, str(output_path)):
            return {"error": "Pandoc conversion failed"}, 500

        formatter = get_formatter(style, str(output_path))
        formatter.process(meta)
        formatter.save(str(output_path))

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{meta.title}.docx",
        )
```

## Deployment Considerations

| Requirement       | Details                                                                  |
| ---------------- | ------------------------------------------------------------------------ |
| **Pandoc**       | Server must have `pandoc` installed in PATH                               |
| **Fonts**        | For PDF: install `ttf-mscorefonts-installer` (Times New Roman) on Linux |
| **LibreOffice**  | `sudo apt install libreoffice` (preferred option for PDF)                |
| **WeasyPrint**   | Alternative for PDF: `pip install normadocs[pdf]`                        |
| **Storage**      | Use `tempfile.TemporaryDirectory()` for transient files                  |
| **Concurrency**  | Each request should use its own temporary directory                       |

## Docker

If deploying with Docker, include Pandoc in the image:

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y pandoc && rm -rf /var/lib/apt/lists/*
RUN pip install normadocs[pdf]

# ... your application
```
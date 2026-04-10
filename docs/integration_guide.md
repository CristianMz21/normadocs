# Guía de Integración con Frameworks Web

**NormaDocs** puede integrarse fácilmente en aplicaciones web como **Django**, **FastAPI** o **Flask** para generar documentos académicos on-demand.

## Instalación

```bash
pip install normadocs

# Con soporte PDF (WeasyPrint)
pip install normadocs[pdf]
```

> **Requisito del servidor**: Pandoc debe estar instalado en el sistema.
>
> ```bash
> sudo apt install pandoc              # Debian/Ubuntu
> sudo dnf install pandoc              # Fedora
> brew install pandoc                  # macOS
> ```

## API Básica

```python
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter
from normadocs.pdf_generator import PDFGenerator

# 1. Pre-procesar Markdown → extraer metadatos + portada
processor = MarkdownPreprocessor()
clean_md, meta = processor.process(raw_markdown)

# 2. Convertir a DOCX con Pandoc
runner = PandocRunner()
runner.run(clean_md, "output.docx")

# 3. Aplicar formato académico (APA, ICONTEC)
formatter = get_formatter("apa", "output.docx")
formatter.process(meta)
formatter.save("output.docx")

# 4. (Opcional) Generar PDF
PDFGenerator.convert("output.docx", "/tmp/output/", clean_md, "output.pdf")
```

### Estilos disponibles

| Estilo           | Valor       | Descripción                                      |
| ---------------- | ----------- | ------------------------------------------------ |
| APA 7ª Edición   | `"apa"`     | Times New Roman 12pt, doble espacio, márgenes 1" |
| ICONTEC NTC 1486 | `"icontec"` | Arial 12pt, espaciado 1.5, márgenes 3/2 cm       |

### Parámetros opcionales de Pandoc

```python
# Con bibliografía BibTeX y estilo CSL
runner.run(
    clean_md,
    "output.docx",
    bibliography="references.bib",
    csl="apa.csl",
)
```

## Ejemplo: Django View

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

        # 1. Pre-procesar
        processor = MarkdownPreprocessor()
        clean_md, meta = processor.process(doc.markdown_content)

        # 2. Convertir con Pandoc
        runner = PandocRunner()
        if not runner.run(clean_md, str(output_path)):
            return HttpResponseServerError("Error Pandoc")

        # 3. Aplicar formato
        formatter = get_formatter(style, str(output_path))
        formatter.process(meta)
        formatter.save(str(output_path))

        # 4. Devolver archivo
        response = FileResponse(
            open(output_path, "rb"),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = f'attachment; filename="{meta.title}.docx"'
        return response
```

## Ejemplo: FastAPI Endpoint

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

## Ejemplo: Flask

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

## Consideraciones de Despliegue

| Requisito          | Detalle                                                                   |
| ------------------ | ------------------------------------------------------------------------- |
| **Pandoc**         | El servidor debe tener `pandoc` instalado en el `PATH`                    |
| **Fuentes**        | Para PDF: instalar `ttf-mscorefonts-installer` (Times New Roman) en Linux |
| **LibreOffice**    | `sudo apt install libreoffice` (opción preferida para PDF)                |
| **WeasyPrint**     | Alternativa para PDF: `pip install normadocs[pdf]`                        |
| **Almacenamiento** | Usar `tempfile.TemporaryDirectory()` para archivos transitorios           |
| **Concurrencia**   | Cada petición debe usar su propio directorio temporal                     |

## Docker

Si despliega con Docker, asegúrese de incluir Pandoc en la imagen:

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y pandoc && rm -rf /var/lib/apt/lists/*
RUN pip install normadocs[pdf]

# ... su aplicación
```

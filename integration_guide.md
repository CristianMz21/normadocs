# Guía de Integración (Frameworks)

`apa_engine` ha sido diseñado para ser fácilmente integrable en aplicaciones web como Django, FastAPI o Flask.

## Instalación como Librería

Asegúrate de que la carpeta `src` esté en el `PYTHONPATH` de tu aplicación, o instala el paquete via `pip install -e .`.

## Ejemplo: Django View

```python
# views.py
from django.http import FileResponse
from pathlib import Path
from apa_engine.preprocessor import MarkdownPreprocessor
from apa_engine.pandoc_client import PandocRunner
from apa_engine.docx_formatter import APADocxFormatter

def export_apa(request, document_id):
    # 1. Obtener contenido Markdown de tu modelo
    doc = DocumentModel.objects.get(id=document_id)
    raw_md = doc.content

    # 2. Definir rutas temporales
    output_dir = Path("/tmp/apa_exports")
    output_dir.mkdir(exist_ok=True)
    temp_docx = output_dir / f"doc_{document_id}.docx"

    # 3. Pipeline de Conversión
    # A) Pre-proceso
    processor = MarkdownPreprocessor()
    processed_md, meta = processor.process(raw_md)

    # B) Pandoc
    runner = PandocRunner()
    if not runner.run(processed_md, str(temp_docx)):
        return HttpResponseServerError("Error en conversión Pandoc")

    # C) Formato APA
    formatter = APADocxFormatter(str(temp_docx))
    formatter.process(meta)
    formatter.save(str(temp_docx))

    # 4. Servir archivo
    return FileResponse(open(temp_docx, 'rb'), filename=f"{meta.title}.docx")
```

## Ejemplo: FastAPI Background Task

```python
from fastapi import FastAPI, BackgroundTasks
from apa_engine.cli import convert_logic # O importar clases individuales

app = FastAPI()

def process_document(md_content: str, user_email: str):
    # Lógica de conversión...
    pass

@app.post("/convert")
async def convert_document(md_content: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_document, md_content, "user@example.com")
    return {"message": "Conversion started"}
```

## Consideraciones de Despliegue

- **Pandoc**: El servidor debe tener `pandoc` instalado.
- **Fuentes**: Para que el PDF se genere correctamente con las fuentes adecuadas, el servidor debe tener instaladas las fuentes (ej. `ttf-mscorefonts-installer` para Times New Roman en Linux).

# NormaDocs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**NormaDocs** es una herramienta profesional de código abierto diseñada para convertir documentos Markdown a formatos académicos estándar (DOCX, PDF), comenzando con soporte estricto para **APA 7ª Edición**.

Su arquitectura modular permite la integración futura de otras normas como **ICONTEC**, **IEEE** y más.

## Características ✨

- **Automatización Total**: Convierte Markdown simple en documentos listos para entregar.
- **Multiformato**: Salida en DOCX y PDF.
- **Cumplimiento APA 7**:
  - Portada automática.
  - Formato Times New Roman 12pt, Doble espacio.
  - Citas y referencias formateadas.
- **Modular**: Úsalo como CLI (`normadocs`) o como librería Python (`normadocs`).

## Instalación 📦

### Requisitos Previos

- Python 3.12+
- [Pandoc](https://pandoc.org/installing.html)
- LibreOffice (Opcional, para PDF)

### Desde el repositorio

```bash
git clone https://github.com/mackroph/normadocs.git
cd normadocs
make install
```

## Uso 🚀

### Línea de Comandos (CLI)

El comando principal es `normadocs`:

```bash
# Ayuda
normadocs --help

# Conversión básica
normadocs IDocs/paper.md

# Conversión a PDF y DOCX en carpeta específica
normadocs IDocs/paper.md -o ./ExportDocs --format pdf
```

### Como Librería (Python)

```python
from pathlib import Path
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.docx_formatter import APADocxFormatter
from normadocs.pandoc_client import PandocRunner

# 1. Pre-procesar
md_text = Path("paper.md").read_text()
processor = MarkdownPreprocessor()
clean_md, meta = processor.process(md_text)

# 2. Convertir
PandocRunner().run(clean_md, "output.docx")

# 3. Aplicar Normas
formatter = APADocxFormatter("output.docx")
formatter.process(meta)
formatter.save("output_final.docx")
```

## Desarrollo 🛠️

```bash
make install  # Instalar dependencias
make test     # Correr tests
make lint     # Verificar calidad
make build    # Crear paquete
```

## Licencia 📄

Este proyecto está bajo la Licencia MIT.

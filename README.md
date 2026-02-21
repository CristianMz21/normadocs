# NormaDocs

[![PyPI](https://img.shields.io/pypi/v/normadocs.svg)](https://pypi.org/project/normadocs/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![CI](https://github.com/CristianMz21/normadocs/actions/workflows/ci.yml/badge.svg)](https://github.com/CristianMz21/normadocs/actions/workflows/ci.yml)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Typed](https://img.shields.io/badge/typed-PEP%20561-brightgreen)](https://peps.python.org/pep-0561/)

**NormaDocs** es una herramienta profesional de código abierto que convierte documentos Markdown a formatos académicos estándar (**DOCX**, **PDF**), con soporte para múltiples normas de citación.

## Normas Soportadas

| Norma                  | Estado          | Fuente               | Espacio    |
| ---------------------- | --------------- | -------------------- | ---------- |
| **APA 7ª Edición**     | ✅ Completo     | Times New Roman 12pt | Doble      |
| **ICONTEC (NTC 1486)** | ✅ Completo     | Arial 12pt           | 1.5 líneas |
| IEEE                   | 🔜 Próximamente | —                    | —          |

## Características ✨

- **Portada automática**: Genera título, autor, institución, programa, fecha.
- **Formato completo**: Márgenes, tipografía, espaciado según la norma seleccionada.
- **Tabla de contenido**: Detecta secciones `# Heading` y las formatea.
- **Tablas APA**: Bordes horizontales, sin líneas verticales, caption con _Tabla X_.
- **Bibliografía**: Soporte para archivos `.bib` (BibTeX) y estilos CSL vía Pandoc.
- **Salida múltiple**: DOCX siempre, PDF opcional (LibreOffice o WeasyPrint).
- **Uso dual**: CLI (`normadocs`) o librería Python importable.
- **Tipado**: Paquete PEP 561 con `py.typed` marker.
- **Quality gates**: CI bloquea publicación si lint, tests o seguridad fallan.

## Instalación 📦

### Requisitos previos

- **Python** 3.10 o superior
- **[Pandoc](https://pandoc.org/installing.html)** (requerido para la conversión)

### Desde PyPI

```bash
pip install normadocs
```

#### Extras opcionales

```bash
# Para generación de PDF con WeasyPrint
pip install normadocs[pdf]

# Para desarrollo (linting, tests, seguridad)
pip install normadocs[dev]
```

### Desde el repositorio

```bash
git clone https://github.com/CristianMz21/normadocs.git
cd normadocs
make install    # pip install -e ".[dev]"
```

### Dependencia del sistema (PDF)

Para generar PDFs se necesita **uno** de estos:

- **LibreOffice** (recomendado): `sudo apt install libreoffice`
- **WeasyPrint**: `pip install normadocs[pdf]`

## Uso 🚀

### CLI (Línea de Comandos)

```bash
# Ayuda completa
normadocs --help

# Conversión básica (APA por defecto)
normadocs mi_documento.md

# Especificar norma ICONTEC
normadocs mi_documento.md --style icontec

# Con bibliografía BibTeX + estilo CSL personalizado
normadocs mi_documento.md --bibliography refs.bib --csl apa.csl

# Generar PDF además de DOCX
normadocs mi_documento.md --format pdf

# Directorio de salida personalizado
normadocs mi_documento.md -o ./Entregas -s apa -f all
```

### Como librería Python

```python
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.pandoc_client import PandocRunner
from normadocs.formatters import get_formatter

# 1. Pre-procesar Markdown
md_text = open("paper.md").read()
processor = MarkdownPreprocessor()
clean_md, meta = processor.process(md_text)

# 2. Convertir a DOCX con Pandoc
PandocRunner().run(clean_md, "output.docx")

# 3. Aplicar formato académico
formatter = get_formatter("apa", "output.docx")  # o "icontec"
formatter.process(meta)
formatter.save("output_final.docx")
```

### Formato del Markdown de entrada

NormaDocs extrae los metadatos de las primeras líneas del archivo:

```markdown
**Título del Documento**

Nombre del Autor
Nombre del Programa
Número de Ficha
Nombre de la Institución
Nombre del Centro
Fecha

# Resumen

Texto del resumen...

**Palabras clave:** palabra1, palabra2, palabra3

# Introducción

Contenido del documento...

# Referencias

Autor, A. A. (2024). Título. _Revista_, 1(2), 3-4.
```

> **Nota**: Las primeras 2 líneas se usan como título. Las líneas 3-13 se mapean
> a los campos: `author`, `program`, `ficha`, `institution`, `center`, `date`.

## Desarrollo 🛠️

```bash
make install     # Instalar en modo editable con deps de desarrollo
make lint        # Ruff check + Ruff format check + MyPy
make test        # Ejecutar tests con pytest
make test-cov    # Tests con reporte de cobertura (mínimo 60%)
make security    # Escaneo de seguridad con Bandit
make check       # Todo: lint + test-cov + security
make build       # Construir paquete wheel + sdist
```

### Estructura del proyecto

```
APAScript/
├── src/normadocs/
│   ├── __init__.py           # Versión del paquete
│   ├── cli.py                # Interfaz de línea de comandos (Typer)
│   ├── config.py             # Constantes (márgenes, campos de metadatos)
│   ├── models.py             # DocumentMetadata, ProcessOptions
│   ├── pandoc_client.py      # Wrapper de Pandoc (MD → DOCX)
│   ├── pdf_generator.py      # LibreOffice / WeasyPrint fallback
│   ├── preprocessor.py       # Extracción de metadatos, portada, page breaks
│   ├── py.typed              # PEP 561 marker
│   └── formatters/
│       ├── __init__.py       # Factory: get_formatter()
│       ├── base.py           # DocumentFormatter (ABC)
│       ├── apa.py            # APA 7ª Edición
│       └── icontec.py        # ICONTEC NTC 1486
├── tests/
│   ├── test_cli.py           # Tests unitarios del CLI
│   ├── test_e2e.py           # Tests end-to-end (25 tests)
│   ├── test_integration.py   # Tests de integración del pipeline
│   ├── test_models.py        # Tests de DocumentMetadata
│   ├── test_pandoc_client.py # Tests del cliente Pandoc
│   ├── test_pdf_generator.py # Tests del generador PDF
│   └── test_preprocessor.py  # Tests del preprocesador
├── .github/workflows/
│   ├── ci.yml                # CI: lint, security, tests, build
│   ├── release.yml           # Publicación a PyPI (requiere CI ✅)
│   └── docker-publish.yml    # Docker image (requiere CI ✅)
├── pyproject.toml            # Configuración del proyecto y herramientas
├── Makefile                  # Comandos de desarrollo
├── CHANGELOG.md              # Historial de cambios
├── CONTRIBUTING.md           # Guía de contribución
└── example.md                # Documento Markdown de ejemplo
```

## CI/CD 🔄

La publicación a **PyPI** y **Docker Hub** está bloqueada si cualquiera de estas comprobaciones falla:

```
Ruff Lint → MyPy → Bandit → Tests (3.10/3.11/3.12 + cobertura) → Build
```

| Pipeline             | Acción                                     |
| -------------------- | ------------------------------------------ |
| `ci.yml`             | Lint + tipos + seguridad + tests + build   |
| `release.yml`        | Publicar a PyPI **solo si CI pasa**        |
| `docker-publish.yml` | Publicar imagen Docker **solo si CI pasa** |

## Licencia 📄

Este proyecto está bajo la **Licencia MIT**. Ver [LICENSE](LICENSE) para más detalles.

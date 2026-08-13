# NormaDocs para agentes de IA

Esta guía define el contrato mínimo para que una persona o un agente de IA use
NormaDocs sin inventar metadatos, confundir estándares ni declarar cumplimiento
sin verificar el resultado.

## Resultado esperado

Un agente debe entregar:

1. El archivo fuente Markdown conservado.
2. El DOCX generado en una ruta explícita.
3. El PDF solo cuando se solicite y exista LibreOffice o WeasyPrint.
4. El reporte de validación cuando se genere PDF con APA.
5. Un resumen honesto de errores, advertencias y herramientas usadas.

> NormaDocs automatiza el formato, pero no puede comprobar que el contenido
> académico sea verdadero, que las fuentes existan o que las reglas de una
> universidad sean idénticas a APA 7. Las instrucciones institucionales tienen
> prioridad sobre este perfil genérico.

## Flujo determinista

```text
1. Identificar estándar y tipo de trabajo
2. Confirmar metadatos; no rellenar datos desconocidos
3. Crear Markdown UTF-8 con frontmatter YAML
4. Convertir con el perfil correcto
5. Validar el PDF si el estándar es APA y se pidió PDF
6. Leer el reporte y corregir el Markdown, no el DOCX generado
7. Repetir hasta obtener PASSED o reportar los errores restantes
```

## Elegir el estándar

| Necesidad | Perfil | Regla principal |
|---|---|---|
| Trabajo estudiantil APA 7 | `apa7estudiante` | Perfil predeterminado; portada estudiantil, número de página y sin running head |
| APA genérico/profesional | `apa` | Puede usar `short_title` para running head |
| Trabajo académico colombiano | `icontec` | NTC 1486; no debe validarse con el verificador APA |
| Trabajo técnico IEEE | `ieee` | IEEE 8th; no debe validarse con el verificador APA |

Si el usuario no indica el estándar, preguntar antes de convertir. Si indica
APA pero no distingue estudiante/profesional, usar `apa7estudiante` y avisarlo.

## Contrato de entrada APA

Usar frontmatter YAML para que el resultado sea reproducible. No inventar
`author`, `institution`, `date`, `instructor` ni otros datos: pedirlos o dejar
claro que faltan.

```markdown
---
title: "Efectos del aprendizaje automático en la educación superior"
author: "Nombre completo"
affiliation: "Departamento o programa académico"
institution: "Universidad o institución"
program: "Programa académico"
instructor: "Nombre del docente"
subject: "Nombre y código del curso"
date: "2026-08-13"
short_title: "MACHINE LEARNING EFFECTS"
---

# Resumen

Resumen opcional de hasta 250 palabras.

**Palabras clave:** aprendizaje automático, educación, tecnología

# Introducción

Presenta el problema, el contexto y el objetivo del informe.

# Desarrollo

Expone el análisis, la metodología, los resultados o los argumentos.

# Conclusiones

Resume las conclusiones que se desprenden del desarrollo.

# Referencias

Autor, A. A. (2026). Título de la obra. Editorial.
```

### Estructura APA académica estricta

El validador de informes académicos generales exige, en este orden:

- Portada con título, autor y una línea adicional de identificación.
- Título repetido como primer encabezado de nivel 1 del contenido.
- `Introducción` / `Introduction`.
- Una sección de desarrollo (`Desarrollo`, `Métodos`, `Resultados`, `Discusión`,
  `Análisis`, `Marco teórico` y equivalentes en inglés).
- `Conclusiones` / `Conclusion`.
- `Referencias` / `References`.

`Resumen`/`Abstract`, palabras clave y apéndices son opcionales. Si aparece un
resumen, debe tener como máximo 250 palabras. Las palabras clave deben estar
dentro del bloque del resumen. Solo los apéndices pueden seguir a Referencias.

## Comandos recomendados

### APA DOCX

```bash
normadocs informe.md \
  --style apa7estudiante \
  --format docx \
  --output-dir ExportDocs
```

### APA DOCX + PDF + reporte

```bash
normadocs informe.md \
  --style apa7estudiante \
  --format all \
  --output-dir ExportDocs \
  --apa-report ExportDocs/informe_apa.md
```

La validación APA estricta está activa por defecto para `pdf` y `all`. Si falla,
el comando termina con código distinto de cero. `--no-verify-apa` desactiva la
validación posterior; úsalo solo si el PDF no es una entrega APA.

### ICONTEC e IEEE

```bash
normadocs informe.md --style icontec --format all --output-dir ExportDocs
normadocs informe.md --style ieee --format docx --output-dir ExportDocs
```

Estos perfiles no deben recibir un reporte APA. Las reglas específicas están
en [ICONTEC](standards/icontec.md) y [IEEE](standards/ieee.md).

## Contrato de salida

El nombre se forma con el nombre del Markdown y el estilo en mayúsculas:

```text
ExportDocs/informe_APA7ESTUDIANTE.docx
ExportDocs/informe_APA7ESTUDIANTE.pdf
```

Comprueba que los archivos existen y tienen tamaño mayor que cero. No edites el
DOCX para corregir errores: modifica el Markdown o sus metadatos y vuelve a
convertirlo.

## Interpretar la validación APA

El reporte contiene `PASSED` o `FAILED`, puntuación e incidencias agrupadas por
categoría. En modo estricto, cualquier advertencia se trata como error.

| Categoría | Qué comprobar primero |
|---|---|
| `structure` | Portada, secciones obligatorias, orden y contenido |
| `cover_page` | Título, autor, afiliación, fecha y repetición del título |
| `margins`, `page_setup` | Carta, márgenes de 1", encabezados y pies |
| `fonts`, `spacing`, `paragraphs` | Fuente, tamaño, doble espacio, alineación y sangrías |
| `headings` | Niveles APA 1–5 y jerarquía |
| `references` | Referencias, orden alfabético y sangría francesa |
| `tables`, `figures` | Etiquetas, títulos, posición y bordes |

Un agente debe copiar el `check`, `expected`, `actual` y `evidence` del reporte
en su respuesta; no ocultar fallos ni convertirlos en afirmaciones de
cumplimiento.

## Uso desde Python

```python
from pathlib import Path

from normadocs.formatters import get_formatter
from normadocs.pandoc_client import PandocRunner
from normadocs.pdf_generator import PDFGenerator
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.verifier.apa_verifier import APAVerifier

source = Path("informe.md")
output = Path("ExportDocs/informe_APA7ESTUDIANTE.docx")
pdf = output.with_suffix(".pdf")

clean_markdown = source.read_text(encoding="utf-8")
# El preprocesador es la fuente correcta de metadata y Markdown limpio.
clean_markdown, metadata = MarkdownPreprocessor().process(clean_markdown)
if not PandocRunner().run(clean_markdown, str(output)):
    raise RuntimeError("Pandoc no pudo crear el DOCX")

formatter = get_formatter("apa7estudiante", str(output))
formatter.process(metadata)
formatter.save(str(output))

if not PDFGenerator.convert(str(output), str(output.parent), clean_markdown, str(pdf)):
    raise RuntimeError("No se pudo generar el PDF")

verifier = APAVerifier(pdf_path=pdf, docx_path=output, meta=metadata, strict=True)
try:
    result = verifier.verify_all()
finally:
    verifier.close()

if not result.passed:
    for issue in result.errors:
        print(issue.check, issue.expected, issue.actual, issue.evidence)
    raise RuntimeError("El documento no cumple la validación APA estricta")
```

Para ICONTEC o IEEE, cambia únicamente `get_formatter(...)` y no ejecutes
`APAVerifier`, porque su contrato no es APA.

## Checklist para una IA

- [ ] Confirmé el estándar y el tipo de documento.
- [ ] Confirmé los metadatos con el usuario; no inventé valores.
- [ ] Usé UTF-8 y frontmatter YAML válido.
- [ ] Incluí la estructura requerida para el perfil elegido.
- [ ] Usé `apa7estudiante` por defecto para trabajos estudiantiles.
- [ ] Generé el DOCX en una ruta explícita.
- [ ] Generé PDF solo cuando se solicitó y el backend está disponible.
- [ ] Ejecuté y leí la validación APA cuando correspondía.
- [ ] Corregí el Markdown y repetí la conversión si hubo errores.
- [ ] Reporté archivos, estándar, validación y errores restantes.

## Límites conocidos

- Pandoc es obligatorio para convertir Markdown.
- LibreOffice o WeasyPrint es necesario para PDF.
- Tesseract solo valida texto visual mediante OCR; no sustituye al verificador
  DOCX/PDF ni comprueba el significado académico.
- APA no valida la calidad de las fuentes, la originalidad, la exactitud de los
  resultados ni las reglas particulares de una institución.

# Uso como biblioteca

NormaDocs expone piezas pequeñas para construir un pipeline reproducible:

```text
MarkdownPreprocessor → PandocRunner → Formatter → PDFGenerator → APAVerifier
```

No mezcles perfiles: `APAVerifier` valida APA 7, no ICONTEC ni IEEE.

## Conversión DOCX

```python
from pathlib import Path

from normadocs.formatters import get_formatter
from normadocs.pandoc_client import PandocRunner
from normadocs.preprocessor import MarkdownPreprocessor

source = Path("informe.md")
output = Path("ExportDocs/informe_APA7ESTUDIANTE.docx")
output.parent.mkdir(parents=True, exist_ok=True)

markdown = source.read_text(encoding="utf-8")
clean_markdown, metadata = MarkdownPreprocessor().process(markdown)

if not PandocRunner().run(clean_markdown, str(output)):
    raise RuntimeError("Pandoc no pudo crear el DOCX")

formatter = get_formatter("apa7estudiante", str(output))
formatter.process(metadata)
formatter.save(str(output))
```

`MarkdownPreprocessor` debe ser la fuente de `DocumentMetadata`; no construyas
metadatos duplicados si el Markdown ya tiene frontmatter.

## Bibliografía

Pasa BibTeX y CSL al mismo `PandocRunner`:

```python
PandocRunner().run(
    clean_markdown,
    str(output),
    bibliography="references.bib",
    csl="apa.csl",
)
```

Las citas del Markdown deben usar la sintaxis de Pandoc, por ejemplo
`[@smith2024]`.

## Conversión APA con PDF y validación

```python
from pathlib import Path

from normadocs.formatters import get_formatter
from normadocs.pandoc_client import PandocRunner
from normadocs.pdf_generator import PDFGenerator
from normadocs.preprocessor import MarkdownPreprocessor
from normadocs.verifier.apa_verifier import APAVerifier

source = Path("informe.md")
out_dir = Path("ExportDocs")
out_dir.mkdir(parents=True, exist_ok=True)
docx_path = out_dir / "informe_APA7ESTUDIANTE.docx"
pdf_path = out_dir / "informe_APA7ESTUDIANTE.pdf"

markdown = source.read_text(encoding="utf-8")
clean_markdown, metadata = MarkdownPreprocessor().process(markdown)

if not PandocRunner().run(clean_markdown, str(docx_path)):
    raise RuntimeError("Pandoc falló")

formatter = get_formatter("apa7estudiante", str(docx_path))
formatter.process(metadata)
formatter.save(str(docx_path))

if not PDFGenerator.convert(
    str(docx_path), str(out_dir), clean_markdown, str(pdf_path)
):
    raise RuntimeError("No se pudo generar el PDF")

verifier = APAVerifier(
    pdf_path=pdf_path,
    docx_path=docx_path,
    meta=metadata,
    strict=True,
)
try:
    result = verifier.verify_all()
finally:
    verifier.close()

if not result.passed:
    for issue in result.errors:
        print(f"{issue.check}: {issue.expected} / {issue.actual}")
    raise RuntimeError("El documento no cumple APA 7 estricta")
```

`result.errors` contiene `check`, `expected`, `actual`, `evidence` y, cuando se
conoce, página y coordenadas. Un agente debe conservar esa información al
explicar un fallo.

## Otros estándares

```python
from normadocs.formatters import get_formatter

formatter = get_formatter("icontec", "document.docx")
# o: get_formatter("ieee", "document.docx")
```

No llames `APAVerifier` para esos perfiles. La validación APA no representa las
reglas de ICONTEC o IEEE.

## Configuración personalizada

```python
formatter = get_formatter(
    "apa7estudiante",
    "document.docx",
    config={
        "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
    },
)
```

Una configuración que cambia fuente, tamaño, márgenes o espaciado puede dejar
de ser APA 7. Si se necesita cumplimiento, conserva los valores del estándar y
verifica el resultado.

## Manejo de errores

- `PandocRunner.run(...) == False`: revisa Pandoc y el Markdown.
- `PDFGenerator.convert(...) == False`: instala LibreOffice o WeasyPrint.
- `result.passed is False`: corrige el Markdown y vuelve a generar; no parches
  el DOCX a mano.
- `FileNotFoundError` del verificador: proporciona rutas existentes de PDF y
  DOCX.

Para el contrato de entrada, estructura obligatoria y procedimiento para IA,
consulta [NormaDocs para agentes de IA](../ai-agent.md).

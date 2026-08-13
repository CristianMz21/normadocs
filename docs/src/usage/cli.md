# CLI Reference

`normadocs` tiene un único comando de conversión. La forma recomendada es
`normadocs INPUT`, no `normadocs convert INPUT`.

```bash
normadocs INPUT.md [OPTIONS]
```

## Comando mínimo

```bash
normadocs informe.md
```

Equivale a convertir con:

| Opción | Valor predeterminado |
|---|---|
| `--style` | `apa7estudiante` |
| `--format` | `docx` |
| `--output-dir` | `ExportDocs/` |
| `--apa-strict` | Activado para validación APA en PDF |

El archivo generado será `ExportDocs/informe_APA7ESTUDIANTE.docx`.

## Opciones principales

| Opción | Descripción | Predeterminado |
|---|---|---|
| `--style`, `-s` | `apa7estudiante`, `apa`, `icontec` o `ieee` | `apa7estudiante` |
| `--format`, `-f` | `docx`, `pdf` o `all` | `docx` |
| `--output-dir`, `-o` | Directorio de salida | `ExportDocs` |
| `--bibliography`, `-b` | Archivo BibTeX `.bib` | Ninguno |
| `--csl`, `-c` | Archivo de estilo CSL | Ninguno |
| `--verify-apa` / `--no-verify-apa` | Activar o desactivar verificación APA posterior | Activado |
| `--apa-strict` / `--no-apa-strict` | Tratar cualquier incidencia como fallo | Activado |
| `--apa-report` | Ruta del reporte Markdown APA | Ninguna |

La verificación APA solo se ejecuta cuando el estilo es APA y se genera PDF con
`--format pdf` o `--format all`. ICONTEC e IEEE no se validan como APA.

## LanguageTool

LanguageTool es opcional y requiere un servidor local o Docker:

```bash
# Servidor ya ejecutándose
normadocs informe.md --language-tool es

# Iniciar el contenedor automáticamente
normadocs informe.md --language-tool es --lt-docker

# Fallar ante cualquier error lingüístico
normadocs informe.md --language-tool es --lt-strict
```

Si no necesitas LanguageTool, no incluyas `--language-tool`.

## Bibliografía

```bash
normadocs informe.md \
  --bibliography references.bib \
  --csl apa.csl \
  --format all
```

Las citas del Markdown usan la sintaxis de Pandoc, por ejemplo `[@smith2024]`.

## Interpretar códigos de salida

| Código | Significado |
|---:|---|
| `0` | Conversión completada y, si correspondía, validación aprobada |
| distinto de `0` | Error de entrada, Pandoc, formato, PDF, LanguageTool o validación APA estricta |

Para una IA, un código distinto de cero obliga a leer el mensaje y el reporte
antes de afirmar que el documento está listo.

## Ejemplos por estándar

```bash
# Trabajo estudiantil APA 7 con reporte de validación
normadocs informe.md -s apa7estudiante -f all --apa-report ExportDocs/apa.md

# APA genérico/profesional
normadocs informe.md -s apa -f all

# ICONTEC NTC 1486
normadocs informe.md -s icontec -f all

# IEEE 8th Edition
normadocs informe.md -s ieee -f docx
```

## Ayuda integrada

```bash
normadocs --help
normadocs INPUT.md --help
```

Para un flujo completo con frontmatter, estructura del informe y criterios para
agentes, consulta la [guía de IA](../ai-agent.md).

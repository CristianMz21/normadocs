# Quickstart

Este recorrido genera un informe APA 7 estudiantil y verifica su PDF. Para que
una persona o una IA pueda repetir el proceso, cada paso tiene una entrada,
un comando y un resultado esperado.

## 1. Instalar dependencias

```bash
pip install normadocs[pdf-verifier]
```

También necesitas Pandoc en `PATH` para cualquier conversión:

```bash
pandoc --version
```

Para PDF instala LibreOffice (recomendado) o WeasyPrint:

```bash
# Debian/Ubuntu
sudo apt install libreoffice

# Alternativa Python
pip install normadocs[pdf]
```

## 2. Crear el Markdown

Guarda este ejemplo como `informe.md`. Sustituye los datos de ejemplo; no
uses valores inventados en un trabajo real.

```markdown
---
title: "Efectos del aprendizaje automático en la educación"
author: "Nombre completo"
affiliation: "Programa académico"
institution: "Institución educativa"
instructor: "Nombre del docente"
date: "2026-08-13"
---

# Resumen

Resumen opcional de hasta 250 palabras.

**Palabras clave:** aprendizaje automático, educación

# Introducción

Presenta el problema, el contexto y el objetivo.

# Desarrollo

Expone el análisis y la evidencia.

# Conclusiones

Resume los hallazgos y sus límites.

# Referencias

Autor, A. A. (2026). Título de la obra. Editorial.
```

Para el informe académico general, `Introducción`, `Desarrollo`, `Conclusiones` y
`Referencias` son obligatorios. `Resumen`, palabras clave y apéndices son
opcionales, pero se validan cuando aparecen. Consulta el [contrato para agentes
de IA](ai-agent.md) para todas las reglas.

## 3. Generar DOCX

El perfil predeterminado es `apa7estudiante`:

```bash
normadocs informe.md \
  --style apa7estudiante \
  --format docx \
  --output-dir ExportDocs
```

Resultado:

```text
ExportDocs/informe_APA7ESTUDIANTE.docx
```

El DOCX aplica portada, márgenes, tipografía, espaciado, encabezados,
referencias, tablas y figuras según el perfil seleccionado.

## 4. Generar y verificar PDF

```bash
normadocs informe.md \
  --style apa7estudiante \
  --format all \
  --output-dir ExportDocs \
  --apa-report ExportDocs/informe_apa.md
```

Resultado esperado:

```text
ExportDocs/informe_APA7ESTUDIANTE.docx
ExportDocs/informe_APA7ESTUDIANTE.pdf
ExportDocs/informe_apa.md
```

La validación APA estricta está activa por defecto. Si encuentra un error, el
comando termina con código distinto de cero y el reporte muestra la categoría,
la regla esperada, el valor encontrado y la evidencia.

## 5. Corregir y repetir

1. Abre `informe_apa.md`.
2. Corrige el Markdown o el frontmatter; no edites manualmente el DOCX generado.
3. Ejecuta de nuevo el comando `--format all`.
4. Continúa hasta obtener `PASSED`.

Para una validación no aplicable, usa `--no-verify-apa`; no lo uses para ocultar
incumplimientos de un trabajo APA.

## Otros estándares

```bash
# ICONTEC NTC 1486
normadocs informe.md --style icontec --format all --output-dir ExportDocs

# IEEE 8th Edition
normadocs informe.md --style ieee --format docx --output-dir ExportDocs
```

ICONTEC e IEEE no se validan con el verificador APA. Sus reglas están en
[Standards](standards/index.md).

## Siguiente paso

- [Guía para agentes de IA](ai-agent.md)
- [Referencia completa del CLI](usage/cli.md)
- [Uso como biblioteca](usage/library.md)
- [Reglas APA 7](standards/apa7.md)
- [Solución de problemas](troubleshooting.md)

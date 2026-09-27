# Quickstart: Informe APA7 Ultra-Estricto

```markdown
---
title: Analisis de sistemas de informacion
author: Cristian Arellano
program: Tecnologia en Analisis y Desarrollo de Software
institution: Servicio Nacional de Aprendizaje (SENA)
subject: Analisis y Diseno de Sistemas
subject_code: ADSO-2026
instructor: Nombre del instructor
date: 26 de septiembre de 2026
---

# Analisis de sistemas de informacion

## Planteamiento del problema

... (Pressman & Maxim, 2020, p. 4).

## Justificacion

...

## Objetivos

### Objetivo general

Analizar ...

### Objetivos especificos

1. Identificar ...
2. Describir ...
3. Analizar ...

## Marco teorico

...

## Metodologia

...

## Resultados

Como se muestra en la Tabla 1 ...

Tabla 1
*Caracteristicas ...*

| Caracteristica | Descripcion |
| --- | --- |
| Automatizacion | Reduce tareas manuales |

## Discusion

...

## Conclusiones

...

## Referencias

Pressman, R. S., & Maxim, B. R. (2020). *Software engineering: A
practitioner's approach* (9th ed.). McGraw-Hill.
```

```bash
normadocs convert informe.md --style apa7estudiante --format all
# expected: DOCX + PDF + "PASSED" 100/100, exit 0
```

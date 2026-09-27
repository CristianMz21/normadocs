---
title: "Automatización de procesos administrativos con software a medida en pymes colombianas"
subtitle: "Informe de análisis y diseño de sistemas de información"
author: "Cristian Muñoz Arellano"
affiliation: "Tecnología en Análisis y Desarrollo de Software"
program: "Tecnología en Análisis y Desarrollo de Software"
ficha: "2971789"
institution: "Servicio Nacional de Aprendizaje (SENA)"
center: "Centro de Servicios y Gestión Empresarial"
instructor: "Ing. Carolina Restrepo"
subject: "Análisis y Diseño de Sistemas de Información"
subject_code: "ADSO-2026"
location: "Medellín, Colombia"
date: "26 de septiembre de 2026"
short_title: "AUTOMATIZACIÓN EN PYMES"
---

# Resumen

Este informe analiza la automatización de procesos administrativos mediante
software a medida en pequeñas y medianas empresas colombianas, con énfasis
en los criterios técnicos para decidir inversiones en tecnología.

**Palabras clave:** automatización, pymes, sistemas de información, software

# Introducción

Las pequeñas y medianas empresas dependen cada vez más de los sistemas de
información para sostener sus procesos administrativos. García y Pérez (2024)
estudiaron la transformación digital en cuarenta empresas y encontraron
mejoras del veinticinco por ciento en los tiempos de proceso. Sin embargo,
la implementación suele enfrentar dificultades técnicas y organizacionales
que generan sobrecostos (Pressman y Maxim, 2020, p. 4).

# Marco teórico

## Antecedentes

Diversos autores coinciden en que la digitalización mejora la eficiencia
operativa cuando se acompaña de rediseño de procesos y capacitación del
personal encargado de operar el nuevo software.

## Bases teóricas

Un sistema de información integra hardware, software, bases de datos y
procedimientos para apoyar la toma de decisiones en la organización.

### Definiciones básicas

Se entiende por automatización la ejecución de tareas mediante reglas
definidas en software, con mínima intervención manual del usuario final.

# Metodología

## Enfoque

Cualitativo con apoyo documental y revisión de literatura académica
reciente sobre sistemas de información [@example2024article].

## Fases del estudio

1. Levantamiento de requerimientos con los interesados del proceso.
2. Modelado de los procesos actuales y propuestos del negocio.
3. Diseño de la arquitectura del software y del modelo de datos.
4. Validación de los resultados con los usuarios finales.

Las técnicas empleadas fueron las siguientes:

- Entrevistas semiestructuradas con el personal administrativo.
- Revisión de manuales de procedimiento y formatos vigentes.
- Observación directa de las tareas repetitivas del proceso.

# Resultados

Como muestra la Tabla 1, la automatización y la integración de datos
concentran la mayor percepción de beneficio entre el personal consultado.

| Criterio | Descripción | Beneficio |
|----------|-------------|-----------|
| Automatización | Reglas en software | Alto |
| Integración | Datos unificados | Alto |
| Capacitación | Entrenamiento | Medio |

Nota. Elaboración propia.

El indicador de eficiencia se calcula como se muestra a continuación:

```math
E = \frac{T_{manual} - T_{auto}}{T_{manual}} \times 100
```

La consulta base para medir los tiempos por proceso es la siguiente:

```sql {code}
select proceso, avg(tiempo_horas) as promedio from mediciones where ano > 2023 group by proceso
```

# Discusión

Los resultados coinciden con lo reportado en la literatura previa sobre
digitalización en empresas medianas del sector servicios y confirman la
importancia del acompañamiento al usuario durante la transición.

> El aprendizaje automático permite personalizar el contenido educativo de
> forma que cada estudiante avanza según sus propias necesidades y ritmo de
> aprendizaje particular, lo que a largo plazo mejora significativamente la
> retención y el rendimiento académico medido en evaluaciones estandarizadas
> diversas y complejas que reflejan el desempeño real (García, 2020).

# Conclusiones

La implementación de sistemas de información mejora la eficiencia de los
procesos administrativos cuando se acompaña de rediseño de procesos,
capacitación del personal y medición continua de los tiempos de respuesta.

# Referencias

García, J., y Pérez, M. (2024). Transformación digital en pymes.
    *Revista Gestión y Tecnología*, 18(2), 45-67.

Pressman, R. S., y Maxim, B. R. (2020). *Software engineering: A
    practitioner's approach* (9th ed.). McGraw-Hill.

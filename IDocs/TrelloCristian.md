**Taller para la determinación de las especificaciones funcionales del software y metodología a utilizar**

Cristian Zaid Arellano Muñoz

Programa de Análisis y Desarrollo de Software (ADSO)

Ficha 3336101

Servicio Nacional de Aprendizaje (SENA)

Evidencia: GA1-220501092-AA5-EV01 / Instructora: Nora Libby Osorio

22 de febrero de 2026

# Resumen

El presente informe documenta el proceso de migración de los requisitos del proyecto Shoppipai, un sistema de comercio electrónico B2C, desde el documento de Especificación de Requisitos de Software (ERS) hacia la herramienta de gestión Trello. Se configuró un tablero con siete listas bajo una metodología híbrida Scrum/Kanban, implementando un sistema de etiquetas por prioridad, área técnica, _story points_ y estado de despliegue. Cada requerimiento fue trasladado a tarjetas individuales con descripciones funcionales, criterios de aceptación en formato _checklist_ y asignación de responsabilidades. El tablero incluye además una lista de gestión de riesgos, una _Definition of Done_ y la documentación del stack tecnológico del proyecto. Como resultado, se logró una gestión más organizada y trazable de los requerimientos, facilitando el seguimiento del avance y la validación de las especificaciones funcionales.

**Palabras clave:** gestión de requisitos, Trello, Scrum, Kanban, validación de software, comercio electrónico

# Contenido

Resumen ..................................................... 3

Introducción ................................................ 4

Objetivos ................................................... 5

Objetivo General ........................................ 5

Objetivos Específicos ................................... 5

Marco Teórico ............................................... 6

Desarrollo de la Evidencia (Configuración en Trello) ....... 7

1.  Creación de cuenta y Tablero Principal ............... 7

2.  Migración de Requerimientos y Asignación ............. 8

3.  Detalle de Tarjeta y Criterios de Aceptación ......... 9

4.  Infraestructura Tecnológica .......................... 10

5.  Aseguramiento de Calidad (QA) ........................ 11

Conclusiones ................................................ 12

Referencias ................................................. 13

# Taller para la determinación de las especificaciones funcionales del software y metodología a utilizar

Gestionar bien los requisitos de software es fundamental para que el producto final realmente cumpla con lo que el cliente necesita (Sommerville, 2011). Según el SENA (2024), la validación de requisitos es una de las etapas más importantes del ciclo de vida del desarrollo, ya que permite asegurar que lo que se construye corresponde a lo que se especificó. En este documento se muestra cómo se pasaron los requisitos del proyecto "Shoppipai" —un e-commerce B2C— desde el documento ERS tradicional hacia Trello, una herramienta que permite organizar los requerimientos de forma visual, asignar responsables y llevar un control del avance del proyecto (Atlassian, 2026).

El tablero se organizó usando una metodología híbrida **Scrum/Kanban**, combinando la planificación por sprints con un flujo de trabajo visual. Se usaron etiquetas de colores para clasificar las tarjetas en cuatro categorías: prioridad (Rojo = Alta/Must, Amarillo = Media/Should, Verde = Baja/Could), área técnica (Azul = Frontend React/Next.js, Morado = Backend Django REST Framework, Celeste = Infraestructura y Seguridad), estimación de esfuerzo en _story points_ (1, 3 y 5) y estado de despliegue (Naranja = Staging/Pruebas, Lima = Producción).

# Objetivos

## Objetivo General

Utilizar Trello como herramienta de gestión para administrar, dar seguimiento y validar las especificaciones funcionales y no funcionales del sistema de comercio electrónico Shoppipai.

## Objetivos Específicos

- Crear un tablero en Trello con siete listas de control (Gestión de Riesgos, Sprint 1: MVP, Backlog Priorizado, QA/Pruebas, En Proceso, Terminado y Documentación y Artefactos) que representen las etapas del flujo de trabajo.
- Pasar los requerimientos del documento ERS a tarjetas en Trello, incluyendo descripciones, criterios de aceptación, etiquetas de prioridad y estimaciones de esfuerzo en _story points_.
- Usar un sistema de etiquetas que permita clasificar cada tarjeta por prioridad (MoSCoW), área técnica, esfuerzo estimado y estado de despliegue.
- Asignar responsabilidades dentro de la plataforma para simular un entorno de trabajo ágil.
- Registrar los riesgos identificados del proyecto junto con sus estrategias de mitigación.
- Definir una _Definition of Done_ (DoD) que establezca los criterios mínimos para considerar una tarea como terminada.

# Marco Teórico

La gestión de requisitos de software es el proceso mediante el cual se identifican, documentan, validan y controlan los cambios en los requerimientos a lo largo del ciclo de vida del proyecto. De acuerdo con el material de formación del SENA (2024), las técnicas de validación permiten verificar que los requisitos sean completos, consistentes y que respondan a las necesidades del cliente.

**Trello** es una herramienta de gestión de proyectos basada en tableros, listas y tarjetas que facilita la organización visual del trabajo (Atlassian, 2026). Su flexibilidad la hace adecuada para implementar diferentes metodologías ágiles, incluyendo Scrum y Kanban.

**Scrum** es un marco de trabajo ágil que organiza el desarrollo en iteraciones llamadas sprints, mientras que **Kanban** se centra en la visualización continua del flujo de trabajo. La combinación de ambas metodologías (Scrumban) permite aprovechar la planificación iterativa de Scrum con la flexibilidad visual de Kanban, lo que resulta útil para proyectos donde un solo desarrollador maneja múltiples tareas simultáneamente.

La técnica de priorización **MoSCoW** clasifica los requisitos en cuatro categorías: _Must have_ (obligatorios), _Should have_ (importantes), _Could have_ (deseables) y _Won't have_ (descartados por ahora). Esta técnica permite tomar decisiones claras sobre qué construir primero en cada sprint (SENA, 2026).

Los **story points** son una unidad de estimación relativa que mide el esfuerzo necesario para completar una tarea, considerando complejidad, incertidumbre y volumen de trabajo. En este proyecto se utilizó una escala Fibonacci simplificada (1, 3 y 5 puntos).

---

# Desarrollo de la Evidencia (Configuración en Trello)

A continuación se presentan las capturas de pantalla que muestran la configuración de Trello para gestionar los requerimientos del proyecto Shoppipai.

## 1. Creación de cuenta y Tablero Principal

Se creó el tablero "Ecomerce (Shoppipai)" en la cuenta de Trello del aprendiz (URL: https://trello.com/b/fSAMgh1R). El tablero cuenta con **siete listas**, cada una representando una etapa del flujo de trabajo:

- **Gestión de Riesgos:** Para registrar y dar seguimiento a los riesgos técnicos identificados en el análisis.
- **Sprint 1: MVP (Entrega Actual):** Agrupa las funcionalidades priorizadas para la primera entrega del sistema.
- **Backlog (Priorizado):** Contiene los requerimientos futuros priorizados con MoSCoW, listos para sprints posteriores.
- **En Proceso (Sincronizado con Código):** Aquí van las tarjetas de los requerimientos que están en desarrollo activo.
- **QA / Pruebas:** Se mueven aquí las tarjetas que ya terminaron desarrollo y están en verificación de calidad.
- **Terminado:** Para las tarjetas que ya se completaron y cumplen con la _Definition of Done_.
- **Documentación y Artefactos:** Centraliza los entregables documentales (Guía del Proyecto, Artefactos UML, Matriz de Trazabilidad, Bitácora de Sesiones Ágiles).

También se definió una **Definition of Done (DoD)** en la Guía del Proyecto. Una tarjeta solo se considera terminada cuando cumple: (1) Criterios de aceptación verificados, (2) Código limpio y documentado, (3) Diseño responsivo verificado, (4) Sin errores en consola, y (5) Aprobado en QA.

**Figura 1**

_Creación de cuenta en Trello_

![Creación de cuenta en Trello](./image/Cuentadetrello.png)

_Nota._ Captura de pantalla del perfil del aprendiz Cristian Muñoz en la plataforma Trello. Fuente: Trello (Atlassian, 2026).

**Figura 2**

_Vista general del tablero principal con todas sus listas_

![Vista general del Tablero Principal](./image/3.png)

_Nota._ Se observan las siete listas configuradas bajo la metodología híbrida Scrum/Kanban. Fuente: elaboración propia.

## 2. Migración de Requerimientos y Asignación de Responsabilidades

Los requerimientos del documento ERS se pasaron a tarjetas individuales dentro de las listas correspondientes. Cada tarjeta tiene su identificador, nombre descriptivo, etiqueta de prioridad y estimación en _story points_ (escala Fibonacci simplificada: 1, 3 y 5). Los requerimientos funcionales en la lista "En Proceso" son:

- **[RF-001]** Catálogo Interactivo de Productos — _Story Points: 3_ | Stack: React + Django Catalog App | Fecha límite: 1 de marzo de 2026.
- **[RF-002]** Filtros de Búsqueda Avanzados.
- **[RF-003]** Checkout Simplificado.
- **[RF-004]** Integración de Pagos con pasarela transaccional — _Story Points: 5_ | Stack: Django Payments App + Wompi/PayU API.
- **[RF-005]** Notificaciones por WhatsApp.

Las tarjetas de alta prioridad (RF-001 y RF-004) incluyen información del _stack_ tecnológico que se usará para implementarlas. En el caso del Catálogo, también tiene una fecha de entrega objetivo para planificar mejor el sprint.

En la lista "Terminado" se encuentra el requerimiento no funcional **[RNF-005] Mantenibilidad y Escalabilidad**, que se implementó con una arquitectura Monolito Modular en Django. La estructura base ya está terminada e incluye ocho aplicaciones modulares: `catalog`, `carts`, `orders`, `payments`, `notifications`, `inventory`, `customers` y `shipping`.

En "Gestión de Riesgos" se documentaron dos riesgos críticos:

- **Fallo en API de Pagos** (Impacto: Crítico): Mitigación con entorno Sandbox y patrón de reintentos (_Pattern Retries_).
- **Degradación de Rendimiento (LCP)** (Impacto: Medio): Mitigación con formatos WebP e _Intersection Observer Lazy Load_.

La asignación de responsabilidades se hizo con la etiqueta "CM" (Cristian Muñoz), asignada a cada tarjeta del tablero.

**Figura 3**

_Listas de requerimientos funcionales y no funcionales migrados al tablero_

![Listas de Requerimientos Funcionales y No Funcionales](./image/1.png)

_Nota._ Cada tarjeta incluye identificador, etiqueta de prioridad y estimación en story points. Fuente: elaboración propia.

## 3. Detalle de Tarjeta y Criterios de Aceptación

Cada tarjeta se configuró internamente con los siguientes elementos para poder validar los requerimientos:

- **Descripción funcional:** Un texto que explica el alcance del requerimiento y cómo se relaciona con los objetivos del negocio.
- **Lista de chequeo (_Checklist_):** Criterios de aceptación específicos para verificar si la funcionalidad cumple con lo esperado.
- **Etiquetas de prioridad y estado:** Indicadores visuales para identificar rápidamente la urgencia y el progreso de cada tarea.

Con este nivel de detalle se puede ir más allá de solo especificar el requisito: se puede validar que realmente se esté construyendo lo que el cliente necesita.

**Figura 4**

_Detalle de la tarjeta RF-001 con descripción funcional y criterios de aceptación_

![Detalle de tarjeta RF-001](./image/2.png)

_Nota._ Se muestra la descripción del requerimiento y la checklist de criterios de aceptación. Fuente: elaboración propia.

**Figura 5**

_Detalle de la tarjeta RF-002 con etiquetas, prioridades e historial de actividad_

![Detalle de tarjeta RF-002](./image/4.png)

_Nota._ Se observan las etiquetas de prioridad, área técnica y el historial de actividad de la tarjeta. Fuente: elaboración propia.

## 4. Infraestructura Tecnológica y Sincronización con el Código Fuente

El tablero también documenta el stack tecnológico del proyecto. Una decisión importante fue que las tarjetas del tablero reflejen la estructura real del repositorio de código, de modo que cada requerimiento funcional tenga un correlato directo en la arquitectura del sistema:

- **Backend:** Django REST Framework (Python) con arquitectura Monolito Modular. La estructura base está terminada con ocho aplicaciones modulares (`catalog`, `carts`, `orders`, `payments`, `notifications`, `inventory`, `customers`, `shipping`). Autenticación con JWT y bcrypt, variables de entorno protegidas con `.env` y soporte SSL.
- **Frontend (Storefront):** Vite + React + TypeScript, con componentes organizados en módulos: `api`, `components`, `pages`, `hooks` y `context`.
- **Dashboard Administrativo:** Next.js + Tailwind CSS, con estructura inicial para la gestión interna del e-commerce.
- **Base de datos:** PostgreSQL como motor relacional principal, con soporte para _partitioning_.
- **Contenedorización:** Docker + Docker Compose para estandarizar los entornos de desarrollo y despliegue.
- **CI/CD:** Pipeline de integración y despliegue continuo con GitHub Actions.
- **Seguridad:** Certificados SSL/TLS, cumplimiento de Habeas Data, variables de entorno protegidas y documentación de políticas en `SECURITY.md`.

Esta información se registró en la lista "Documentación y Artefactos", junto con la Guía del Proyecto (Definition of Done), los Artefactos UML, la Matriz de Trazabilidad y la Bitácora de Sesiones Ágiles.

## 5. Aseguramiento de Calidad (QA)

Se incluyó la lista **"QA / Pruebas"** como paso obligatorio antes de mover cualquier tarjeta a "Terminado". Esto refuerza el compromiso con la calidad y se complementa con los siguientes _frameworks_ de pruebas:

- **Backend:** Pytest-django para pruebas unitarias, de integración y de API.
- **Frontend:** Vitest como _test runner_ para los componentes React.

También se definieron **métricas de rendimiento objetivo** como parte de los criterios de aceptación de los requerimientos no funcionales:

_Métricas de rendimiento objetivo_

| Métrica                          | Objetivo       |
| -------------------------------- | -------------- |
| LCP (_Largest Contentful Paint_) | < 1.5 segundos |
| TTFB (_Time to First Byte_)      | < 500 ms       |
| Disponibilidad del sistema       | 99.9%          |

---

# Conclusiones

- Pasar los requisitos de un documento de texto a Trello facilita mucho el trabajo, ya que se evitan problemas de versiones desactualizadas y se tiene una sola fuente de verdad para todo el proyecto.
- La metodología híbrida Scrum/Kanban, con siete listas diferenciadas (incluyendo Backlog Priorizado y QA/Pruebas), permite tener la flexibilidad visual del Kanban sin perder la estructura iterativa del Scrum, lo cual funciona bien para un desarrollador que maneja varios frentes a la vez.
- El sistema de etiquetas por prioridad MoSCoW, área técnica, _story points_ y estado de despliegue permite filtrar y priorizar tareas desde distintas perspectivas sin necesitar herramientas adicionales.
- Las tarjetas con criterios de aceptación en _checklist_, estimaciones en _story points_ y una _Definition of Done_ clara permiten ir más allá de solo especificar: obligan a verificar punto por punto que se está construyendo el producto correctamente.
- Tener una lista de Gestión de Riesgos dentro del tablero da visibilidad constante sobre las amenazas técnicas del proyecto (como fallos en APIs de pago o problemas de rendimiento), lo que ayuda a tomar decisiones a tiempo durante los sprints.
- La sincronización entre las tarjetas del tablero y la estructura real del código (ocho aplicaciones Django, módulos frontend organizados, pipeline de CI/CD) refuerza la trazabilidad y permite entender rápidamente el estado del desarrollo.
- Definir métricas de rendimiento desde el inicio (LCP < 1.5s, TTFB < 500ms, disponibilidad del 99.9%) como parte de la gestión de requerimientos muestra que los requisitos no funcionales reciben el mismo seguimiento que los funcionales.

# Referencias

- Agile Business Consortium. (s.f.). _MoSCoW Prioritisation_. Recuperado el 21 de febrero de 2026, de https://www.agilebusiness.org/page/ProjectFramework_10_MoSCoWPrioritisation

- Atlassian. (2026). _Trello_ [Software de gestión de proyectos]. https://trello.com

- Atlassian. (s.f.). _¿Qué es Kanban?_. Recuperado el 21 de febrero de 2026, de https://www.atlassian.com/es/agile/kanban

- Schwaber, K. y Sutherland, J. (2020). _La Guía de Scrum: La Guía Definitiva de Scrum: Las Reglas del Juego_. Scrum.org. https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-Spanish.pdf

- Servicio Nacional de Aprendizaje. (2024). _Validación de requisitos_ [Material de formación]. Programa de Análisis y Desarrollo de Software. https://zajuna.sena.edu.co/

- Servicio Nacional de Aprendizaje. (2026). _Sesión en línea: Aplicar técnicas de validación de requisitos del software AP1- AA5 - EV1_ [Videoconferencia].

- Sommerville, I. (2011). _Ingeniería de software_ (9.ª ed.). Pearson Educación.

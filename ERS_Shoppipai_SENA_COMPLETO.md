**Especificación de Requisitos de Software para el Sistema de Comercio
Electrónico Shoppipai**

Cristian Zaid Arellano Muñoz

Programa de Análisis y Desarrollo de Software

Ficha 3336101

Servicio Nacional de Aprendizaje (SENA)

Centro de Materiales y Ensayos

13 de febrero de 2026

# Contenido

Resumen ..................................................... 3

Objetivos ................................................... 5

   Objetivo General ........................................ 5

   Objetivos Específicos ................................... 5

Descripción General del Sistema ......................... 6

   Propósito ........................................... 6

   Alcance ............................................. 6

   Metodología de Desarrollo ........................... 7

   Beneficios Esperados ................................ 7

*Stakeholders* o Interesados ............................ 8

Requisitos Funcionales .................................. 10

Requisitos No Funcionales ............................... 24

Historias de Usuario .................................... 30

Estrategia de Validación ................................ 36

   Construcción de Prototipos .......................... 36

   Diseño de Casos de Prueba ........................... 37

Matriz de Trazabilidad .................................. 38

Referencias ................................................. 40

# Resumen

El presente documento define la especificación de requisitos de software
para el desarrollo del sistema de comercio electrónico Shoppipai, una
plataforma web B2C diseñada para automatizar la gestión integral de
ventas y control de inventario de calzado. El proyecto busca transformar
el modelo operativo actual, basado en mensajería instantánea y registros
manuales, en una solución digital centralizada, escalable y segura. Se
identificaron siete requisitos funcionales prioritarios mediante
técnicas de entrevista semiestructurada y observación directa,
clasificados según la metodología MoSCoW y validados mediante prototipos
interactivos y casos de prueba detallados. La arquitectura propuesta
sigue principios ágiles bajo el marco Scrum, con énfasis en la
usabilidad, seguridad transaccional mediante pasarelas de pago
certificadas, y trazabilidad completa desde la consulta de productos
hasta la entrega al cliente. El sistema incluye módulos de catálogo
interactivo con filtros avanzados, proceso de *checkout* simplificado,
gestión automatizada de inventario en tiempo real, notificaciones
multicanal y portal de rastreo para clientes. Los requisitos no
funcionales garantizan diseño *responsive*, cumplimiento de normativas
de protección de datos, tiempos de respuesta óptimos y disponibilidad
del 99.9%. Este trabajo establece la línea base contractual para el
desarrollo del producto, asegurando alineación entre las expectativas
del negocio y la implementación técnica.

*Palabras clave:* especificación de requisitos, comercio electrónico,
sistema web, gestión de inventario, metodología ágil, arquitectura de
software, *stakeholders*, requisitos funcionales, requisitos no
funcionales



En el contexto de la transformación digital de los negocios, la
especificación rigurosa de requisitos de software constituye el
fundamento crítico para el éxito de cualquier proyecto de desarrollo.
Este documento presenta la Especificación de Requisitos de Software
(ERS) para el sistema de comercio electrónico Shoppipai, un proyecto
orientado a modernizar las operaciones de venta minorista de calzado
mediante la implementación de una plataforma web integral que automatice
los procesos de gestión de inventario, procesamiento de pedidos y
atención al cliente.

La necesidad de este sistema surge de las limitaciones operativas del
modelo actual de ventas, que depende exclusivamente de la comunicación
vía WhatsApp y registros manuales dispersos. Esta situación genera
múltiples problemas: tiempos excesivos dedicados a responder consultas
repetitivas sobre disponibilidad de productos, dificultades para
mantener información actualizada del inventario, falta de trazabilidad
en los pedidos, y ausencia de métricas confiables para la toma de
decisiones estratégicas. La propietaria del negocio ha identificado
estas deficiencias como los principales obstáculos para el crecimiento
sostenible de la empresa.

El propósito fundamental de este documento consiste en definir de manera
formal, completa y no ambigua el conjunto de requisitos funcionales y no
funcionales que regirán el desarrollo, implementación y despliegue del
sistema. Este artefacto técnico servirá como línea base contractual y
referencia técnica primordial entre el equipo de desarrollo y los
interesados (*stakeholders*), garantizando que el producto final se
alinee con precisión a las expectativas estratégicas y operativas del
negocio.

Para la elaboración de esta especificación se han aplicado técnicas de
ingeniería de requisitos reconocidas en la industria, incluyendo
entrevistas semiestructuradas con la propietaria del negocio (L. Delgado, comunicación personal, 16 de noviembre de 2025),
observación directa del flujo de trabajo actual, análisis de
documentación existente, y validación mediante prototipos interactivos.
Los requisitos se han clasificado utilizando la metodología MoSCoW
(*Must have, Should have, Could have, Won\'t have*) para establecer
prioridades claras y asegurar que el Producto Mínimo Viable (MVP)
incluya todas las funcionalidades críticas para la operación del
negocio.

El documento se estructura en siete secciones principales que cubren la
descripción general del sistema, la identificación y análisis de
*stakeholders*, la especificación detallada de requisitos funcionales y
no funcionales, el modelado mediante historias de usuario, la estrategia
de validación, y la matriz de trazabilidad que vincula cada requisito
con los objetivos estratégicos del proyecto.

Es pertinente señalar que este documento adopta deliberadamente un
**enfoque híbrido** de ingeniería de requisitos que combina la
estructura formal de la norma IEEE 830 (Requisitos Funcionales
numerados, criterios de aceptación verificables, clasificación de
estabilidad) con las prácticas ágiles del marco Scrum (Historias de
Usuario, estimación por puntos, desarrollo iterativo). Esta decisión
metodológica responde a una necesidad práctica identificada en la
industria del software: mientras que los Requisitos Funcionales (RF)
proporcionan la **formalidad contractual y la trazabilidad documental**
exigidas por los estándares académicos y profesionales —sirviendo como
línea base inmutable para la verificación y la auditoría—, las Historias
de Usuario (HU) traducen esos mismos requisitos al lenguaje del valor de
negocio, facilitando la **priorización dinámica, la planificación de
Sprints y la comunicación efectiva** con el *Product Owner* durante el
desarrollo iterativo. De este modo, cada RF encuentra su representación
operativa en una o más HU, y viceversa, garantizando coherencia
bidireccional entre la especificación formal y la ejecución ágil del
proyecto. Este enfoque está respaldado por autores como Wiegers y Beatty
(2013), quienes reconocen que la combinación de técnicas tradicionales y
ágiles maximiza la calidad de la especificación sin sacrificar la
flexibilidad del desarrollo.

# Objetivos

## Objetivo General

Especificar de manera completa, precisa y verificable los requisitos
funcionales y no funcionales del sistema de comercio electrónico
Shoppipai, estableciendo la línea base técnica y contractual que guiará
el desarrollo de una plataforma web robusta, segura y escalable,
orientada a automatizar integralmente el ciclo de ventas y gestión de
inventario, mejorando significativamente la experiencia del cliente y
proporcionando herramientas analíticas para la toma de decisiones
estratégicas basadas en datos.

## Objetivos Específicos

Identificar y documentar los requisitos funcionales del sistema que
describan con precisión las funcionalidades, procesos de negocio, reglas
y comportamientos que debe implementar la plataforma para satisfacer las
necesidades operativas del negocio y las expectativas de los usuarios
finales.

Definir los requisitos no funcionales que establezcan los atributos de
calidad del sistema, incluyendo aspectos de usabilidad, seguridad,
rendimiento, fiabilidad y escalabilidad, de acuerdo con estándares
internacionales reconocidos como ISO/IEC 25010.

Identificar y clasificar a todos los *stakeholders* o interesados del
proyecto, analizando su nivel de poder e interés mediante la matriz
Poder-Interés, para definir estrategias de gestión y comunicación
diferenciadas que aseguren su satisfacción y participación activa
durante el desarrollo.

Modelar los requisitos funcionales mediante la técnica de historias de
usuario, expresando cada funcionalidad desde la perspectiva del valor
que aporta a un rol específico y estableciendo criterios de aceptación
claros y verificables que faciliten la validación en cada iteración de
desarrollo.

Establecer una estrategia integral de validación de requisitos que
combine técnicas de prototipado evolutivo para validación temprana de
interfaces de usuario y diseño de casos de prueba detallados para
verificación funcional, minimizando el riesgo de retrabajo por
malentendidos o especificaciones ambiguas.

Construir una matriz de trazabilidad que vincule cada requisito
especificado con los objetivos estratégicos del negocio, los
*stakeholders* solicitantes y los entregables técnicos asociados,
asegurando transparencia, justificación y seguimiento completo del
alcance del proyecto.

# Descripción General del Sistema

## Propósito

El sistema Shoppipai es una plataforma de comercio electrónico B2C
(*Business to Consumer*) diseñada específicamente para la venta
minorista de calzado en línea. El propósito principal del sistema
consiste en automatizar y optimizar el ciclo completo de venta, desde la
exhibición del catálogo de productos hasta la entrega final al cliente,
eliminando las ineficiencias del modelo actual basado en comunicación
manual vía WhatsApp.

## Alcance

El alcance del proyecto abarca el diseño, desarrollo, pruebas y puesta
en producción de una solución web integral que cubre las siguientes
áreas funcionales principales:

Módulo de Cliente (*Frontend*). Incluye catálogo digital interactivo con
capacidades de filtrado avanzado, experiencia de compra optimizada con
carrito persistente y proceso de pago simplificado, y portal de
autogestión para rastreo de pedidos y consulta de historial.

Módulo Administrativo (*Backend*). Comprende gestión de inventario en
tiempo real con alertas de reabastecimiento, centro de procesamiento de
pedidos con *dashboard* centralizado, y sistema de notificaciones
multicanal mediante WhatsApp Business API y correo electrónico.

Integraciones Externas. El sistema se integrará con pasarelas de pago
certificadas (Wompi o PayU) para procesamiento seguro de transacciones,
APIs de mensajería instantánea para notificaciones automatizadas, y
servicios de correo electrónico transaccional para comunicaciones con
clientes.

## Metodología de Desarrollo

El proyecto adoptará un ciclo de vida ágil basado en el marco de trabajo
Scrum, con *Sprints* de dos semanas que permitirán entregas
incrementales de valor y retroalimentación continua. La elicitación de
requisitos se ha fundamentado en entrevistas semiestructuradas,
observación directa y análisis documental. Los requisitos se
especificarán mediante historias de usuario y se priorizarán utilizando
la técnica MoSCoW. La validación se realizará mediante prototipos
interactivos desarrollados en Figma y casos de prueba detallados que
cubran escenarios funcionales críticos.

## Beneficios Esperados

La implementación del sistema generará múltiples beneficios
cuantificables: reducción estimada del 90% en el tiempo dedicado a
consultas repetitivas sobre disponibilidad y precios, eliminación de
errores de inventario mediante actualización automática en tiempo real,
mejora en la satisfacción del cliente a través de información
transparente y autoservicio, reducción de tiempos de respuesta en el
procesamiento de pedidos mediante notificaciones automáticas, y
disponibilidad de métricas confiables para análisis de ventas y toma de
decisiones estratégicas.

# Stakeholders o Interesados

La identificación y análisis de los *stakeholders* constituye un
elemento fundamental para el éxito del proyecto, ya que permite
establecer estrategias de comunicación y gestión diferenciadas según el
nivel de poder e interés de cada grupo. La matriz Poder-Interés
clasifica a los interesados en cuatro cuadrantes estratégicos: Gestionar
Atentamente (alto poder, alto interés), Mantener Satisfecho (alto poder,
bajo interés), Mantener Informado (bajo poder, alto interés), y
Monitorear (bajo poder, bajo interés).

  -----------------------------------------------------------------------------------
  **ID**      **Interesado**   **Rol**       **Poder**   **Interés**   **Estrategia
                                                                       de Gestión**
  ----------- ---------------- ------------- ----------- ------------- --------------
  SH-01       Luisa Delgado    Propietaria   Alto        Alto          Gestionar
                               (Product                                Atentamente
                               Owner)                                  (Colaborar)

  SH-02       Cristian         Equipo de     Medio       Alto          Mantener
              Arellano         Desarrollo                              Informado

  SH-03       Clientes Finales Usuarios      Alto        Medio         Mantener
                               Compradores                             Satisfecho
                                                                       (Satisfacer)

  SH-04       Pasarela de      Proveedor     Alto        Bajo          Mantener
              Pagos            Tecnológico                             Satisfecho

  SH-05       Transportadora   Operador      Bajo        Bajo          Monitorear
                               Logístico                               (Observar)
  -----------------------------------------------------------------------------------

Cada *stakeholder* identificado requiere una estrategia de gestión
específica. Luisa Delgado, como *Product Owner*, debe participar
activamente en las ceremonias Scrum y validar todos los entregables. Los
clientes finales, aunque no participan directamente en el desarrollo,
definen el éxito comercial del sistema mediante su adopción y
satisfacción. La pasarela de pagos constituye un componente crítico de
alto poder que requiere satisfacción continua de sus requisitos técnicos
y planes de contingencia ante fallos. El equipo de desarrollo debe
mantenerse informado de las decisiones del proyecto con comunicación
fluida para asesorar sobre viabilidad técnica. La transportadora
requiere únicamente integración técnica adecuada para recepción de datos
de despacho.

# Requisitos Funcionales

Los requisitos funcionales describen las acciones, comportamientos y
procesos de negocio específicos que el sistema debe implementar. Cada
requisito se ha documentado siguiendo la estructura estándar de la
industria, incluyendo identificador único, nombre descriptivo,
descripción detallada, criterios de aceptación verificables, prioridad
según MoSCoW, y clasificación de estabilidad temporal según Sommerville
(Duradero para requisitos estables del núcleo del negocio, Volátil para
aquellos dependientes de tecnologías externas o regulaciones
cambiantes).

+-----------------------------------+-----------------------------------+
| **ID**                            | RF-001                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Catálogo Interactivo de Productos |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema debe mostrar una       |
|                                   | grilla de productos organizada y  |
|                                   | atractiva con carga diferida      |
|                                   | (lazy load) para optimizar el     |
|                                   | rendimiento y reducir el consumo  |
|                                   | de datos móviles. Cada ficha de   |
|                                   | producto debe incluir nombre      |
|                                   | completo, precio actual, precio   |
|                                   | anterior tachado (si aplica       |
|                                   | descuento), tallas disponibles en |
|                                   | tiempo real, variantes de color y |
|                                   | un carrusel de imágenes de alta   |
|                                   | calidad con funcionalidad de      |
|                                   | zoom.                             |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | 1\. Las imágenes deben permitir   |
|                                   | funcionalidad de zoom de alta     |
|                                   | resolución al pasar el mouse      |
|                                   | (desktop) o gesto de              |
|                                   | pellizcar/doble toque (móvil).    |
|                                   |                                   |
|                                   | 2\. Si el stock de una talla      |
|                                   | específica es 0, el sistema debe  |
|                                   | mostrar visualmente una etiqueta  |
|                                   | \'Agotado\' en rojo, deshabilitar |
|                                   | la opción de selección y bloquear |
|                                   | la compra para esa variante.      |
|                                   |                                   |
|                                   | 3\. El tiempo de carga inicial de |
|                                   | la galería de imágenes (LCP -     |
|                                   | Largest Contentful Paint) no debe |
|                                   | exceder los 1.5 segundos en redes |
|                                   | 4G estándar para asegurar una     |
|                                   | buena experiencia de usuario.     |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Must (Debe tener)                 |
+-----------------------------------+-----------------------------------+
| **Clasificación**                 | Duradero                          |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RF-002                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Filtros de Búsqueda Avanzados     |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | Permitir al usuario refinar la    |
|                                   | búsqueda de productos en el       |
|                                   | catálogo aplicando múltiples      |
|                                   | criterios simultáneos y           |
|                                   | combinables: talla específica,    |
|                                   | rango de precio (slider           |
|                                   | dinámico), marca, color y         |
|                                   | categoría (deportivo, casual,     |
|                                   | formal, sandalias, etc.). El      |
|                                   | filtrado debe realizarse de       |
|                                   | manera dinámica sin recargar la   |
|                                   | página completa.                  |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | 1\. El filtrado debe realizarse   |
|                                   | de manera dinámica utilizando     |
|                                   | tecnología AJAX o similar,        |
|                                   | actualizando los resultados en la |
|                                   | misma página sin recargarla       |
|                                   | completamente (comportamiento     |
|                                   | SPA).                             |
|                                   |                                   |
|                                   | 2\. El sistema debe mostrar un    |
|                                   | contador de resultados            |
|                                   | disponibles en tiempo real        |
|                                   | (ejemplo: \'15 zapatos            |
|                                   | encontrados\') antes de que el    |
|                                   | usuario aplique el filtro.        |
|                                   |                                   |
|                                   | 3\. Debe existir una opción       |
|                                   | visible, accesible y clara de     |
|                                   | \'Limpiar filtros\' para          |
|                                   | reiniciar la búsqueda rápidamente |
|                                   | a su estado original.             |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Must (Debe tener)                 |
+-----------------------------------+-----------------------------------+
| **Clasificación**                 | Duradero                          |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RF-003                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | *Checkout* Simplificado           |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema debe permitir a los    |
|                                   | usuarios no registrados realizar  |
|                                   | compras mediante un flujo de      |
|                                   | *checkout* simplificado de una    |
|                                   | sola página (*One-Page Checkout*) |
|                                   | donde ingresen información de     |
|                                   | envío y pago sin crear cuenta     |
|                                   | obligatoria.                      |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | 1\. Validación en tiempo real de  |
|                                   | campos obligatorios (email,       |
|                                   | dirección, teléfono, documento de |
|                                   | identidad) con mensajes de error  |
|                                   | claros, contextuales y amigables. |
|                                   |                                   |
|                                   | 2\. Persistencia automática de    |
|                                   | los datos ingresados en el        |
|                                   | navegador (local storage o        |
|                                   | sesión) si ocurre un error de     |
|                                   | validación, caída de red o        |
|                                   | recarga accidental, para evitar   |
|                                   | que el usuario tenga que          |
|                                   | reescribir todo.                  |
|                                   |                                   |
|                                   | 3\. Resumen flotante (sticky) del |
|                                   | pedido con desglose detallado de  |
|                                   | costos (subtotal, costo de envío, |
|                                   | impuestos, descuentos, total a    |
|                                   | pagar) visible en todo momento    |
|                                   | durante el proceso de scroll.     |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Must (Debe tener)                 |
+-----------------------------------+-----------------------------------+
| **Clasificación**                 | Duradero                          |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RF-004                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Integración con Pasarela de Pagos |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | Conexión segura, estable y        |
|                                   | robusta vía API o plugin          |
|                                   | certificado con proveedores de    |
|                                   | pago líderes en el mercado local  |
|                                   | como Wompi o PayU para procesar   |
|                                   | pagos con métodos locales (Nequi, |
|                                   | PSE, Daviplata, Efecty) y         |
|                                   | tarjetas de crédito/débito        |
|                                   | nacionales e internacionales.     |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | 1\. Redirección segura a la       |
|                                   | pasarela utilizando tokens de     |
|                                   | sesión encriptados, llaves de API |
|                                   | seguras y validación de           |
|                                   | integridad de datos (firma        |
|                                   | digital/hash) para evitar         |
|                                   | manipulaciones.                   |
|                                   |                                   |
|                                   | 2\. Recepción y procesamiento     |
|                                   | asíncrono de webhook/callback     |
|                                   | (servidor a servidor) para        |
|                                   | confirmar automáticamente el      |
|                                   | estado de la transacción          |
|                                   | (Aprobada, Rechazada, Pendiente)  |
|                                   | y actualizar el estado del pedido |
|                                   | en la base de datos sin depender  |
|                                   | de la redirección del usuario.    |
|                                   |                                   |
|                                   | 3\. Visualización de una página   |
|                                   | de respuesta personalizada        |
|                                   | (\'Thank you page\' o \'Error     |
|                                   | page\') clara, informativa y      |
|                                   | orientativa según el estado final |
|                                   | del pago, con instrucciones       |
|                                   | siguientes para el cliente.       |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Must (Debe tener)                 |
+-----------------------------------+-----------------------------------+
| **Clasificación**                 | Volátil (Implementación técnica   |
|                                   | dependiente de API externa; la    |
|                                   | funcionalidad de negocio es       |
|                                   | Permanente)                       |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RF-005                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Notificaciones Automáticas        |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema integrará una API de   |
|                                   | mensajería (WhatsApp Business)    |
|                                   | conectada al *backend*, para      |
|                                   | notificar automáticamente al      |
|                                   | administrador sobre nuevas ventas |
|                                   | realizadas, incluyendo los        |
|                                   | detalles del pedido y datos del   |
|                                   | cliente en tiempo real.           |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | 1\. El mensaje debe contener como |
|                                   | mínimo datos clave para la acción |
|                                   | inmediata: ID único del pedido,   |
|                                   | lista detallada de productos      |
|                                   | comprados (SKU, talla, color,     |
|                                   | cantidad), y datos completos de   |
|                                   | envío del cliente para la         |
|                                   | generación de la guía de          |
|                                   | transporte.                       |
|                                   |                                   |
|                                   | 2\. La latencia de envío del      |
|                                   | mensaje debe ser menor a 2        |
|                                   | minutos post-confirmación del     |
|                                   | pago para permitir una acción     |
|                                   | logística rápida y eficiente.     |
|                                   |                                   |
|                                   | 3\. Debe existir un mecanismo de  |
|                                   | fallback robusto (envío           |
|                                   | automático a correo electrónico o |
|                                   | SMS) si la API de mensajería      |
|                                   | falla, no está disponible         |
|                                   | momentáneamente o se agota la     |
|                                   | cuota de mensajes del mes.        |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Should (Debería tener)            |
+-----------------------------------+-----------------------------------+
| **Clasificación**                 | Volátil (Tecnología cambiante)    |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RF-006                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Alertas de *Stock* Crítico        |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema monitoreará            |
|                                   | continuamente los niveles de      |
|                                   | *stock* de todas las variantes de |
|                                   | producto (talla/color) y          |
|                                   | generará alertas visuales en el   |
|                                   | *dashboard* administrativo cuando |
|                                   | las cantidades desciendan por     |
|                                   | debajo del umbral configurado     |
|                                   | (ej: 3 unidades).                 |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | 1\. El umbral de alerta debe ser  |
|                                   | configurable por el administrador |
|                                   | según la criticidad del producto  |
|                                   | (valor por defecto sugerido:      |
|                                   | menos de 3 unidades), permitiendo |
|                                   | ajustes por categoría o producto  |
|                                   | específico.                       |
|                                   |                                   |
|                                   | 2\. Mostrar un indicador visual   |
|                                   | destacado (icono de advertencia,  |
|                                   | color rojo, notificación en       |
|                                   | *dashboard* o *badge* numérico)   |
|                                   | en la lista de productos del      |
|                                   | panel administrativo para llamar  |
|                                   | la atención sobre el stock bajo   |
|                                   | de forma inmediata.               |
|                                   |                                   |
|                                   | 3\. Bloqueo automático, inmediato |
|                                   | y concurrente de la venta en el   |
|                                   | *frontend* si el inventario llega |
|                                   | a 0 durante una sesión de usuario |
|                                   | activa, para evitar la sobreventa |
|                                   | (*overselling*) y problemas       |
|                                   | posteriores de servicio al        |
|                                   | cliente.                          |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Should (Debería tener)            |
+-----------------------------------+-----------------------------------+
| **Clasificación**                 | Duradero                          |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RF-007                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Rastreo de Pedidos Cliente        |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | Módulo de autoservicio intuitivo  |
|                                   | y accesible para que el cliente   |
|                                   | consulte el estado actual e       |
|                                   | histórico de su envío ingresando  |
|                                   | su número de pedido y/o correo    |
|                                   | electrónico de compra, reduciendo |
|                                   | significativamente las consultas  |
|                                   | de soporte tipo WISMO (Where Is   |
|                                   | My Order).                        |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | 1\. Los estados permitidos y      |
|                                   | visibles deben ser                |
|                                   | estandarizados, claros y          |
|                                   | comprensibles: Recibido, Pago     |
|                                   | Confirmado, En Preparación,       |
|                                   | Enviado/En Reparto, Entregado,    |
|                                   | Cancelado.                        |
|                                   |                                   |
|                                   | 2\. Visualización gráfica         |
|                                   | atractiva e intuitiva (línea de   |
|                                   | tiempo horizontal, stepper        |
|                                   | vertical o barra de progreso      |
|                                   | animada) del estado del proceso   |
|                                   | para facilitar la comprensión     |
|                                   | rápida del cliente sin necesidad  |
|                                   | de leer texto extenso.            |
|                                   |                                   |
|                                   | 3\. Si el estado es 'Enviado',    |
|                                   | el sistema debe mostrar           |
|                                   | obligatoriamente el número de     |
|                                   | guía de la transportadora y, si   |
|                                   | es técnicamente posible mediante  |
|                                   | integración API, un enlace        |
|                                   | directo (deep link) al portal de  |
|                                   | rastreo del operador logístico    |
|                                   | específico.                       |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Could (Podría tener)              |
+-----------------------------------+-----------------------------------+
| **Clasificación**                 | Volátil (Requisito emergente)     |
+-----------------------------------+-----------------------------------+

# Requisitos No Funcionales

Los requisitos no funcionales definen los atributos de calidad del
sistema según el estándar internacional ISO/IEC 25010, estableciendo
niveles de servicio cuantificables que garantizan la viabilidad
operativa, la satisfacción del usuario y el cumplimiento de normativas
aplicables. Estos requisitos son igualmente críticos que los
funcionales, ya que un sistema que cumple todas sus funcionalidades pero
falla en rendimiento, seguridad o usabilidad será rechazado por los
usuarios.

+-----------------------------------+-----------------------------------+
| **ID**                            | RNF-001                           |
+-----------------------------------+-----------------------------------+
| **Atributo de Calidad**           | Usabilidad                        |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema debe implementar       |
|                                   | diseño *responsive* (adaptable) y |
|                                   | accesible. La interfaz debe       |
|                                   | ajustarse fluidamente a           |
|                                   | diferentes tamaños de pantalla y  |
|                                   | resoluciones, garantizando una    |
|                                   | experiencia de usuario            |
|                                   | consistente, legible y funcional  |
|                                   | en cualquier dispositivo moderno  |
|                                   | (móviles, tabletas, computadoras  |
|                                   | de escritorio).                   |
+-----------------------------------+-----------------------------------+
| **Métrica/Restricción Técnica**   | \- El sitio debe ser totalmente   |
|                                   | funcional y visualmente correcto  |
|                                   | en teléfonos móviles (ancho       |
|                                   | mínimo 320px), tabletas en        |
|                                   | orientación vertical y            |
|                                   | horizontal, y computadoras de     |
|                                   | escritorio con resoluciones       |
|                                   | estándar.                         |
|                                   |                                   |
|                                   | \- Validación exhaustiva con      |
|                                   | herramientas de Developer Tools   |
|                                   | de navegadores, emuladores        |
|                                   | móviles en línea y dispositivos   |
|                                   | físicos representativos del       |
|                                   | mercado objetivo.                 |
|                                   |                                   |
|                                   | \- Cumplimiento de pautas básicas |
|                                   | de accesibilidad WCAG 2.1 Nivel   |
|                                   | A, incluyendo contraste de color  |
|                                   | adecuado, etiquetas alt           |
|                                   | descriptivas para imágenes, y     |
|                                   | navegación completa por teclado   |
|                                   | sin dependencia exclusiva del     |
|                                   | mouse.                            |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RNF-002                           |
+-----------------------------------+-----------------------------------+
| **Atributo de Calidad**           | Seguridad                         |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema debe garantizar        |
|                                   | confidencialidad e integridad de  |
|                                   | datos mediante protección robusta |
|                                   | de la información personal del    |
|                                   | cliente (PII - Personally         |
|                                   | Identifiable Information) y los   |
|                                   | datos transaccionales contra      |
|                                   | accesos no autorizados,           |
|                                   | interceptación durante la         |
|                                   | transmisión, o manipulación       |
|                                   | maliciosa.                        |
+-----------------------------------+-----------------------------------+
| **Métrica/Restricción Técnica**   | \- Implementación obligatoria y   |
|                                   | forzada de certificado SSL/TLS    |
|                                   | (HTTPS con protocolo TLS 1.2 o    |
|                                   | superior) en todas las páginas    |
|                                   | del sitio web, no solamente en el |
|                                   | *checkout*, para cifrado completo |
|                                   | de las comunicaciones             |
|                                   | cliente-servidor.                 |
|                                   |                                   |
|                                   | \- Encriptación de datos          |
|                                   | sensibles en reposo (almacenados  |
|                                   | en base de datos) utilizando      |
|                                   | algoritmos estándar de la         |
|                                   | industria: bcrypt o Argon2 para   |
|                                   | contraseñas de usuarios, AES-256  |
|                                   | para datos personales y tokens de |
|                                   | sesión.                           |
|                                   |                                   |
|                                   | \- Cumplimiento estricto de       |
|                                   | normativas locales de protección  |
|                                   | de datos personales (Ley 1581 de  |
|                                   | 2012 - Habeas Data en Colombia),  |
|                                   | incluyendo política de privacidad |
|                                   | publicada, aviso de cookies, y    |
|                                   | mecanismos de consentimiento      |
|                                   | informado del usuario.            |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RNF-003                           |
+-----------------------------------+-----------------------------------+
| **Atributo de Calidad**           | Eficiencia de Desempeño           |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema debe mantener tiempos  |
|                                   | de respuesta óptimos bajo         |
|                                   | condiciones de carga normal y     |
|                                   | picos de tráfico previsibles para |
|                                   | mantener la atención del usuario, |
|                                   | mejorar la tasa de conversión     |
|                                   | comercial, reducir la tasa de     |
|                                   | rebote (bounce rate) y favorecer  |
|                                   | el posicionamiento SEO orgánico   |
|                                   | en motores de búsqueda.           |
+-----------------------------------+-----------------------------------+
| **Métrica/Restricción Técnica**   | \- El tiempo de carga inicial de  |
|                                   | la página de inicio (First        |
|                                   | Contentful Paint - FCP) no debe   |
|                                   | superar los 3 segundos medidos en |
|                                   | una conexión móvil 4G promedio    |
|                                   | (velocidad de descarga aproximada |
|                                   | de 10 Mbps).                      |
|                                   |                                   |
|                                   | \- El tiempo de respuesta del     |
|                                   | servidor (TTFB - Time To First    |
|                                   | Byte) para solicitudes de API     |
|                                   | críticas (agregar producto al     |
|                                   | carrito, búsqueda con filtros,    |
|                                   | procesamiento de *checkout*) debe   |
|                                   | ser consistentemente menor a 500  |
|                                   | milisegundos bajo carga normal.   |
|                                   |                                   |
|                                   | \- El índice de velocidad general |
|                                   | (Speed Index) debe estar          |
|                                   | optimizado mediante técnicas de   |
|                                   | compresión de imágenes (WebP,     |
|                                   | JPEG progresivo), minificación de |
|                                   | código JavaScript y CSS, y lazy   |
|                                   | loading de recursos no críticos.  |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RNF-004                           |
+-----------------------------------+-----------------------------------+
| **Atributo de Calidad**           | Fiabilidad                        |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema debe garantizar        |
|                                   | disponibilidad continua y         |
|                                   | recuperación ante desastres para  |
|                                   | asegurar que la tienda esté en    |
|                                   | línea y operativa la mayor parte  |
|                                   | del tiempo, minimizando la        |
|                                   | pérdida de oportunidades de       |
|                                   | venta, especialmente durante      |
|                                   | campañas promocionales, fechas    |
|                                   | especiales o temporadas altas de  |
|                                   | ventas.                           |
+-----------------------------------+-----------------------------------+
| **Métrica/Restricción Técnica**   | \- Acuerdo de Nivel de Servicio   |
|                                   | (SLA) de disponibilidad           |
|                                   | operacional del 99.9% anual       |
|                                   | (equivalente a máximo 8.76 horas  |
|                                   | de inactividad no planificada por |
|                                   | año) garantizado contractualmente |
|                                   | por el proveedor de               |
|                                   | infraestructura/hosting           |
|                                   | seleccionado.                     |
|                                   |                                   |
|                                   | \- Implementación de copias de    |
|                                   | seguridad (backups) automáticas   |
|                                   | programadas diarias de la base de |
|                                   | datos completa, archivos          |
|                                   | estáticos cargados por usuarios,  |
|                                   | y configuraciones del sistema,    |
|                                   | con almacenamiento redundante     |
|                                   | externo (cloud storage) y         |
|                                   | retención mínima de 30 días para  |
|                                   | recuperación histórica ante       |
|                                   | desastres.                        |
|                                   |                                   |
|                                   | \- Procedimientos documentados y  |
|                                   | probados de recuperación ante     |
|                                   | desastres (Disaster Recovery      |
|                                   | Plan) que permitan restaurar el   |
|                                   | sistema a un estado funcional en  |
|                                   | menos de 4 horas desde la         |
|                                   | detección de un fallo crítico.    |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | RNF-005                           |
+-----------------------------------+-----------------------------------+
| **Atributo de Calidad**           | Mantenibilidad y Escalabilidad    |
|                                   | Arquitectónica                    |
+-----------------------------------+-----------------------------------+
| **Descripción**                   | El sistema debe implementar una   |
|                                   | arquitectura de software modular, |
|                                   | bien documentada y basada en      |
|                                   | principios de diseño sólidos que  |
|                                   | facilite cambios futuros,         |
|                                   | actualizaciones de tecnología,    |
|                                   | corrección rápida de errores y    |
|                                   | crecimiento horizontal del        |
|                                   | sistema sin acumulación excesiva  |
|                                   | de deuda técnica.                 |
+-----------------------------------+-----------------------------------+
| **Métrica/Restricción Técnica**   | \- El *backend* debe construirse    |
|                                   | bajo una arquitectura de Monolito |
|                                   | Modular bien estructurado, con    |
|                                   | separación clara y estricta de    |
|                                   | responsabilidades entre dominios  |
|                                   | lógicos del negocio (módulos de   |
|                                   | Catálogo, Inventario, Pedidos,    |
|                                   | Usuarios, Pagos) y capas técnicas |
|                                   | (Presentación/API, Lógica de      |
|                                   | Negocio/Servicios, Acceso a       |
|                                   | Datos/Repositorios).              |
|                                   |                                   |
|                                   | \- Esta estructura modular        |
|                                   | facilitará el mantenimiento       |
|                                   | evolutivo, permitirá pruebas      |
|                                   | unitarias aisladas por módulo, y  |
|                                   | posibilitará una migración futura |
|                                   | gradual y progresiva a una        |
|                                   | arquitectura de microservicios si |
|                                   | la escala del negocio y la        |
|                                   | complejidad operativa lo          |
|                                   | justifican técnica y              |
|                                   | económicamente.                   |
|                                   |                                   |
|                                   | \- Uso consistente y documentado  |
|                                   | de patrones de diseño estándar    |
|                                   | reconocidos por la industria: MVC |
|                                   | (Model-View-Controller) para      |
|                                   | estructura general, Repository    |
|                                   | Pattern para abstracción de       |
|                                   | acceso a datos, DTO (Data         |
|                                   | Transfer Objects) para            |
|                                   | comunicación entre capas, y       |
|                                   | Dependency Injection para         |
|                                   | inversión de control.             |
+-----------------------------------+-----------------------------------+

# Historias de Usuario

Las historias de usuario constituyen una técnica ágil de captura de
requisitos que expresa cada funcionalidad desde la perspectiva del valor
que aporta a un usuario específico. La estructura estándar sigue el
formato: \'Como \[rol\], quiero \[acción\], para \[beneficio\]\'. Cada
historia se complementa con criterios de aceptación expresados mediante
escenarios de comportamiento (BDD - *Behavior Driven Development*)
utilizando la sintaxis Dado-Cuando-Entonces que facilita la validación
objetiva del cumplimiento del requisito.

+-----------------------------------+-----------------------------------+
| **ID**                            | HU-001                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Ver Disponibilidad Inmediata      |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Alta                              |
+-----------------------------------+-----------------------------------+
| **Estimación**                    | 3 puntos                          |
+-----------------------------------+-----------------------------------+
| **Historia**                      | Como cliente interesado en un     |
|                                   | modelo específico de calzado,     |
|                                   | quiero ver si mi talla exacta     |
|                                   | está disponible en tiempo real    |
|                                   | antes de intentar agregarla al    |
|                                   | carrito, para no perder tiempo    |
|                                   | navegando en productos agotados,  |
|                                   | evitar la frustración de          |
|                                   | enamorarme de un producto que no  |
|                                   | puedo comprar y agilizar mi       |
|                                   | decisión de compra.               |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | Escenario A: Talla Disponible     |
|                                   |                                   |
|                                   | Dado que estoy en la ficha de     |
|                                   | detalle de un producto            |
|                                   | visualizando la información       |
|                                   |                                   |
|                                   | Cuando selecciono una talla       |
|                                   | específica que tiene inventario   |
|                                   | registrado en el sistema mayor a  |
|                                   | cero                              |
|                                   |                                   |
|                                   | Entonces el botón \'Agregar al    |
|                                   | Carrito\' se habilita visualmente |
|                                   | (color primario activo), muestra  |
|                                   | el precio vigente y permite       |
|                                   | realizar la acción de agregar el  |
|                                   | producto al carrito de compras.   |
|                                   |                                   |
|                                   | Escenario B: Talla Agotada        |
|                                   |                                   |
|                                   | Dado que estoy en la ficha de     |
|                                   | detalle de un producto            |
|                                   |                                   |
|                                   | Cuando selecciono una talla que   |
|                                   | tiene inventario igual a cero en  |
|                                   | el sistema                        |
|                                   |                                   |
|                                   | Entonces el botón de compra se    |
|                                   | deshabilita visualmente (color    |
|                                   | gris/inactivo), se muestra un     |
|                                   | texto claro e informativo \'Sin   |
|                                   | Stock\' o \'Agotado\' y           |
|                                   | opcionalmente aparece un campo de |
|                                   | suscripción \'Avísame cuando esté |
|                                   | disponible\' para notificaciones  |
|                                   | futuras.                          |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | HU-002                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Alerta de Venta en Tiempo Real    |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Alta                              |
+-----------------------------------+-----------------------------------+
| **Estimación**                    | 5 puntos                          |
+-----------------------------------+-----------------------------------+
| **Historia**                      | Como propietaria del negocio      |
|                                   | enfocada en la eficiencia         |
|                                   | operativa y tiempos de respuesta  |
|                                   | rápidos, quiero recibir una       |
|                                   | alerta instantánea en mi celular  |
|                                   | personal (vía WhatsApp) cada vez  |
|                                   | que se realice una venta exitosa  |
|                                   | en la plataforma web, para poder  |
|                                   | iniciar inmediatamente el proceso |
|                                   | de empaque y despacho del pedido, |
|                                   | reducir significativamente los    |
|                                   | tiempos de entrega al cliente     |
|                                   | final y tener visibilidad en      |
|                                   | tiempo real del flujo de ventas   |
|                                   | sin tener que revisar             |
|                                   | constantemente el panel           |
|                                   | administrativo del sistema.       |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | Escenario A: Pago Exitoso y Envío |
|                                   | de Notificación                   |
|                                   |                                   |
|                                   | Dado que un cliente completa      |
|                                   | exitosamente un proceso de pago   |
|                                   | en la plataforma web              |
|                                   |                                   |
|                                   | Cuando la pasarela de pagos       |
|                                   | notifica al sistema *backend* la    |
|                                   | aprobación definitiva de la       |
|                                   | transacción mediante webhook o    |
|                                   | callback seguro                   |
|                                   |                                   |
|                                   | Entonces el sistema consume       |
|                                   | automáticamente la API de         |
|                                   | WhatsApp Business y envía un      |
|                                   | mensaje predefinido y             |
|                                   | estructurado con los detalles     |
|                                   | clave del pedido (ID único, lista |
|                                   | de productos con tallas/colores,  |
|                                   | datos completos del cliente para  |
|                                   | envío) al número telefónico       |
|                                   | previamente configurado de Luisa. |
|                                   |                                   |
|                                   | Escenario B: Fallo en API de      |
|                                   | Mensajería con Mecanismo de       |
|                                   | Respaldo                          |
|                                   |                                   |
|                                   | Dado que la API de WhatsApp no    |
|                                   | responde a la solicitud, devuelve |
|                                   | un código de error HTTP o está    |
|                                   | temporalmente caída por           |
|                                   | mantenimiento                     |
|                                   |                                   |
|                                   | Entonces el sistema captura y     |
|                                   | registra detalladamente el error  |
|                                   | en un archivo de log de auditoría |
|                                   | para posterior revisión técnica y |
|                                   | diagnóstico, y envía              |
|                                   | inmediatamente la misma           |
|                                   | notificación de venta por correo  |
|                                   | electrónico prioritario (con      |
|                                   | asunto destacado) a la cuenta     |
|                                   | administrativa registrada como    |
|                                   | mecanismo de respaldo automático  |
|                                   | infalible.                        |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | HU-003                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Compra Rápida como Invitado       |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Media                             |
+-----------------------------------+-----------------------------------+
| **Estimación**                    | 8 puntos                          |
+-----------------------------------+-----------------------------------+
| **Historia**                      | Como cliente nuevo que valora la  |
|                                   | rapidez, privacidad y simplicidad |
|                                   | en las compras en línea, o como   |
|                                   | comprador ocasional que realiza   |
|                                   | una compra única sin intención de |
|                                   | crear perfil permanente, quiero   |
|                                   | poder realizar una compra         |
|                                   | completa de principio a fin sin   |
|                                   | tener que crear obligatoriamente  |
|                                   | una cuenta de usuario con         |
|                                   | contraseña ni validar mi correo   |
|                                   | electrónico previamente, para     |
|                                   | agilizar significativamente mi    |
|                                   | proceso de compra, reducir la     |
|                                   | fricción y pasos burocráticos     |
|                                   | innecesarios, evitar compartir    |
|                                   | más datos personales de los       |
|                                   | estrictamente necesarios y        |
|                                   | completar la transacción          |
|                                   | comercial en el menor tiempo      |
|                                   | posible.                          |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | Escenario A: Selección de Modo de |
|                                   | Compra Invitado                   |
|                                   |                                   |
|                                   | Dado que tengo uno o más          |
|                                   | productos agregados en mi carrito |
|                                   | de compras y estoy en la pantalla |
|                                   | de inicio de sesión o             |
|                                   | identificación del proceso de     |
|                                   | *checkout*                          |
|                                   |                                   |
|                                   | Cuando selecciono conscientemente |
|                                   | la opción visual claramente       |
|                                   | identificada como \'Continuar     |
|                                   | como invitado\', \'Compra rápida  |
|                                   | sin registro\' o equivalente      |
|                                   |                                   |
|                                   | Entonces el sistema me redirige   |
|                                   | directamente al formulario        |
|                                   | completo de datos de envío y      |
|                                   | facturación sin solicitar         |
|                                   | creación de contraseña, sin pedir |
|                                   | confirmación de email ni requerir |
|                                   | proceso de login con credenciales |
|                                   | existentes.                       |
|                                   |                                   |
|                                   | Escenario B: Finalización Exitosa |
|                                   | de Compra en Modo Invitado        |
|                                   |                                   |
|                                   | Dado que completé exitosamente    |
|                                   | todo el proceso de compra como    |
|                                   | usuario invitado, proporcionando  |
|                                   | únicamente mis datos de contacto  |
|                                   | y envío necesarios                |
|                                   |                                   |
|                                   | Entonces el sistema crea          |
|                                   | internamente un registro temporal |
|                                   | de cliente tipo \'Guest\' o       |
|                                   | \'Invitado\' asociado únicamente  |
|                                   | a este pedido específico para     |
|                                   | fines logísticos, de trazabilidad |
|                                   | y de historial transaccional,     |
|                                   | pero no me obliga a validar el    |
|                                   | correo electrónico para procesar  |
|                                   | y confirmar la orden de compra,   |
|                                   | no almacena credenciales de       |
|                                   | acceso permanentes en la base de  |
|                                   | datos, aunque opcionalmente puede |
|                                   | ofrecerme al final del proceso la |
|                                   | posibilidad de crear una cuenta   |
|                                   | completa con los datos ya         |
|                                   | ingresados (oferta opcional, no   |
|                                   | obligatoria).                     |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | HU-004                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Gestión de Stock Crítico          |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Alta                              |
+-----------------------------------+-----------------------------------+
| **Estimación**                    | 5 puntos                          |
+-----------------------------------+-----------------------------------+
| **Historia**                      | Como propietaria del negocio      |
|                                   | responsable de mantener la        |
|                                   | disponibilidad de productos,      |
|                                   | quiero recibir alertas visuales   |
|                                   | automáticas en el panel           |
|                                   | administrativo cuando el stock    |
|                                   | de cualquier variante de producto |
|                                   | (combinación de talla y color)    |
|                                   | alcance un nivel crítico          |
|                                   | configurable, para poder tomar    |
|                                   | decisiones oportunas de           |
|                                   | reabastecimiento, evitar quiebres |
|                                   | de stock que generen pérdidas de  |
|                                   | ventas y garantizar que los       |
|                                   | clientes siempre encuentren       |
|                                   | disponibilidad en los productos   |
|                                   | más demandados.                   |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | Escenario A: Stock por Debajo del |
|                                   | Umbral Configurado                |
|                                   |                                   |
|                                   | Dado que el administrador ha      |
|                                   | configurado un umbral de alerta   |
|                                   | de stock mínimo para un producto  |
|                                   | o categoría específica (por       |
|                                   | defecto: 3 unidades)              |
|                                   |                                   |
|                                   | Cuando el inventario disponible   |
|                                   | de una variante de producto       |
|                                   | desciende por debajo de dicho     |
|                                   | umbral tras una venta confirmada  |
|                                   | o un ajuste manual de inventario  |
|                                   |                                   |
|                                   | Entonces el sistema muestra un    |
|                                   | indicador visual destacado        |
|                                   | (icono de advertencia en color    |
|                                   | rojo y *badge* numérico con la    |
|                                   | cantidad restante) junto al       |
|                                   | producto en la lista del panel    |
|                                   | administrativo, y el widget de    |
|                                   | resumen del *dashboard* muestra   |
|                                   | un contador actualizado de        |
|                                   | "Productos en stock crítico".     |
|                                   |                                   |
|                                   | Escenario B: Stock Agotado con    |
|                                   | Bloqueo Automático de Venta       |
|                                   |                                   |
|                                   | Dado que un cliente está          |
|                                   | navegando activamente en la       |
|                                   | tienda y visualizando un producto |
|                                   | con inventario disponible         |
|                                   |                                   |
|                                   | Cuando otro cliente completa una  |
|                                   | compra que reduce el inventario   |
|                                   | de esa variante exacta a 0        |
|                                   | unidades de forma concurrente     |
|                                   |                                   |
|                                   | Entonces el sistema actualiza     |
|                                   | automáticamente la ficha del      |
|                                   | producto en el *frontend*,        |
|                                   | mostrando la etiqueta 'Agotado',  |
|                                   | deshabilitando el botón 'Agregar  |
|                                   | al Carrito' para esa variante y   |
|                                   | bloqueando cualquier intento de   |
|                                   | compra para evitar la sobreventa  |
|                                   | (*overselling*), sin necesidad de |
|                                   | que el cliente recargue la página |
|                                   | manualmente.                      |
+-----------------------------------+-----------------------------------+

+-----------------------------------+-----------------------------------+
| **ID**                            | HU-005                            |
+-----------------------------------+-----------------------------------+
| **Nombre**                        | Rastreo de Pedidos en Línea       |
+-----------------------------------+-----------------------------------+
| **Prioridad**                     | Baja                              |
+-----------------------------------+-----------------------------------+
| **Estimación**                    | 3 puntos                          |
+-----------------------------------+-----------------------------------+
| **Historia**                      | Como cliente que espera un        |
|                                   | pedido, quiero consultar el       |
|                                   | estado de mi envío ingresando el  |
|                                   | número de orden en la página web, |
|                                   | para conocer su ubicación real    |
|                                   | sin tener que escribirle a la     |
|                                   | tienda por WhatsApp.              |
+-----------------------------------+-----------------------------------+
| **Criterios de Aceptación**       | Escenario A: Consulta Exitosa     |
|                                   |                                   |
|                                   | Dado que tengo un número de       |
|                                   | pedido válido (ej: ORD-123)       |
|                                   |                                   |
|                                   | Cuando lo ingreso en el buscador  |
|                                   | de la página "Rastrear Pedido"    |
|                                   |                                   |
|                                   | Entonces el sistema muestra una   |
|                                   | barra de progreso visual con el   |
|                                   | estado actual (Recibido, Enviado, |
|                                   | Entregado) y el número de guía    |
|                                   | de la transportadora si aplica.   |
|                                   |                                   |
|                                   | Escenario B: Pedido No Encontrado |
|                                   |                                   |
|                                   | Dado que ingreso un número de     |
|                                   | pedido incorrecto o inexistente   |
|                                   |                                   |
|                                   | Cuando hago clic en "Buscar"      |
|                                   |                                   |
|                                   | Entonces el sistema muestra un    |
|                                   | mensaje de error amigable "No     |
|                                   | encontramos un pedido con ese     |
|                                   | número, por favor verifícalo".    |
+-----------------------------------+-----------------------------------+

# Estrategia de Validación

La validación de requisitos constituye una actividad crítica para
asegurar que las especificaciones son correctas, completas,
consistentes, no ambiguas y verificables antes de iniciar el desarrollo.
Una validación deficiente conduce a retrabajo costoso, insatisfacción
del cliente y riesgo de fracaso del proyecto. Por ello, se ha diseñado
una estrategia dual que combina validación temprana mediante prototipos
interactivos con validación continua mediante casos de prueba
estructurados.

## Construcción de Prototipos

Se aplicará la técnica de prototipado evolutivo e iterativo, centrada en
el usuario. Inicialmente se crearán prototipos de baja fidelidad
(*wireframes*) para definir la estructura de la información y el flujo
de navegación sin distracciones visuales. Tras validación inicial, se
desarrollarán *mockups* de alta fidelidad interactivos en Figma que
simulen la interacción real, permitiendo validar usabilidad, diseño
visual y jerarquía de información antes de la codificación. El objetivo
consiste en confirmar el flujo de compra completo (*end-to-end*), la
disposición óptima de elementos en fichas de producto para maximizar
conversión, y la adaptabilidad correcta en dispositivos móviles. La
validación requiere aprobación explícita documentada del *Product Owner*
antes de iniciar el *Sprint* 1 de desarrollo, sirviendo como referencia
visual para los desarrolladores.

## Diseño de Casos de Prueba

Se generarán casos de prueba detallados y estructurados para validar
funcionalmente los requisitos críticos y los flujos de negocio
complejos. Estos casos servirán como base para pruebas manuales de QA y
pruebas de aceptación del usuario (UAT) finales. Un caso fundamental es
CP-001: Proceso de Compra Exitoso con Pago Nequi, que verifica que un
cliente invitado complete el ciclo de compra de principio a fin
utilizando método de pago local, asegurando integración correcta de
todos los componentes (catálogo, carrito, *checkout*, pasarela,
inventario, notificaciones). Este caso de prueba documenta: (1)
Precondiciones: sistema en ambiente *Staging*/QA, producto con *stock*
disponible, pasarela configurada en modo *Sandbox*; (2) Pasos de
ejecución: navegación a catálogo, selección de producto y talla, agregar
al carrito, compra como invitado, formulario de envío, selección Nequi,
pago en pasarela, redirección; (3) Resultados esperados: redirección a
página de confirmación, descuento automático de inventario, pedido
visible en panel *admin* con estado Pagado, notificación WhatsApp
recibida, correo de confirmación enviado al cliente.

# Matriz de Trazabilidad

La matriz de trazabilidad constituye una herramienta de control y
seguimiento que vincula cada requisito especificado con los objetivos
estratégicos del negocio, los *stakeholders* solicitantes, su estado
actual y los entregables técnicos asociados. Esta matriz asegura
transparencia, justificación y seguimiento completo del alcance del
proyecto.

  ---------------------------------------------------------------------------------------------------------------
  **ID Req.** **Descripción**   **HU Asociada**          **Objetivo       **Stakeholder   **Estado**   **Entregable
                                                         Relacionado**    Solicitante**                Asociado**
  ----------- ----------------- ------------------------ ---------------- --------------- ------------ ----------------
  RF-001      Catálogo          HU-001 (Ver              Centralizar Info SH-03           Pendiente    Módulo Catálogo
              Interactivo       Disponibilidad           y Mejorar        (Clientes)                   *Frontend*
                                Inmediata)               Visualización                                 

  RF-002      Filtros Búsqueda  HU-001 (Ver              Mejorar          SH-03           Pendiente    Componente Barra
              Avanzados         Disponibilidad           Experiencia      (Clientes)                   Búsqueda
                                Inmediata)               Usuario                                       

  RF-003      *Checkout*          HU-003 (Compra           Optimización     SH-01 (Luisa)   Pendiente    Módulo *Checkout*
              Simplificado      Rápida como              Operativa y                                   *One-Page*
                                Invitado)                Conversión                                    

  RF-004      Pasarela Pagos    HU-003 (Compra           Seguridad        SH-01 (Luisa)   Pendiente    Integración API
                                Rápida como              Transaccional                                 Pagos
                                Invitado)                                                              

  RF-005      Alertas WhatsApp  HU-002 (Alerta de        Automatización   SH-01 (Luisa)   Pendiente    Servicio
                                Venta en Tiempo          Procesos                                      Notificaciones
                                Real)                                                                  

  RF-006      Gestión           HU-004 (Gestión          Centralizar Info SH-01 (Luisa)   Pendiente    *Dashboard*
              Inventario        de Stock                 y Control Stock                               Administrativo
              Crítico           Crítico)                                                               

  RF-007      Rastreo Pedidos   HU-005 (Rastreo          Autogestión y    SH-03           Pendiente    Portal Cliente /
                                de Pedidos en            Reducción        (Clientes)                   Tracking
                                Línea)                   Soporte                                       
  ---------------------------------------------------------------------------------------------------------------

# Referencias

Cohn, M. (2004). *User stories applied: For agile software development*. Addison-Wesley Professional.

IEEE Computer Society. (1998). *IEEE Std 830-1998: IEEE recommended practice for software requirements specifications*. Institute of Electrical and Electronics Engineers.

International Organization for Standardization. (2011). *ISO/IEC 25010:2011 Systems and software engineering --- Systems and software Quality Requirements and Evaluation (SQuaRE) --- System and software quality models*. ISO/IEC.

Pressman, R. S., & Maxim, B. R. (2014). *Software engineering: A practitioner\'s approach* (8th ed.). McGraw-Hill Education.

Schwaber, K., & Sutherland, J. (2020). *The Scrum guide: The definitive guide to Scrum: The rules of the game*. Scrum.org.

Servicio Nacional de Aprendizaje. (2024a). *Fundamentos de análisis y diseño de software* \[Material de formación\]. Programa de Análisis y Desarrollo de Software. https://zajuna.sena.edu.co/

Servicio Nacional de Aprendizaje. (2024b). *Ingeniería de requisitos* \[Material de formación\]. Programa de Análisis y Desarrollo de Software. https://zajuna.sena.edu.co/

Servicio Nacional de Aprendizaje. (2024c). *Validación de requisitos* \[Material de formación\]. Programa de Análisis y Desarrollo de Software. https://zajuna.sena.edu.co/

Sommerville, I. (2011). *Software engineering* (9th ed.). Addison-Wesley.

Wiegers, K., & Beatty, J. (2013). *Software requirements* (3rd ed.). Microsoft Press.

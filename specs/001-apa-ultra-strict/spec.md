# Feature Specification: APA7 Ultra-Strict Student Report by Default

**Feature Branch**: `001-apa-ultra-strict`

**Created**: 2026-09-26

**Status**: Draft

**Input**: User description: "mejorar y hacer mas estricto normadocs; informe
academico estrictamente bajo APA 7ma edicion; ultra estricto por defecto;
usar https://github.com/github/spec-kit"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convertir informe a DOCX ultra-estricto (Priority: P1)

Estudiante ejecuta `normadocs convert informe.md --style apa7estudiante` y
obtiene un DOCX que cumple APA 7 estudiante sin flags extra: portada de 7
campos, titulo repetido en pag. 2, margenes 2.54cm, doble espacio, Times New
Roman 12 (o Arial/Calibri/Georgia permitidos segun perfil), headings 1-5,
tablas/figuras numeradas, referencias con sangria francesa.

**Why this priority**: Es el camino principal; si esto falla, nada mas importa.

**Independent Test**: Convertir `examples/` de informe con frontmatter
completo; abrir DOCX y verificar portada, margenes, fuentes, headings con
`pytest tests/unit/test_apa_ultra_strict.py`.

**Acceptance Scenarios**:

1. **Given** un `.md` con frontmatter completo (titulo, autor, programa,
   institucion, asignatura+codigo, docente, fecha), **When** convierto con
   defaults, **Then** la portada contiene los 7 elementos centrados, titulo
   en negrita, y el cuerpo repite el titulo centrado-negrita en pag. 2.
2. **Given** un doc convertido, **When** inspecciono estilos, **Then**
   margenes = 1in, interlineado doble, `space_before/after = 0`,
   alineacion izquierda (no justificado), sangria primera linea 0.5in,
   headings 1 (centrado+negrita), 2 (izq+negrita), 3 (izq+negrita+cursiva),
   4/5 (sangria 0.5in + punto + run-in).
3. **Given** fuentes alternativas validas APA (Arial 11, Calibri 11,
   Georgia 11), **When** el perfil las permite, **Then** el verificador no
   las rechaza; Times New Roman 12 sigue siendo el default.

---

### User Story 2 - Verificacion estricta que falla el build (Priority: P1)

El pipeline verifica por defecto y falla (`exit 1`) ante cualquier
desviacion: portada incompleta, cita sin referencia, referencia sin cita,
tabla sin capcion o sin mencion previa, cita textual sin `p./pp.`, bloque
>=40 palabras con comillas.

**Why this priority**: "Ultra-estricto por defecto" significa que el error
llega al estudiante, no al docente.

**Independent Test**: `pytest tests/unit/test_apa_verify_strict.py` con
documentos defectuosos; `normadocs convert --format all` debe fallar con
`--apa-strict` (default true).

**Acceptance Scenarios**:

1. **Given** un cuerpo con `(Garcia, 2024)` sin entrada en Referencias,
   **When** verifico en estricto, **Then** obtengo
   `citations.reference_missing` como error y el comando falla.
2. **Given** una entrada en Referencias nunca citada, **When** verifico en
   estricto, **Then** obtengo `references.uncited` como error.
3. **Given** una `Tabla 1` sin mencion `Tabla 1` previa en el texto,
   **When** verifico, **Then** obtengo `tables.not_cited_before` como error.

---

### User Story 3 - Estructura de informe academico guiada (Priority: P2)

El sistema reconoce y exige el orden del informe: Planteamiento,
Justificacion, Objetivos (1 general + 3-5 especificos), Marco teorico,
Metodologia, Resultados, Discusion, Conclusiones, [Recomendaciones],
Referencias (pag. nueva), [Apendices]. `Introduccion` es opcional porque el
titulo hace de apertura (convencion APA).

**Why this priority**: Da valor academico real mas alla del formato fisico.

**Independent Test**: Documentos con secciones faltantes o desordenadas
fallan `structure.informe_*`; plantilla en `docs/` + ejemplo en `examples/`.

**Acceptance Scenarios**:

1. **Given** un informe sin `Objetivos`, **When** verifico, **Then** falla
   `structure.informe_objetivos_present`.
2. **Given** 2 objetivos especificos o 6, **When** verifico, **Then** falla
   `structure.informe_objetivos_count` (rango 3-5).
3. **Given** `Discusion` antes de `Resultados`, **When** verifico,
   **Then** falla `structure.informe_order`.

---

### User Story 4 - Citas y bloques APA 8.x estrictos (Priority: P2)

Citas narrativas (`Autor (2020)`) vs parenteticas (`(Autor, 2020)`); `&`
dentro de parentesis, `y` fuera (texto espanol); `et al.` para 3+ autores;
textual corta <40 palabras entre comillas con `p./pp.`; bloque >=40 sin
comillas, sangria 0.5in, doble espacio.

**Why this priority**: Es donde mas puntos se pierden en evaluaciones.

**Independent Test**: Casos parametrizados en `tests/unit/`.

**Acceptance Scenarios**:

1. **Given** `(Perez y Gomez, 2020)`, **When** formateo/verifico,
   **Then** se normaliza o falla a `(Perez & Gomez, 2020)`.
2. **Given** comillas con 45 palabras sin `p.`, **When** verifico,
   **Then** fallan `citations.block_quote_format` y/o `citations.page_missing`.

---

### Edge Cases

- Frontmatter sin `subject_code`: error de portada en estricto, warning si
  opt-out lax (no existe aun; por defecto siempre estricto).
- Doc sin tablas/figuras: checks de mencion previa pasan vacuos.
- `short_title` presente: se permite running head profesional en pags. 2+;
  sin `short_title`: header solo con numero de pagina (estudiante).
- Referencias con `s. f.` / `n. d.`: ordenan primero (cronologico APA).
- Documentos legacy que pasaban antes ahora fallan: aceptado y documentado
  en CHANGELOG (breaking change intencional).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El default `normadocs convert` (style `apa7estudiante`) MUST
  aplicar y verificar reglas ultra-estrictas sin flags adicionales.
- **FR-002**: La portada MUST contener y el verificador MUST exigir los 7
  elementos: titulo, autor, programa/departamento, institucion, asignatura +
  codigo, docente, fecha; pag. 1 con solo numero arriba-derecha.
- **FR-003**: El cuerpo MUST repetir el titulo centrado-negrita en pag. 2;
  `Introduccion` como heading MUST ser opcional.
- **FR-004**: El formateador MUST fijar carta 8.5x11in, margenes 1in,
  doble espacio, `space_before/after=0`, alineacion izquierda, sangria
  primera linea 0.5in (excepto primera linea tras titulo/heading, citas en
  bloque, referencias, captions).
- **FR-005**: Las fuentes MUST validar contra perfiles permitidos APA
  (TNR 12, Arial 11, Calibri 11, Georgia 11); default TNR 12; cualquier otra
  fuente/tamano MUST fallar en estricto.
- **FR-006**: Headings 1-5 MUST cumplir alineacion/negrita/cursiva/sangria/
  punto-run-in; Nivel 3 MUST ser error (no warning) en estricto.
- **FR-007**: Tablas/Figuras MUST numerarse 1..N sin huecos; caption arriba
  (`Tabla N` bold + titulo italic); `Nota.` italic debajo cuando exista;
  solo bordes horizontales; cada tabla/figura MUST mencionarse en el texto
  antes de aparecer.
- **FR-008**: Citas MUST usar `&` parentetico / `y` narrativo (ES),
  `et al.` para 3+ autores; textual corta MUST incluir `p./pp.`; bloque
  >=40 MUST ser sangria 0.5in sin comillas, doble espacio.
- **FR-009**: El verificador MUST cruzar citas<->referencias en ambas
  direcciones (`citations.reference_missing`, `references.uncited`).
- **FR-010**: Referencias MUST empezar en pag. nueva, titulo centrado-
  negrita, orden alfabetico + cronologico mismo autor, doble espacio,
  sangria francesa 0.5in, `https://doi.org/` para DOIs, `, & ` ante ultimo
  autor, journal+volumen en italic.
- **FR-011**: Estructura informe MUST validarse en orden y contenido minimo
  (objetivos 1+3-5, secciones requeridas, solo apendices tras referencias).
- **FR-012**: `running_head` default MUST ser desactivado (estudiante);
  solo con `short_title` se permite head profesional en pags. 2+.
- **FR-013**: Cada regla del formateador MUST tener su check espejo y
  viceversa; `apa7.yaml` + `apa7estudiante.yaml` son fuente unica de verdad.
- **FR-014**: Calidad MUST mantenerse: `ruff`, `mypy --strict`, `pyright`
  limpios, sin supresiones; `pytest -W error --cov-fail-under=78`.

### Key Entities

- **Informe academico**: portada 7 campos + secciones ordenadas + titulo
  repetido + referencias + apendices opcionales.
- **Perfil de estilo**: `apa7estudiante.yaml` (default estricto) vs
  `apa7.yaml` base; fuentes permitidas, running head, espaciado.
- **Cita**: narrativa vs parentetica, autores, ano, paginas, bloque.
- **Referencia**: entrada con autores, fecha, titulo, fuente, DOI/URL.
- **VerificationIssue**: check, severity, expected, actual, evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un informe modelo completo convierte y verifica con score
  100/100 y `PASSED` en defaults.
- **SC-002**: Cada defecto de las acceptance scenarios produce el check
  esperado y falla el comando en estricto (16/16 casos rojos en tests).
- **SC-003**: `make check` (lint + test-cov + security) pasa en Python
  3.10-3.13 sin supresiones (`scripts/find_suppressions.sh` limpio).
- **SC-004**: Cobertura total >= 78% y ningun warning de pytest
  (`-W error`).

## Assumptions

- `pandoc` en PATH y LibreOffice disponibles en CI/local para PDF.
- breaking change aceptado: docs legacy no-estrictos fallaran; se documenta.
- Alcance v1: espanol + ingles (nombres de seccion en ambos idiomas);
  otros idiomas fuera de alcance.
- Deteccion cita<->referencia es heuristica por apellido+ano (no CSL parse
  completo); suficiente para el 95% de casos estudiantiles.

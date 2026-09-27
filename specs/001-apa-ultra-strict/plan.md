# Implementation Plan: APA7 Ultra-Strict Student Report by Default

**Branch**: `001-apa-ultra-strict` | **Date**: 2026-09-26 | **Spec**: `specs/001-apa-ultra-strict/spec.md`

**Input**: Feature specification from `/specs/001-apa-ultra-strict/spec.md`

## Summary

Endurecer NormaDocs a ultra-estricto por defecto: portada de 7 campos,
fuentes por perfil APA, headings 1-5 estrictos, estructura de informe
guiada, tablas/figuras con mencion previa, citas con `p./pp.` y bloques,
cruce citas<->referencias, y verificacion que falla el build. Base: perfiles
YAML como fuente unica de verdad + simetria formatter<->verifier.

## Technical Context

**Language/Version**: Python 3.10+ (matrix 3.10-3.13)

**Primary Dependencies**: python-docx, pandoc (subprocess), typer,
pyyaml, LibreOffice/WeasyPrint (PDF)

**Storage**: N/A (archivos .md -> .docx/.pdf)

**Testing**: pytest, unittest patterns, Typer CliRunner, `-W error --cov-fail-under=78`

**Target Platform**: Linux (CI ubuntu), macOS local

**Project Type**: CLI (library/cli)

**Performance Goals**: conversion tipica < 30s; verificacion < 10s

**Constraints**: `mypy --strict` + `pyright` limpios; cero supresiones
(`RUFF_NOQA=1`, annotations-check); ruff line-length 100 (E,F,W,I,UP,B,SIM,RUF)

**Scale/Scope**: ~15 checks, 9 handlers, 1 plantilla, 1 ejemplo, ~20 tests nuevos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- I. Ultra-strict default: plan lo implementa (FR-001, strict default true). PASS
- II. Zero-suppression: ningun `noqa/type: ignore/nosec` en el plan. PASS
- III. Test-first: tasks exigen tests rojos primero + gate 78%. PASS
- IV. Formatter-verifier symmetry: cada FR tiene lado formatter + check. PASS
- V. Simplicity: se reutilizan handlers/checks existentes, sin nuevos
  servicios. PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-apa-ultra-strict/
├── spec.md               # Feature spec (done)
├── plan.md               # This file
├── research.md           # Phase 0: decisiones (perfiles fuente, heuristica cita<->ref)
├── data-model.md         # Phase 1: entidades (Informe, Perfil, Cita, Referencia, Issue)
├── quickstart.md         # Phase 1: como convertir un informe modelo
├── contracts/            # Phase 1: CLI contract (flags) + check catalog
└── tasks.md              # Phase 2 output
```

### Source Code (repository root)

```text
src/normadocs/
├── config.py                      # METADATA_FIELDS + subject_code
├── models.py                      # subject_code, course_code
├── preprocessor.py                # title page md 7 campos
├── standards/
│   ├── apa7.yaml                  # base (running_head off, fonts perfis)
│   └── apa7estudiante.yaml        # default ultra-strict profile
├── formatters/apa/
│   ├── apa_cover.py               # orden 7 campos
│   ├── apa_page.py                # running head solo con short_title
│   ├── apa_styles.py              # fuentes por perfil
│   ├── apa_paragraphs.py          # headings, bloques, sangrias
│   ├── apa_citations.py           # & / et al. / p.
│   └── apa_tables.py / apa_figures.py  # captions + mencion previa (formatter deja marcas)
└── verifier/checks/
    ├── cover_page.py              # 7 campos
    ├── structure.py (+ informe_structure)  # orden + objetivos 1+3-5 + intro opcional
    ├── fonts.py                   # perfiles permitidos
    ├── headings.py                # L3 error
    ├── tables.py / figures.py     # secuencia + mencion previa
    ├── citations.py               # & / et al. / p. / bloque
    ├── references.py (+ cross-check)  # orden + formato + uncited
    └── cross_refs.py (nuevo)      # citas<->referencias ambas direcciones

tests/
├── unit/test_apa_ultra_strict.py  # formatter estricto
└── unit/test_apa_verify_strict.py # verifier estricto (16 casos rojos/verdes)
```

**Structure Decision**: Single project existente; sin nuevos top-level
paquetes. Nuevo check `cross_refs.py` registrado en `apa_verifier.py` y
`checks/__init__.py`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Nuevo check `cross_refs.py` | Cruce bidireccional cita<->ref no cabe en checks actuales sin mezclar responsabilidades | Meterlo en `citations.py`/`references.py` duplicaria parsing y romperia simetria single-responsibility |

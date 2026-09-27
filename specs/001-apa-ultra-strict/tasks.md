# Tasks: APA7 Ultra-Strict Student Report by Default

**Input**: Design documents from `/specs/001-apa-ultra-strict/`

**Prerequisites**: plan.md (done), spec.md (done)

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Crear `specs/001-apa-ultra-strict/{research,data-model,quickstart}.md` y `contracts/` con catalogo de checks
- [ ] T002 [P] Alinear `src/normadocs/models.py` (`subject_code`) y `config.py` (`METADATA_FIELDS`) con los 7 campos de portada
- [ ] T003 [P] Fijar perfiles `standards/apa7.yaml` (`running_head.enabled: false`, `fonts.allowed`) y `standards/apa7estudiante.yaml` ultra-estricto

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T004 Tests rojos base en `tests/unit/test_apa_ultra_strict.py` y `tests/unit/test_apa_verify_strict.py` (portada 7 campos, fuentes, headings, tablas, citas, cross-ref) — DEBEN fallar antes de implementar
- [ ] T005 Registrar nuevo check `verifier/checks/cross_refs.py` en `checks/__init__.py` y `apa_verifier.py::_init_checks`

**Checkpoint**: Tests rojos confirmados con `pytest tests/unit/test_apa_ultra_strict.py tests/unit/test_apa_verify_strict.py -v`

## Phase 3: User Story 1 — DOCX ultra-estricto (P1) MVP

- [ ] T006 [P] [US1] Portada 7 campos en `preprocessor.py:build_title_page_md` + `formatters/apa/apa_cover.py` (orden: titulo, autor, programa/depto, institucion, asignatura+codigo, docente, fecha)
- [ ] T007 [P] [US1] Titulo repetido centrado-negrita pag. 2 (`apa_cover.py:_ensure_cover_title`) + `cover_page.py:title_repeated`
- [ ] T008 [US1] Formato fisico en `apa_page.py`/`apa_styles.py`/`apa_paragraphs.py` (carta, 1in, doble, space 0, izquierda, sangria 0.5in) — depende T002-T003
- [ ] T009 [US1] Fuentes por perfil en `apa_styles.py` + `verifier/checks/fonts.py` (TNR12/Arial11/Calibri11/Georgia11)
- [ ] T010 [US1] Headings 1-5 estrictos (`apa_styles.py`, `apa_paragraphs.py`, `checks/headings.py` L3=error)

**Checkpoint**: US1 convierte un informe modelo con score 100/100

## Phase 4: User Story 2 — Verificacion que falla (P1)

- [ ] T011 [P] [US2] `checks/cross_refs.py`: `citations.reference_missing` + `references.uncited` (apellido+ano, tolera `s. f./n. d.`)
- [ ] T012 [P] [US2] Mencion previa tabla/figura en `checks/tables.py` + `checks/figures.py` (`tables.not_cited_before`, `figures.not_cited_before`)
- [ ] T013 [US2] `cover_page.py` + `structure.py`: 7 campos, header solo-pagina, referencias en pag. nueva
- [ ] T014 [US2] CLI: confirmar `--apa-strict` default true falla el build (`cli.py:_should_verify_apa`, `_verify_apa_stage`) + test CLI

**Checkpoint**: US1+US2 — 16 casos rojos/verdes pasan

## Phase 5: User Story 3+4 — Informe + citas (P2)

- [ ] T015 [P] [US3] `checks/structure.py` (o `informe_structure.py`): orden informe, intro opcional, objetivos 1+3-5, solo apendices tras referencias
- [ ] T016 [P] [US4] `checks/citations.py` + `apa_citations.py`: `&`/`y`, `et al.`, `p./pp.` corta, bloque >=40 sin comillas
- [ ] T017 [P] [US4] `checks/references.py`: `https://doi.org/`, `, & `, journal+volumen italic, orden alfa+crono
- [ ] T018 Plantilla `docs/src/.../informe-apa7.md` + ejemplo `examples/informe_apa7ejemplo.md` + CHANGELOG breaking change

**Checkpoint**: Todas las user stories funcionales

## Phase 6: Polish

- [ ] T019 `make check` verde (ruff+mypy+pyright+pytest `-W error --cov-fail-under=78`+bandit) + `scripts/find_suppressions.sh` limpio
- [ ] T020 Run `quickstart.md` end-to-end: convertir ejemplo, verificar 100/100, generar PDF si LibreOffice disponible

## Dependencies & Execution Order

- T001-T003 sin dependencias (T002, T003 paralelizables)
- T004-T005 bloquean US1/US2 (tests rojos primero)
- T006/T007 en paralelo; T008 depende T002-T003; T009-T010 en paralelo
- T011/T012/T013 en paralelo; T014 al final de US2
- T015/T016/T017 en paralelo; T018 cierra
- T019-T020 polish final

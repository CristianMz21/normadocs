# Feature Specification: Correcciones de evaluación estricta (informe APA7)

**Feature Branch**: `002-correcciones-evaluacion`

**Created**: 2026-09-26

**Status**: Implemented

**Input**: External strict review of `informe_apa7_ejemplo_APA7ESTUDIANTE.pdf`
(7 findings; 4 confirmed defects, 3 already-correct claims).

## Findings vs. evidence (DOCX runs + PDF spans + border XML)

- CONFIRMED `Instructor:` prefix → emit bare instructor name (F1).
- CONFIRMED fragmented pagination (11 breaks) → continuous body; only
  references/appendices open a page via shared `config.is_section_break_heading` (F2).
- CONFIRMED ordered objectives flattened to bullets (`numPr` stripped) →
  preserve ordered numbering by `numFmt`, bullets stay literal (F3).
- CONFIRMED title not Title Case → `cover_page.title_case` warning
  (verify-only, Spanish minor-word list; never rewrites) (F6).
- REJECTED vertical table lines in current artifact (0 vertical / 3
  horizontal rules in PDF) → hardening only: explicit table-level borders
  + cell-level vertical check in verifier (F4).
- REJECTED caption/reference italics (PDF shows BoldMT/ItalicMT) →
  hardening only: auto-italic book titles + `references.book_title_italic` (F5).
- REJECTED heading hierarchy + cover blank line (DOCX data correct).

## Requirements

- **FR-001**: Cover instructor line MUST be the bare name.
- **FR-002**: Preprocessor MUST break pages only before
  references/appendix H1s; `apa_page` fallback MUST share the same set
  (Conclusiones excluded).
- **FR-003**: Ordered lists MUST keep Word numbering with 0.5in hanging
  indent; unordered lists keep the literal-bullet rendering.
- **FR-004**: Tables MUST carry explicit horizontal-only borders at table
  and cell level; verifier MUST flag cell-level verticals.
- **FR-005**: Plain book-style entries MUST get auto-italic titles;
  verifier MUST flag missing title italics.
- **FR-006**: Sentence-case cover titles MUST warn (`title_case`),
  never auto-rewritten.
- **FR-007**: `DOCXParagraphInfo.is_list_item` MUST expose Word numbering
  so objective counting works with preserved lists.

## Success Criteria

- **SC-001**: `examples/informe_apa7_ejemplo.md` converts (docx+pdf) and
  verifies strict 100/100 PASSED. ACHIEVED (12 → 5 pages).
- **SC-002**: Full gates green: ruff, mypy --strict, pyright 0/0/0,
  bandit 0, pytest -W error --cov-fail-under=78 (89.09%), no suppressions.

# Data Model: APA Ultra-Strict

## Informe academico

- `title: str` (required)
- `author: str` (required)
- `program: str` (programa o departamento, required)
- `institution: str` (required)
- `subject: str` (asignatura, required)
- `subject_code: str` (codigo, required)
- `instructor: str` (docente, required)
- `date: str` (required)
- `sections: list[Section]` in fixed order (see spec US3)

## Perfil de estilo

- `fonts.allowed: list[{name, size}]` — default 4 APA profiles
- `running_head.enabled: bool` — default false (student)
- `spacing.line: double`, `paragraph_before/after: 0`
- `margins: 1in x4`, `page_setup: letter`

## Cita

- `kind: narrative | parenthetical`
- `authors: list[str]`, `year: str` (YYYY | s. f. | n. d.), `pages: str | None`
- `words: int` → `is_block = words >= 40`

## Referencia

- `authors_head: str`, `year: str`, `title: str`, `source: str`, `doi_url: str | None`
- `sort_key = (author.casefold(), year_int, full.casefold())`

## VerificationIssue

Existing dataclass unchanged; new check ids:
`cover_page.{subject,instructor,date}_present`,
`structure.informe_{section}_present|order|objetivos_count`,
`citations.{page_missing,reference_missing}`,
`references.uncited`,
`tables|figures.not_cited_before`,
`fonts.profile_mismatch`.

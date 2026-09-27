# Research: APA Ultra-Strict

## Decision 1: Font profiles, not single font

APA 7 allows TNR 12, Arial 11, Calibri 11, Georgia 11. Current
`fonts.py` strict rejects everything but TNR 12. Decision: `fonts.allowed`
list in YAML + `get_default_config` default of the 4 profiles; verifier
accepts any run matching one full profile (name+size), formatter defaults
to TNR 12.

## Decision 2: Citation<->reference heuristic

Full CSL parsing out of scope. Heuristic: extract `(Surname, YEAR)` and
`Surname (YEAR)` keys (surname = first capitalized token, year = 4-digit or
`s. f./n. d.`), compare casefolded sets both directions. Tolerates `et al.`.
95% student coverage, documented limitation.

## Decision 3: Table/figure mention-before

Formatter guarantees caption above + numbering. Verifier adds
`not_cited_before`: first body mention index of `Tabla N` must precede the
table element index. Same for figures. Vacuous pass when no tables.

## Decision 4: Informe structure as extension of StructureCheck

Rather than a new top-level concept, extend `structure.py` with informe
vocabulary (planteamiento, justificacion, objetivos, marco, metodologia,
resultados, discusion, conclusiones, recomendaciones, referencias,
apendices) + keep legacy abstract/intro/development aliases. Introduction
heading optional (title-as-opening per APA).

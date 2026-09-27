# Contracts: CLI + Check Catalog

## CLI contract (unchanged flags, stricter defaults)

- `normadocs convert INPUT --style apa7estudiante --format docx|pdf|all`
- `--verify-apa/--no-verify-apa` default true; `--apa-strict` default true
  (any warning = failure, exit 1); `--apa-report PATH` markdown report.
- Style resolution: `apa|apa7 -> apa7.yaml`, `apa7estudiante -> apa7estudiante.yaml`.

## Check catalog (new/changed ids)

- `cover_page.{title,author,program,institution,subject,instructor,date}_present|alignment`
- `cover_page.no_header`, `cover_page.title_repeated`
- `structure.informe_{planteamiento,justificacion,objetivos,marco,metodologia,resultados,discusion,conclusiones,referencias}_present`
- `structure.informe_objetivos_count` (1 general + 3-5 especificos)
- `structure.informe_order`, `structure.content_after_references`
- `fonts.profile_mismatch` (run must match one allowed profile)
- `headings.level3_*` severity error in strict
- `tables.{caption_bold,caption_italic,caption_position,numbering_sequence,not_cited_before,vertical_borders}`
- `figures.{...,not_cited_before}`
- `citations.{ampersand,et_al,block_quote_format,page_missing,reference_missing}`
- `references.{section_present,hanging_indent,spacing,alphabetical_order,entry_ampersand,doi_format,italic_source,uncited}`

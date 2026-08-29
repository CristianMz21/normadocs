# OpenSpec Specs — Source of Truth

This directory holds the consolidated main specs per domain. It is empty at bootstrap.

Main specs live at `openspec/specs/{domain}/spec.md`. Delta specs from active changes live at
`openspec/changes/{change-name}/specs/{domain}/spec.md` and are merged into main specs on archive.

To seed initial specs, run `/sdd-new <change>` or manually create the first domain (e.g., `formatting`,
`cli`, `pipeline`) via `sdd-spec`.

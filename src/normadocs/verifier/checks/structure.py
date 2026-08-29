"""Document structure verification for a general APA academic report."""

from __future__ import annotations

import re
from itertools import pairwise
from typing import TYPE_CHECKING, Literal

from .. import CheckCategory, VerificationIssue
from ..docx_analyzer import DOCXParagraphInfo

if TYPE_CHECKING:
    from ..apa_verifier import VerificationContext

_HEADING_LEVEL_RE = re.compile(r"(?:heading|encabezado)\s*(\d+)\s*$", re.IGNORECASE)


Severity = Literal["error", "warning"]

INTRODUCTION_NAMES = frozenset({"introduccion", "introduction"})
ABSTRACT_NAMES = frozenset({"resumen", "abstract", "summary"})
CONCLUSION_NAMES = frozenset({"conclusion", "conclusiones", "conclusions"})
REFERENCE_NAMES = frozenset({"referencias", "references", "bibliografia", "bibliography"})
APPENDIX_PREFIXES = ("apendice", "apendices", "appendix", "appendices")
DEVELOPMENT_NAMES = frozenset(
    {
        "desarrollo",
        "development",
        "marco teorico",
        "theoretical framework",
        "analisis",
        "analysis",
        "metodo",
        "metodos",
        "method",
        "methods",
        "resultados",
        "results",
        "discusion",
        "discussion",
    }
)
KEYWORD_PREFIXES = ("palabras clave:", "keywords:")


class StructureCheck:
    """Check the required structure of a general academic APA report."""

    @staticmethod
    def _consume_digits(text: str, idx: int) -> int:
        while idx < len(text) and text[idx].isdigit():
            idx += 1
        return idx

    @staticmethod
    def _consume_dot_digits(text: str, idx: int) -> int:
        while idx < len(text) and text[idx] == ".":
            nxt = idx + 1
            if nxt < len(text) and text[nxt].isdigit():
                idx = StructureCheck._consume_digits(text, nxt + 1)
            else:
                break
        return idx

    @staticmethod
    def _strip_number_prefix(text: str) -> str:
        """Remove leading numbering like '1.', '1.2', '2) ' without super-linear regex."""
        stripped = text.strip()
        if not stripped or not stripped[0].isdigit():
            return stripped
        idx = StructureCheck._consume_digits(stripped, 0)
        idx = StructureCheck._consume_dot_digits(stripped, idx)
        if idx < len(stripped) and stripped[idx] in ".)":
            idx += 1
        while idx < len(stripped) and stripped[idx].isspace():
            idx += 1
        return stripped[idx:]

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize heading text for Spanish/English structural matching."""
        normalized = StructureCheck._strip_number_prefix(text.strip())
        normalized = normalized.casefold()
        replacements = str.maketrans("áéíóúüñ", "aeiouun")
        return normalized.translate(replacements)

    @staticmethod
    def _heading_level(style_name: str | None) -> int | None:
        """Extract an outline level from a Word heading style name."""
        if style_name is None:
            return None
        match = _HEADING_LEVEL_RE.search(style_name)
        return int(match.group(1)) if match else None

    @staticmethod
    def _severity(ctx: VerificationContext) -> Severity:
        """Use warnings only for explicitly non-strict compatibility reports."""
        return "error" if ctx.strict else "warning"

    def _issue(
        self,
        ctx: VerificationContext,
        check: str,
        expected: str,
        actual: str,
        evidence: str,
    ) -> VerificationIssue:
        """Create a structural issue with strict-mode severity."""
        return VerificationIssue(
            check=f"{CheckCategory.STRUCTURE}.{check}",
            severity=self._severity(ctx),
            expected=expected,
            actual=actual,
            evidence=evidence,
        )

    @staticmethod
    def _section_end(
        headings: list[tuple[int, DOCXParagraphInfo, int]], heading_position: int, total: int
    ) -> int:
        """Return the paragraph boundary immediately before the next heading."""
        for index, _, _ in headings:
            if index > heading_position:
                return index
        return total

    @staticmethod
    def _has_content(
        paragraphs: list[DOCXParagraphInfo], start: int, end: int, exclude_keywords: bool = False
    ) -> bool:
        """Return whether a section contains substantive non-empty paragraphs."""
        for paragraph in paragraphs[start:end]:
            text = paragraph.text.strip()
            if not text:
                continue
            if exclude_keywords and text.casefold().startswith(KEYWORD_PREFIXES):
                continue
            return True
        return False

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Validate report structure and section ordering."""
        paragraphs = ctx.docx.get_paragraphs_info()
        issues: list[VerificationIssue] = []
        nonempty = self._collect_nonempty(paragraphs)
        if not nonempty:
            return self._missing_content(issues, ctx)
        headings = self._collect_headings(nonempty)
        if not headings:
            return self._missing_headings(issues, ctx)
        self._check_title_heading(headings, ctx, issues)
        self._check_cover_content(headings, paragraphs, ctx, issues)
        self._check_body_content(headings, paragraphs, ctx, issues)
        self._check_heading_hierarchy(headings, ctx, issues)
        sections = self._collect_sections(headings)
        self._check_required_sections(sections, ctx, issues)
        self._check_section_levels(sections, ctx, issues)
        self._check_section_content(sections, headings, paragraphs, ctx, issues)
        self._check_abstract(sections, headings, paragraphs, ctx, issues)
        self._check_keywords(nonempty, sections, headings, paragraphs, ctx, issues)
        self._check_section_order(sections, ctx, issues)
        self._check_content_after_references(sections, headings, ctx, issues)
        return issues

    def _collect_nonempty(
        self, paragraphs: list[DOCXParagraphInfo]
    ) -> list[tuple[int, DOCXParagraphInfo]]:
        return [
            (index, paragraph)
            for index, paragraph in enumerate(paragraphs)
            if paragraph.text.strip()
        ]

    def _collect_headings(
        self, nonempty: list[tuple[int, DOCXParagraphInfo]]
    ) -> list[tuple[int, DOCXParagraphInfo, int]]:
        headings: list[tuple[int, DOCXParagraphInfo, int]] = []
        for index, paragraph in nonempty:
            level = self._heading_level(paragraph.style_name)
            if level is not None:
                headings.append((index, paragraph, level))
        return headings

    def _missing_content(
        self, issues: list[VerificationIssue], ctx: VerificationContext
    ) -> list[VerificationIssue]:
        issues.append(
            self._issue(
                ctx,
                "content_present",
                "A structured academic report",
                "No non-empty paragraphs",
                "The DOCX has no report content to validate",
            )
        )
        return issues

    def _missing_headings(
        self, issues: list[VerificationIssue], ctx: VerificationContext
    ) -> list[VerificationIssue]:
        issues.append(
            self._issue(
                ctx,
                "headings_present",
                "At least one Heading 1 for the report title and sections",
                "No heading-styled paragraphs found",
                "A report without structural headings cannot be validated as an APA report",
            )
        )
        return issues

    def _check_title_heading(
        self,
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        title = self._normalize(ctx.meta.title)
        _first_heading_index, first_heading, first_level = headings[0]
        if first_level != 1:
            issues.append(
                self._issue(
                    ctx,
                    "title_heading_level",
                    "The repeated title must be a level-1 heading",
                    f"Heading level {first_level}",
                    "The first structural heading is not a level-1 title",
                )
            )
        if self._normalize(first_heading.text) != title:
            issues.append(
                self._issue(
                    ctx,
                    "title_repeated",
                    f"First content heading exactly matching '{ctx.meta.title}'",
                    f"'{first_heading.text.strip()}'",
                    "The title-page title must be repeated before the report body",
                )
            )

    def _check_cover_content(
        self,
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        first_heading_index = headings[0][0]
        cover_lines = [
            paragraph.text.strip()
            for paragraph in paragraphs[:first_heading_index]
            if paragraph.text.strip()
        ]
        if len(cover_lines) >= 3:
            return
        issues.append(
            self._issue(
                ctx,
                "cover_content",
                "Cover with title, author, and an additional identification line",
                f"Only {len(cover_lines)} non-empty cover line(s)",
                "The report cover is incomplete before the repeated title",
            )
        )

    def _check_body_content(
        self,
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        first_heading_index = headings[0][0]
        if self._has_content(paragraphs, first_heading_index + 1, len(paragraphs)):
            return
        issues.append(
            self._issue(
                ctx,
                "body_content_present",
                "Substantive report content after the repeated title",
                "No content after the repeated title",
                "The document contains a title but no report body",
            )
        )

    def _check_heading_hierarchy(
        self,
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        previous_level = headings[0][2]
        for _, paragraph, level in headings[1:]:
            if level <= previous_level + 1:
                previous_level = level
                continue
            issues.append(
                self._issue(
                    ctx,
                    "heading_hierarchy",
                    f"Heading level no greater than {previous_level + 1}",
                    f"Heading {level}: '{paragraph.text.strip()}'",
                    "The report skips an intermediate heading level",
                )
            )
            previous_level = level

    def _collect_sections(
        self, headings: list[tuple[int, DOCXParagraphInfo, int]]
    ) -> dict[str, list[tuple[int, DOCXParagraphInfo, int]]]:
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]] = {
            "abstract": [],
            "introduction": [],
            "development": [],
            "conclusion": [],
            "references": [],
            "appendix": [],
        }
        for index, paragraph, level in headings[1:]:
            normalized = self._normalize(paragraph.text)
            self._assign_section(normalized, index, paragraph, level, sections)
        return sections

    def _assign_section(
        self,
        normalized: str,
        index: int,
        paragraph: DOCXParagraphInfo,
        level: int,
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
    ) -> None:
        if normalized in ABSTRACT_NAMES:
            sections["abstract"].append((index, paragraph, level))
        if normalized in INTRODUCTION_NAMES:
            sections["introduction"].append((index, paragraph, level))
        if normalized in CONCLUSION_NAMES:
            sections["conclusion"].append((index, paragraph, level))
        if normalized in REFERENCE_NAMES:
            sections["references"].append((index, paragraph, level))
        if normalized in DEVELOPMENT_NAMES:
            sections["development"].append((index, paragraph, level))
        if normalized.startswith(APPENDIX_PREFIXES):
            sections["appendix"].append((index, paragraph, level))

    def _check_required_sections(
        self,
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        for name in ("introduction", "development", "conclusion", "references"):
            if sections[name]:
                continue
            issues.append(
                self._issue(
                    ctx,
                    f"{name}_present",
                    f"A {name} section",
                    "Section not found",
                    f"The general academic report requires a {name} section",
                )
            )

    def _check_section_levels(
        self,
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        for name in ("introduction", "development", "conclusion", "references"):
            for _index, paragraph, level in sections[name]:
                if level == 1:
                    continue
                issues.append(
                    self._issue(
                        ctx,
                        f"{name}_level",
                        f"{name.title()} as a level-1 heading",
                        f"Heading {level}: '{paragraph.text.strip()}'",
                        "Main report sections must use level-1 headings",
                    )
                )

    def _check_section_content(
        self,
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        for name in ("introduction", "development", "conclusion"):
            if not sections[name]:
                continue
            index = sections[name][0][0]
            end = self._section_end(headings, index, len(paragraphs))
            if self._has_content(paragraphs, index + 1, end, exclude_keywords=True):
                continue
            issues.append(
                self._issue(
                    ctx,
                    f"{name}_content",
                    f"Substantive content inside the {name} section",
                    "Section has no non-empty body paragraph",
                    f"The {name} heading is present but contains no content",
                )
            )

    def _check_abstract(
        self,
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        if not sections["abstract"]:
            return
        abstract_index = sections["abstract"][0][0]
        abstract_end = self._section_end(headings, abstract_index, len(paragraphs))
        abstract_words = sum(
            len(paragraph.text.split())
            for paragraph in paragraphs[abstract_index + 1 : abstract_end]
        )
        if abstract_words > 250:
            issues.append(
                self._issue(
                    ctx,
                    "abstract_length",
                    "Abstract no longer than 250 words",
                    f"{abstract_words} words",
                    "APA 7 student abstracts should be concise",
                )
            )
        intro_index = sections["introduction"][0][0] if sections["introduction"] else None
        if intro_index is not None and abstract_index > intro_index:
            issues.append(
                self._issue(
                    ctx,
                    "abstract_order",
                    "Abstract before Introduction",
                    "Abstract appears after Introduction",
                    "The abstract belongs before the report body",
                )
            )

    def _check_keywords(
        self,
        nonempty: list[tuple[int, DOCXParagraphInfo]],
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        paragraphs: list[DOCXParagraphInfo],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        keyword_indexes = [
            index
            for index, paragraph in nonempty
            if paragraph.text.strip().casefold().startswith(KEYWORD_PREFIXES)
        ]
        if not keyword_indexes:
            return
        if not sections["abstract"]:
            issues.append(
                self._issue(
                    ctx,
                    "keywords_without_abstract",
                    "Keywords only when an abstract is present",
                    "Keywords found without Abstract/Resumen",
                    "Keywords must belong to the abstract block",
                )
            )
            return
        abstract_index = sections["abstract"][0][0]
        abstract_end = self._section_end(headings, abstract_index, len(paragraphs))
        if all(abstract_index < index < abstract_end for index in keyword_indexes):
            return
        issues.append(
            self._issue(
                ctx,
                "keywords_order",
                "Keywords inside the abstract block",
                "Keywords outside the abstract block",
                "Keywords must immediately follow the abstract text",
            )
        )

    def _check_section_order(
        self,
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        ordered_sections = [(name, entries[0][0]) for name, entries in sections.items() if entries]
        for (left_name, left_index), (right_name, right_index) in pairwise(ordered_sections):
            if left_index <= right_index:
                continue
            issues.append(
                self._issue(
                    ctx,
                    "section_order",
                    "Introduction, development, conclusions, references, appendices",
                    f"{left_name} appears after {right_name}",
                    "The report sections are not in APA academic order",
                )
            )

    def _check_content_after_references(
        self,
        sections: dict[str, list[tuple[int, DOCXParagraphInfo, int]]],
        headings: list[tuple[int, DOCXParagraphInfo, int]],
        ctx: VerificationContext,
        issues: list[VerificationIssue],
    ) -> None:
        if not sections["references"]:
            return
        references_index = sections["references"][0][0]
        for index, paragraph, _ in headings:
            if index <= references_index:
                continue
            normalized = self._normalize(paragraph.text)
            if normalized.startswith(APPENDIX_PREFIXES):
                continue
            issues.append(
                self._issue(
                    ctx,
                    "content_after_references",
                    "Only appendices after References",
                    f"Heading after References: '{paragraph.text.strip()}'",
                    "References must close the main report body",
                )
            )
            break

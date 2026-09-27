"""
Configuration constants for APA Engine.
"""

from pathlib import Path

# Raw OpenXML page break for Pandoc integration
PAGEBREAK_OPENXML = """
```{=openxml}
<w:p>
  <w:r>
    <w:br w:type="page"/>
  </w:r>
</w:p>
```
"""

# Default output directory
DEFAULT_OUTPUT_DIR = Path("ExportDocs")

# Default body font for the academic standards (APA 7, ICONTEC, IEEE)
DEFAULT_BODY_FONT = "Times New Roman"

# Headings that must start on a new page (APA 7: references and appendices).
# Body sections flow continuously; only these break the page.
SECTION_BREAK_HEADINGS = frozenset(
    {
        "referencias",
        "references",
        "bibliografia",
        "bibliography",
        "lista de referencias",
        "apendice",
        "apendices",
        "appendix",
        "appendices",
    }
)

_ACCENTS = str.maketrans("áéíóúüñ", "aeiouun")


def normalize_heading(text: str) -> str:
    """Normalize a heading for structural matching (case/accents/numbering)."""
    return text.strip().casefold().translate(_ACCENTS)


def is_section_break_heading(text: str) -> bool:
    """Return whether a heading must start on a new page."""
    normalized = normalize_heading(text)
    return any(
        normalized == entry or normalized.startswith(f"{entry} ")
        for entry in SECTION_BREAK_HEADINGS
    )


# Metadata field order for positional fallback extraction (legacy layout).
# New fields (subject, subject_code) are appended so existing documents
# without YAML frontmatter keep their meaning; prefer frontmatter.
METADATA_FIELDS = [
    "author",
    "program",
    "ficha",
    "institution",
    "center",
    "instructor",
    "date",
    "subject",
    "subject_code",
]

# Centralized OpenXML attribute constants (S1192)
W_VAL = "w:val"
W_TYPE = "w:type"
W_SPACING = "w:spacing"
W_LINE = "w:line"
W_LINE_RULE = "w:lineRule"
W_AFTER = "w:after"
W_BEFORE = "w:before"
W_JC = "w:jc"
W_IND = "w:ind"

# Centralized style name constants (S1192)
HEADING_1_STYLE = "Heading 1"
HEADING_2_STYLE = "Heading 2"
HEADING_3_STYLE = "Heading 3"
HEADING_4_STYLE = "Heading 4"
HEADING_5_STYLE = "Heading 5"
NORMAL_STYLE = "Normal"
BODY_TEXT_STYLE = "Body Text"
COMPACT_STYLE = "Compact"

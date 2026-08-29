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

# Metadata field order for extraction
METADATA_FIELDS = ["author", "program", "ficha", "institution", "center", "instructor", "date"]

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

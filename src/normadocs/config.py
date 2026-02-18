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

# Metadata field order for extraction
METADATA_FIELDS = ["author", "program", "ficha", "institution", "center", "date"]

"""
NormaDocs - Markdown to academic DOCX/PDF converter (APA 7th, ICONTEC, IEEE).
"""

__version__ = "0.2.0"

from .converter import Converter
from .exceptions import NormaDocsError

__all__ = ["Converter", "NormaDocsError"]

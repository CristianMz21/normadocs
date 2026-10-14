"""
NormaDocs - Markdown to academic DOCX/PDF converter (APA 7th, ICONTEC, IEEE).
"""

from importlib.metadata import PackageNotFoundError, version

from .converter import Converter
from .exceptions import NormaDocsError

try:
    __version__ = version("normadocs")
except PackageNotFoundError:
    __version__ = "0.3.2"

__all__ = ["Converter", "NormaDocsError", "__version__"]

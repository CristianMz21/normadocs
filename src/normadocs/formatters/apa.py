"""APA 7th Edition formatter - backward compatibility module.

This module exists for backward compatibility. The actual implementation
has been moved to the apa/ subpackage.
"""

from normadocs.formatters.apa import APADocxFormatter

__all__ = ["APADocxFormatter"]

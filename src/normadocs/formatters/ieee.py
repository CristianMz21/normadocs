"""
IEEE formatter placeholder.

This module provides a placeholder implementation for IEEE citation style.
Full implementation coming soon.
"""

from typing import Any

from ..models import DocumentMetadata
from .base import DocumentFormatter


class IEEEDocxFormatter(DocumentFormatter):
    """
    Placeholder for IEEE formatting.

    TODO: Implement IEEE 8th Edition formatting.
    """

    def __init__(self, doc_path: str, config: dict[str, Any] | None = None):
        super().__init__(doc_path, config)

    def process(self, meta: DocumentMetadata) -> None:
        """Apply IEEE formatting (not yet implemented)."""
        raise NotImplementedError(
            "IEEE formatter is not yet implemented. Please use 'apa' or 'icontec' for now."
        )

    def save(self, output_path: str) -> None:
        """Save the formatted document."""
        self.doc.save(str(output_path))

"""Abstract base class for document formatters.

All formatters (APA, ICONTEC, IEEE) inherit from this class and implement
the process() and save() methods.
"""

from abc import ABC, abstractmethod
from typing import Any

from docx import Document
from docx.table import Table

from ..models import DocumentMetadata


class DocumentFormatter(ABC):
    """Abstract base class for all document formatters (APA, ICONTEC, IEEE)."""

    def __init__(self, doc_path: str, config: dict[str, Any] | None = None) -> None:
        """Initialize DocumentFormatter.

        Args:
            doc_path: Path to the DOCX file to format.
            config: Optional configuration dictionary.
        """
        self.doc_path = doc_path
        self.doc = Document(doc_path)
        self.config = config if config is not None else {}

    def get_config(self, *keys: str, default: Any = None) -> Any:
        """Get a nested config value using dot notation keys.

        Example:
            self.get_config("fonts", "body", "name", default="Times New Roman")
        """
        value: Any = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    @abstractmethod
    def process(self, meta: DocumentMetadata) -> None:
        """Apply all formatting rules to the document."""
        pass

    @abstractmethod
    def save(self, output_path: str) -> None:
        """Save the formatted document."""
        pass

    def _format_table_caption(self, table: Table, number: int, title: str) -> None:
        """Format table caption (Table X + Title). Optional override for subclasses."""
        raise NotImplementedError(f"Caption formatting not implemented for {type(self).__name__}")

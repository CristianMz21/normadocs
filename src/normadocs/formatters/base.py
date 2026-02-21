from abc import ABC, abstractmethod

from docx import Document

from ..models import DocumentMetadata


class DocumentFormatter(ABC):
    """Abstract base class for all document formatters (APA, ICONTEC, IEEE)."""

    def __init__(self, doc_path: str):
        self.doc_path = doc_path
        self.doc = Document(doc_path)

    @abstractmethod
    def process(self, meta: DocumentMetadata) -> None:
        """Apply all formatting rules to the document."""
        pass

    @abstractmethod
    def save(self, output_path: str) -> None:
        """Save the formatted document."""
        pass

    def _format_table_caption(self, table, number: int, title: str):  # noqa: B027
        """Format table caption (Table X + Title). Optional override for subclasses."""

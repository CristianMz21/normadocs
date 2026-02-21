"""
Data models for APA Document processing.
"""

from dataclasses import dataclass, field


@dataclass
class DocumentMetadata:
    """Holds metadata extracted from the source Markdown."""

    title: str = "Sin Título"
    author: str | None = None
    program: str | None = None
    ficha: str | None = None
    institution: str | None = None
    center: str | None = None
    date: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "DocumentMetadata":
        """Create instance from a dictionary, handling known fields."""
        known_fields = {
            "title",
            "author",
            "program",
            "ficha",
            "institution",
            "center",
            "date",
        }
        known_data = {k: v for k, v in data.items() if k in known_fields}
        extra_data = {k: v for k, v in data.items() if k not in known_fields}

        return cls(**known_data, extra=extra_data)


@dataclass
class ProcessOptions:
    """Configuration options for the conversion process."""

    input_file: str
    output_dir: str
    output_format: str = "docx"  # docx, pdf, all

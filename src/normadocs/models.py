"""
Data models for APA Document processing.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DocumentMetadata:
    """Holds metadata extracted from the source Markdown."""

    title: str = "Sin Título"
    subtitle: str | None = None
    author: str | None = None
    affiliation: str | None = None
    program: str | None = None
    ficha: str | None = None
    institution: str | None = None
    center: str | None = None
    instructor: str | None = None
    subject: str | None = None
    location: str | None = None
    date: str | None = None
    short_title: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "DocumentMetadata":
        """Create instance from a dictionary, handling known fields."""
        known_fields = {
            "title",
            "subtitle",
            "author",
            "affiliation",
            "program",
            "ficha",
            "institution",
            "center",
            "instructor",
            "subject",
            "location",
            "date",
            "short_title",
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


@dataclass(frozen=True, slots=True)
class ConvertOptions:
    """Collapsed CLI options to fix S107 (21→2)."""

    output_dir: Path = Path("ExportDocs")
    format: str = "docx"
    style: str = "apa7estudiante"
    bibliography: str | None = None
    csl: str | None = None
    language_tool: str | None = None
    lt_host: str = "localhost"
    lt_port: int = 8081
    lt_stop_on_error: bool = True
    lt_docker: bool = False
    lt_keep_alive: bool = False
    lt_report: Path | None = None
    lt_enabled_rules: str | None = None
    lt_disabled_rules: str | None = None
    lt_ignore_words: str | None = None
    lt_strict: bool = False
    lt_no_spelling: bool = False
    verify_apa: bool = True
    apa_strict: bool = True
    apa_report: Path | None = None

class NormaDocsError(Exception):
    """Base exception for all normadocs errors."""

    pass


class ConversionError(NormaDocsError):
    """Raised when document conversion fails (e.g. pandoc, formatter)."""

    pass


class DependencyError(NormaDocsError):
    """Raised when a required dependency is missing."""

    pass


class LanguageToolError(NormaDocsError):
    """Raised when LanguageTool check fails."""

    pass


class ValidationError(NormaDocsError):
    """Raised when inputs or arguments are invalid."""

    pass

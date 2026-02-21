from .apa import APADocxFormatter
from .base import DocumentFormatter
from .icontec import IcontecFormatter


def get_formatter(style: str = "apa", doc_path: str = "") -> DocumentFormatter:
    """
    Factory to get the appropriate formatter.

    Args:
        style: The citation style ('apa', 'icontec', 'ieee').
        doc_path: Path to the DOCX file to format.

    Returns:
        An instance of a DocumentFormatter subclass.
    """
    style = style.lower()
    if style == "apa":
        return APADocxFormatter(doc_path)
    elif style == "icontec":
        return IcontecFormatter(doc_path)
    else:
        # Fallback to APA or raise error? For now, default/fallback is APA if unknown
        # or raise ValueError. Let's raise for clarity.
        raise ValueError(f"Unsupported style: {style}. Available: apa, icontec")

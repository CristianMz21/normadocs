"""
Formatter factory with YAML-based standard support.
"""

from typing import Any

from ..standards import StandardLoader, get_default_config, merge_with_defaults
from .apa import APADocxFormatter
from .base import DocumentFormatter  # noqa: F401
from .icontec import IcontecFormatter
from .ieee import IEEEDocxFormatter


def get_formatter(
    style: str = "apa",
    doc_path: str = "",
    config: dict[str, Any] | None = None,
) -> APADocxFormatter | IcontecFormatter | IEEEDocxFormatter:
    """
    Factory to get the appropriate formatter with YAML config.

    Args:
        style: The citation style ('apa', 'icontec', 'ieee').
        doc_path: Path to the DOCX file to format.
        config: Optional config dict to override YAML defaults.

    Returns:
        An instance of a DocumentFormatter subclass.
    """
    style = style.lower()
    loader = StandardLoader()

    try:
        yaml_config = loader.load(style)
    except FileNotFoundError:
        yaml_config = get_default_config(style)

    if config is not None:
        final_config = merge_with_defaults(config, style)
        deep_merge(yaml_config, config)
    else:
        final_config = yaml_config

    if style in ("apa", "apa7"):
        return APADocxFormatter(doc_path, final_config)
    elif style == "icontec":
        return IcontecFormatter(doc_path, final_config)
    elif style == "ieee":
        return IEEEDocxFormatter(doc_path, final_config)
    else:
        raise ValueError(f"Unsupported style: {style}. Available: apa, icontec, ieee")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Recursively merge override into base dict (in-place)."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value


def load_standard_config(style: str) -> dict[str, Any]:
    """
    Load citation standard configuration from YAML file, merged with defaults.

    Args:
        style: The citation style name (e.g., 'apa7', 'icontec').

    Returns:
        Dictionary containing the merged standard configuration.
    """
    loader = StandardLoader()
    return loader.load(style)


def list_available_standards() -> list[str]:
    """List all available citation standard names."""
    loader = StandardLoader()
    return loader.list_available()

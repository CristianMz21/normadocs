"""
Configuration schema for citation standards.

Defines the structure and default values for all supported standards.
"""

from typing import Any, cast

DEFAULT_APA7_CONFIG: dict[str, Any] = {
    "name": "APA 7th Edition",
    "version": "7.0",
    "citation_style": "apa",
    "fonts": {
        "body": {"name": "Times New Roman", "size": 12},
        "headings": {
            "name": "Times New Roman",
            "level1": {"alignment": "center", "bold": True},
            "level2": {"alignment": "left", "bold": True},
            "level3": {"alignment": "left", "bold": True, "italic": True},
            "level4": {"alignment": "left", "bold": True},
            "level5": {"alignment": "left", "bold": True, "italic": True},
        },
    },
    "margins": {"unit": "inches", "top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
    "spacing": {"line": "double", "paragraph_before": 0, "paragraph_after": 0},
    "page_setup": {"page_numbers": True, "header": True, "first_page_number": 1},
    "citations": {"et_al_min_authors": 3, "ampersand": True},
    "block_quote": {"min_words": 40, "indent_inches": 0.5},
    "references": {"sort": True, "italicize_journals": True},
    "tables": {
        "borders": "horizontal_only",
        "caption_prefix": "Table",
        "caption_above": True,
        "note_suffix": "Elaboración propia.",
        "vertical_align": "top",
    },
    "figures": {
        "caption_prefix": "Figure",
        "caption_above": True,
        "title_above": True,
        "nota_prefix": "Note.",
    },
    "cover": {
        "title_align": "center",
        "author_align": "center",
    },
}


DEFAULT_ICONTEC_CONFIG: dict[str, Any] = {
    "name": "ICONTEC (NTC 1486)",
    "version": "1.0",
    "citation_style": "icontec",
    "fonts": {
        "body": {"name": "Arial", "size": 12},
        "headings": {
            "name": "Arial",
            "level1": {"alignment": "center", "bold": True, "uppercase": True},
        },
    },
    "margins": {"unit": "cm", "top": 3.0, "bottom": 2.0, "left": 3.0, "right": 2.0},
    "spacing": {"line": 1.5, "paragraph_before": 0, "paragraph_after": 0},
    "page_setup": {"page_numbers": True, "header": False, "first_page_number": 1},
    "tables": {
        "borders": "full",
        "caption_prefix": "Tabla",
        "caption_above": True,
    },
    "figures": {
        "caption_prefix": "Figura",
    },
    "cover": {
        "title_align": "center",
        "author_align": "center",
    },
}


DEFAULT_IEEE_CONFIG: dict[str, Any] = {
    "name": "IEEE 8th Edition",
    "version": "8.0",
    "citation_style": "ieee",
    "fonts": {
        "body": {"name": "Times New Roman", "size": 10},
        "headings": {
            "name": "Times New Roman",
            "level1": {"alignment": "center", "bold": True},
        },
    },
    "margins": {"unit": "inches", "top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
    "spacing": {"line": "single", "paragraph_before": 0, "paragraph_after": 0},
    "page_setup": {"page_numbers": True, "header": False, "first_page_number": 1},
    "tables": {
        "borders": "full",
        "caption_prefix": "Table",
        "caption_above": True,
    },
    "figures": {
        "caption_prefix": "Fig",
        "title_above": True,
    },
    "cover": {
        "title_align": "center",
        "author_align": "left",
    },
}


def get_default_config(style: str) -> dict[str, Any]:
    """Get the default configuration for a given style.

    Student APA papers differ from professional papers because they omit the
    running-head text by default. Keep that profile explicit so it remains
    correct even if its YAML file is unavailable in a fallback installation.

    Args:
        style: The style name (e.g., "apa", "apa7", "apa7estudiante").

    Returns:
        A dictionary containing the merged standard defaults.
    """
    style_lower = style.lower()
    if style_lower == "apa7estudiante":
        student_config = deep_copy(DEFAULT_APA7_CONFIG)
        student_config["running_head"] = {"enabled": False, "max_length": 50}
        return cast(dict[str, Any], student_config)

    defaults = {
        "apa": DEFAULT_APA7_CONFIG,
        "apa7": DEFAULT_APA7_CONFIG,
        "icontec": DEFAULT_ICONTEC_CONFIG,
        "ieee": DEFAULT_IEEE_CONFIG,
    }
    return defaults.get(style_lower, DEFAULT_APA7_CONFIG)


def merge_with_defaults(config: dict[str, Any], style: str) -> dict[str, Any]:
    """Merge user configuration with defaults for the given style.

    Args:
        config: User-provided configuration dictionary.
        style: The style name for defaults lookup.

    Returns:
        The merged configuration dictionary with user values overriding defaults.
    """
    defaults = get_default_config(style)
    result = cast(dict[str, Any], deep_copy(defaults))
    deep_merge(result, config)
    return result


def deep_copy(obj: Any) -> Any:
    """Create a deep copy of an object.

    Args:
        obj: The object to copy.

    Returns:
        A deep copy of the object.
    """
    if not isinstance(obj, dict):
        return obj
    result = {}
    for key, value in obj.items():
        if isinstance(value, dict):
            result[key] = deep_copy(value)
        else:
            result[key] = value
    return result


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base dictionary.

    Args:
        base: The base dictionary to merge into.
        override: The override dictionary.

    Returns:
        The merged dictionary.
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

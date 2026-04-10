"""Citation standards configuration module with YAML-based standards."""

from pathlib import Path
from typing import Any

import yaml

from .schema import get_default_config, merge_with_defaults

_STANDARDS_DIR = Path(__file__).parent


def _load_yaml(name: str) -> dict[str, Any]:
    """Load a YAML standard configuration file."""
    path = _STANDARDS_DIR / f"{name}.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_style_key(style: str) -> str:
    """Normalize style name to match YAML file naming."""
    style_lower = style.lower()
    if style_lower in ("apa", "apa7"):
        return "apa7"
    return style_lower


APA7_CONFIG = _load_yaml("apa7")
ICONTEC_CONFIG = _load_yaml("icontec")
IEEE_CONFIG = _load_yaml("ieee")


class StandardLoader:
    """Loads and validates citation standard configurations from YAML files."""

    def __init__(self, standards_dir: Path | None = None):
        if standards_dir is None:
            standards_dir = Path(__file__).parent
        self.standards_dir = standards_dir

    def load(self, name: str) -> dict[str, Any]:
        """Load a standard configuration by name, merged with defaults."""
        key = _get_style_key(name)
        path = self.standards_dir / f"{key}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Standard '{name}' not found at {path}")
        with open(path, encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)
        return merge_with_defaults(yaml_config, key)

    def load_raw(self, name: str) -> dict[str, Any]:
        """Load raw YAML config without merging defaults."""
        key = _get_style_key(name)
        path = self.standards_dir / f"{key}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Standard '{name}' not found at {path}")
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def list_available(self) -> list[str]:
        """List all available standard names."""
        return [p.stem for p in self.standards_dir.glob("*.yaml")]

    def exists(self, name: str) -> bool:
        """Check if a standard exists."""
        key = _get_style_key(name)
        return (self.standards_dir / f"{key}.yaml").exists()


__all__ = [
    "APA7_CONFIG",
    "ICONTEC_CONFIG",
    "IEEE_CONFIG",
    "StandardLoader",
    "get_default_config",
    "merge_with_defaults",
]

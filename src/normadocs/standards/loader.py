"""
Standard loader for YAML-based configuration.
"""

from pathlib import Path
from typing import Any

import yaml


class StandardLoader:
    """Loads and validates citation standard configurations from YAML files."""

    def __init__(self, standards_dir: Path | None = None):
        if standards_dir is None:
            standards_dir = Path(__file__).parent
        self.standards_dir = standards_dir

    def load(self, name: str) -> dict[str, Any]:
        """Load a standard configuration by name."""
        path = self.standards_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Standard '{name}' not found at {path}")
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def list_available(self) -> list[str]:
        """List all available standard names."""
        return [p.stem for p in self.standards_dir.glob("*.yaml")]

    def exists(self, name: str) -> bool:
        """Check if a standard exists."""
        return (self.standards_dir / f"{name}.yaml").exists()

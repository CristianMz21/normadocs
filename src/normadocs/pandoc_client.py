"""
Module for running Pandoc conversions.
"""

import subprocess
import tempfile
import sys
from pathlib import Path


class PandocRunner:
    """Encapsulates Pandoc execution logic."""

    def __init__(self, pandoc_path: str = "pandoc"):
        self.pandoc_path = pandoc_path

    def run(self, md_text: str, output_path: str) -> bool:
        """
        Run pandoc to convert Markdown to DOCX.
        Returns True if successful, False otherwise.
        """
        path_obj = Path(output_path)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(md_text)
            tmp_path = tmp.name

        cmd = [
            self.pandoc_path,
            tmp_path,
            "-f",
            "markdown+raw_attribute",
            "-t",
            "docx",
            "-o",
            str(path_obj.absolute()),
            "--standalone",
        ]

        print(f"  ▸ Ejecutando Pandoc -> {path_obj.name}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            Path(tmp_path).unlink(missing_ok=True)

            if result.returncode != 0:
                print(f"  ✗ Error de Pandoc:\n{result.stderr}", file=sys.stderr)
                return False

            return True

        except FileNotFoundError:
            print("  ✗ Error: Pandoc no encontrado en el sistema.", file=sys.stderr)
            Path(tmp_path).unlink(missing_ok=True)
            return False

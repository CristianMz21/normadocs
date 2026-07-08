"""
Module for running Pandoc conversions.
"""

import platform
import sys
import tempfile
from pathlib import Path

from .utils.subprocess import CommandFailedError, get_command_path, run_command


def _print_pandoc_missing_error() -> None:
    """Print a friendly, actionable error when Pandoc is not installed."""
    system = platform.system()
    if system == "Darwin":
        hint = "brew install pandoc"
    elif system == "Linux":
        hint = "sudo apt install pandoc  (or use your distro's package manager)"
    elif system == "Windows":
        hint = "choco install pandoc  (or see the link below)"
    else:
        hint = "see the link below"

    print("  ✗ Error: Pandoc no está instalado en el sistema.", file=sys.stderr)
    print(f"    Instálalo con: {hint}", file=sys.stderr)
    print("    Más info: https://pandoc.org/installing.html", file=sys.stderr)


class PandocRunner:
    """Encapsulates Pandoc execution logic."""

    def __init__(self, pandoc_path: str = "pandoc") -> None:
        """Initialize PandocRunner.

        Args:
            pandoc_path: Path to Pandoc executable. Defaults to "pandoc".
        """
        self.pandoc_path = pandoc_path

    def run(
        self,
        md_text: str,
        output_path: str,
        bibliography: str | None = None,
        csl: str | None = None,
        resource_path: str | None = None,
    ) -> bool:
        """Convert Markdown to DOCX using Pandoc.

        Args:
            md_text: The Markdown content to convert.
            output_path: Path for the output DOCX file.
            bibliography: Optional BibTeX file for citations.
            csl: Optional CSL style file for citation formatting.
            resource_path: Optional path for image resources.

        Returns:
            True if conversion succeeded, False otherwise.

        Raises:
            FileNotFoundError: If Pandoc executable is not found.
            CommandFailedError: If Pandoc returns a non-zero exit code.
        """
        if "/" in self.pandoc_path:
            resolved_path = self.pandoc_path
        else:
            try:
                resolved_path = get_command_path(self.pandoc_path)
            except FileNotFoundError:
                _print_pandoc_missing_error()
                return False

        path_obj = Path(output_path)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(md_text)
            tmp_path = tmp.name

        cmd = [
            resolved_path,
            tmp_path,
            "-f",
            "markdown+raw_attribute",
            "-t",
            "docx",
            "-o",
            str(path_obj.absolute()),
            "--standalone",
        ]

        if resource_path:
            cmd.extend([f"--resource-path={resource_path}"])

        if bibliography:
            cmd.extend([f"--bibliography={bibliography}", "--citeproc"])

        if csl:
            cmd.extend([f"--csl={csl}"])

        print(f"  ▸ Ejecutando Pandoc -> {path_obj.name}")

        try:
            run_command(cmd)
            Path(tmp_path).unlink(missing_ok=True)
            return True

        except CommandFailedError as e:
            print(f"  ✗ Error de Pandoc:\n{e.stderr}", file=sys.stderr)
            Path(tmp_path).unlink(missing_ok=True)
            return False

        except FileNotFoundError:
            _print_pandoc_missing_error()
            Path(tmp_path).unlink(missing_ok=True)
            return False

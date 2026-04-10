"""
Command Line Interface for APA Engine.
"""

import logging
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from docx import Document

from . import cli_helpers
from .config import DEFAULT_OUTPUT_DIR
from .formatters import get_formatter
from .languagetool_client import LanguageToolClient, format_errors
from .pandoc_client import PandocRunner
from .pdf_generator import PDFGenerator
from .preprocessor import MarkdownPreprocessor

# Re-export for backward compatibility with existing tests that patch these
__all__ = [
    "Document",
    "LanguageToolClient",
    "MarkdownPreprocessor",
    "PDFGenerator",
    "PandocRunner",
    "format_errors",
    "get_formatter",
    "subprocess",
]

logger = logging.getLogger("normadocs")

app = typer.Typer(
    help="NormaDocs: Convert Markdown to APA 7th, ICONTEC, or IEEE formatted DOCX/PDF."
)


def get_default_ignored_words() -> list[str]:
    """Load default ignored words from config file."""
    config_path = Path(__file__).parent / "config" / "lt_ignore_words.txt"
    if config_path.exists():
        words = config_path.read_text(encoding="utf-8").strip().split("\n")
        return [w.strip() for w in words if w.strip() and not w.startswith("#")]
    return []


DEFAULT_LT_IGNORE_WORDS = get_default_ignored_words()


@app.command()
def convert(
    input_file: Annotated[
        Path, typer.Argument(help="Input Markdown file", exists=True, readable=True)
    ],
    output_dir: Annotated[
        Path, typer.Option("--output-dir", "-o", help="Directory for output files")
    ] = DEFAULT_OUTPUT_DIR,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: docx, pdf, or all")
    ] = "docx",
    style: Annotated[
        str, typer.Option("--style", "-s", help="Citation style: apa, icontec")
    ] = "apa",
    bibliography: Annotated[
        str | None, typer.Option("--bibliography", "-b", help="Path to bibliography file (.bib)")
    ] = None,
    csl: Annotated[str | None, typer.Option("--csl", "-c", help="Path to CSL style file")] = None,
    language_tool: Annotated[
        str | None,
        typer.Option(
            "--language-tool",
            "-lt",
            help="Language for LanguageTool checking (e.g., es, en, fr). Enables pre and post conversion checks.",
        ),
    ] = None,
    lt_host: Annotated[
        str, typer.Option("--lt-host", help="LanguageTool server host")
    ] = "localhost",
    lt_port: Annotated[int, typer.Option("--lt-port", help="LanguageTool server port")] = 8081,
    lt_stop_on_error: Annotated[
        bool,
        typer.Option(
            "--lt-stop-on-error/--lt-continue-on-error",
            help="Stop or continue if LanguageTool finds errors",
        ),
    ] = True,
    lt_docker: Annotated[
        bool,
        typer.Option(
            "--lt-docker",
            help="Start LanguageTool container automatically using Docker (uses port 8010)",
        ),
    ] = False,
    lt_keep_alive: Annotated[
        bool,
        typer.Option(
            "--lt-keep-alive",
            help="Keep LanguageTool container running after conversion (for faster subsequent runs)",
        ),
    ] = False,
    lt_report: Annotated[
        Path | None,
        typer.Option(
            "--lt-report",
            help="Save LanguageTool errors to a report file (Markdown format) for later review",
        ),
    ] = None,
    lt_enabled_rules: Annotated[
        str | None,
        typer.Option(
            "--lt-enabled-rules",
            help="Comma-separated list of rule IDs to enable (e.g., MISC_SPELLING,GRAMMAR)",
        ),
    ] = None,
    lt_disabled_rules: Annotated[
        str | None,
        typer.Option(
            "--lt-disabled-rules",
            help="Comma-separated list of rule IDs to disable (e.g., WHITESPACE_RULE,UPPERCASE_SENTENCE_START)",
        ),
    ] = None,
    lt_ignore_words: Annotated[
        str | None,
        typer.Option(
            "--lt-ignore-words",
            help="Comma-separated list of words to ignore. Default: uses config file (empty to disable)",
        ),
    ] = None,
    lt_strict: Annotated[
        bool,
        typer.Option(
            "--lt-strict",
            help="Fail if LanguageTool finds any errors (implies --lt-stop-on-error)",
        ),
    ] = False,
    lt_no_spelling: Annotated[
        bool,
        typer.Option(
            "--lt-no-spelling",
            help="Disable spell checking (useful for technical documents with many technical terms)",
        ),
    ] = False,
):
    """
    Convert a Markdown file to DOCX/PDF with specific citation style.
    """
    input_path = Path(input_file)
    if not input_path.exists():
        typer.echo(f"Error: El archivo {input_file} no existe.", err=True)
        raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # --lt-strict implies --lt-stop-on-error
    if lt_strict:
        lt_stop_on_error = True

    # Docker image erikvl87/languagetool uses port 8010 by default
    if lt_docker and lt_port == 8081:
        lt_port = 8010

    logger.info("▸ Procesando %s ...", input_file)

    # 1. Preprocess markdown
    clean_md, meta = cli_helpers.process_markdown(input_path)

    # Trackers for errors and docker container
    all_errors: list[tuple[str, list]] = []
    docker_container: str | None = None

    # 2. LanguageTool pre-check
    if language_tool:
        lt_client = cli_helpers._setup_languagetool_client(
            language_tool=language_tool,
            lt_host=lt_host,
            lt_port=lt_port,
            lt_enabled_rules=lt_enabled_rules,
            lt_disabled_rules=lt_disabled_rules,
            lt_ignore_words=lt_ignore_words,
            lt_no_spelling=lt_no_spelling,
            default_ignore_words=DEFAULT_LT_IGNORE_WORDS,
        )
        if lt_client:
            docker_container = cli_helpers._ensure_languagetool_server(
                lt_client, lt_docker, lt_port
            )
            if not cli_helpers._run_languagetool_precheck(
                lt_client, clean_md, lt_stop_on_error, all_errors
            ):
                cli_helpers._cleanup_docker(docker_container, lt_keep_alive, lt_port)
                raise typer.Exit(code=1)

    # 3. Pandoc conversion
    suffix = f"_{style.upper()}"
    output_docx = output_dir / f"{input_path.stem}{suffix}.docx"
    output_pdf = output_dir / f"{input_path.stem}{suffix}.pdf"

    if not cli_helpers._run_pandoc(clean_md, output_docx, bibliography, csl, input_path):
        cli_helpers._cleanup_docker(docker_container, lt_keep_alive, lt_port)
        raise typer.Exit(code=1)

    # 4. LanguageTool post-check
    if (
        language_tool
        and lt_client
        and not cli_helpers._run_languagetool_postcheck(
            lt_client, output_docx, lt_stop_on_error, all_errors
        )
    ):
        cli_helpers._cleanup_docker(docker_container, lt_keep_alive, lt_port)
        raise typer.Exit(code=1)

    # 5. Apply formatting
    logger.info("▸ Aplicando formato %s ...", style.upper())
    cli_helpers._apply_formatting(style, output_docx, meta)
    logger.info("✔ Generado con éxito: %s", output_docx.name)

    # 6. PDF generation
    cli_helpers._generate_pdf(format, output_docx, output_dir, clean_md, output_pdf)

    # 7. Cleanup Docker container (always runs, even on errors)
    cli_helpers._cleanup_docker(docker_container, lt_keep_alive, lt_port)

    # 8. Write LanguageTool report
    cli_helpers._write_lt_report(lt_report, all_errors, input_path, language_tool)

    logger.info("\nDone!")


if __name__ == "__main__":
    app()

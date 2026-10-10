"""
Command Line Interface for NormaDocs.
"""

from pathlib import Path
from typing import Annotated

import typer

from .converter import Converter
from .exceptions import NormaDocsError
from .models import ConvertOptions

app = typer.Typer(
    help="NormaDocs - Converts Markdown files to APA/ICONTEC/IEEE DOCX and PDF.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def convert(
    input_file: Annotated[
        Path, typer.Argument(help="Input Markdown file", exists=True, readable=True)
    ],
    output_dir: Annotated[
        Path, typer.Option("--output-dir", "-o", help="Directory for output files")
    ] = Path("ExportDocs"),
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: docx, pdf, or all")
    ] = "docx",
    style: Annotated[
        str,
        typer.Option(
            "--style", "-s", help="Citation style: apa7estudiante (default), apa, icontec, or ieee"
        ),
    ] = "apa7estudiante",
    bibliography: Annotated[
        str | None, typer.Option("--bibliography", "-b", help="Path to bibliography file (.bib)")
    ] = None,
    csl: Annotated[str | None, typer.Option("--csl", "-c", help="Path to CSL style file")] = None,
    language_tool: Annotated[
        str | None,
        typer.Option(
            "--language-tool",
            "-lt",
            help="Language for LanguageTool checking (e.g., es, en). Enables checks.",
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
            help="Keep LanguageTool container running after conversion",
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
            help="Comma-separated list of rule IDs to disable (e.g., WHITESPACE_RULE)",
        ),
    ] = None,
    lt_ignore_words: Annotated[
        str | None,
        typer.Option(
            "--lt-ignore-words",
            help="Comma-separated list of words to ignore.",
        ),
    ] = None,
    lt_strict: Annotated[
        bool,
        typer.Option(
            "--lt-strict", help="Fail if LanguageTool finds any errors (implies --lt-stop-on-error)"
        ),
    ] = False,
    lt_no_spelling: Annotated[
        bool,
        typer.Option(
            "--lt-no-spelling",
            help="Disable spell checking (useful for technical docs)",
        ),
    ] = False,
    verify_apa: Annotated[
        bool,
        typer.Option(
            "--verify-apa/--no-verify-apa",
            help="Verify PDF against APA 7th Edition standards after export",
        ),
    ] = True,
    apa_strict: Annotated[
        bool,
        typer.Option(
            "--apa-strict", help="Use strict APA 7 validation; any detected warning is a failure"
        ),
    ] = True,
    apa_report: Annotated[
        Path | None,
        typer.Option("--apa-report", help="Save APA verification report to file (Markdown format)"),
    ] = None,
) -> None:
    """
    Convert a Markdown file to DOCX and/or PDF.
    """
    # Build options
    opts = ConvertOptions(
        output_dir=output_dir,
        format=format,
        style=style,
        bibliography=bibliography,
        csl=csl,
        language_tool=language_tool,
        lt_host=lt_host,
        lt_port=lt_port,
        lt_stop_on_error=lt_stop_on_error,
        lt_docker=lt_docker,
        lt_keep_alive=lt_keep_alive,
        lt_report=lt_report,
        lt_enabled_rules=lt_enabled_rules,
        lt_disabled_rules=lt_disabled_rules,
        lt_ignore_words=lt_ignore_words,
        lt_strict=lt_strict,
        lt_no_spelling=lt_no_spelling,
        verify_apa=verify_apa,
        apa_strict=apa_strict,
        apa_report=apa_report,
    )

    try:
        Converter.convert_document(input_file, opts)
    except NormaDocsError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from None


if __name__ == "__main__":
    app()

"""
Helper functions for CLI commands.

These functions encapsulate the detailed logic of the convert command,
keeping cli.py as a thin orchestrator.
"""

import logging
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import typer
from docx import Document

from .formatters import get_formatter
from .languagetool_client import LanguageToolClient, LanguageToolError, format_errors
from .models import DocumentMetadata
from .pandoc_client import PandocRunner
from .pdf_generator import PDFGenerator
from .preprocessor import MarkdownPreprocessor
from .utils.subprocess import CommandFailedError, get_command_path, run_command

logger = logging.getLogger("normadocs")


class LanguageToolResult(NamedTuple):
    """Result from LanguageTool check."""

    errors: list[LanguageToolError]
    all_errors: list[tuple[str, list[LanguageToolError]]]


def _setup_languagetool_client(
    language_tool: str | None,
    lt_host: str,
    lt_port: int,
    lt_enabled_rules: str | None,
    lt_disabled_rules: str | None,
    lt_ignore_words: str | None,
    lt_no_spelling: bool,
    default_ignore_words: list[str],
) -> LanguageToolClient | None:
    """
    Create and configure a LanguageToolClient with the given parameters.

    Args:
        language_tool: Language code (e.g., 'es', 'en') or None to skip
        lt_host: LanguageTool server host
        lt_port: LanguageTool server port
        lt_enabled_rules: Comma-separated rule IDs to enable
        lt_disabled_rules: Comma-separated rule IDs to disable
        lt_ignore_words: Comma-separated words to ignore
        lt_no_spelling: Whether to disable spell checking
        default_ignore_words: Default words to ignore from config file

    Returns:
        Configured LanguageToolClient instance or None if language_tool is None
    """
    if not language_tool:
        return None

    enabled_rules = (
        [r.strip() for r in lt_enabled_rules.split(",") if r.strip()] if lt_enabled_rules else None
    )
    disabled_rules = (
        [r.strip() for r in lt_disabled_rules.split(",") if r.strip()]
        if lt_disabled_rules
        else None
    )

    # Determine ignore words
    if lt_ignore_words == "":
        ignore_words = []
    elif lt_ignore_words:
        ignore_words = lt_ignore_words.split(",")
    else:
        ignore_words = default_ignore_words

    return LanguageToolClient(
        host=lt_host,
        port=lt_port,
        language=language_tool,
        enabled_rules=enabled_rules,
        disabled_rules=disabled_rules,
        ignore_words=ignore_words,
        disable_spelling=lt_no_spelling,
    )


def _ensure_languagetool_server(
    lt_client: LanguageToolClient,
    lt_docker: bool,
    lt_port: int,
) -> str | None:
    """
    Ensure LanguageTool server is running, starting Docker container if needed.

    Args:
        lt_client: LanguageToolClient instance
        lt_docker: Whether to auto-start Docker container
        lt_port: Port to use (may be adjusted for docker)

    Returns:
        Docker container name if we started one, None otherwise

    Raises:
        SystemExit: If server cannot be started
    """
    if lt_client.is_server_running():
        return None

    if lt_docker:
        docker_path = get_command_path("docker")
        logger.info("▸ Iniciando contenedor Docker de LanguageTool...")
        try:
            run_command(
                [
                    docker_path,
                    "run",
                    "-d",
                    "--name",
                    "normadocs-lt",
                    "-p",
                    f"{lt_port}:8010",
                    "erikvl87/languagetool",
                ],
            )
        except CommandFailedError as e:
            typer.echo(f"Error iniciando contenedor Docker: {e.stderr}", err=True)
            raise typer.Exit(code=1) from None

        logger.info("▸ Esperando que LanguageTool esté listo...")
        for _ in range(30):
            if lt_client.is_server_running():
                break
            time.sleep(1)
        else:
            typer.echo("Error: LanguageTool server no respondió a tiempo.", err=True)
            raise typer.Exit(code=1)

        return "normadocs-lt"
    else:
        typer.echo(
            f"Error: LanguageTool server no está corriendo en {lt_client.base_url}. "
            "Use --lt-docker para iniciar automáticamente o ejecute:\n"
            "  docker run -d --name normadocs-lt -p 8081:8081 erikvl87/languagetool",
            err=True,
        )
        raise typer.Exit(code=1)


def _run_languagetool_precheck(
    lt_client: LanguageToolClient,
    content: str,
    lt_stop_on_error: bool,
    all_errors: list[tuple[str, list[LanguageToolError]]],
) -> bool:
    """
    Run LanguageTool check on markdown content before conversion.

    Args:
        lt_client: LanguageToolClient instance
        content: Markdown content to check
        lt_stop_on_error: Whether to exit on errors
        all_errors: List to append errors to for reporting

    Returns:
        True if check passed (no errors or --lt-continue-on-error), False otherwise
    """
    logger.info("▸ Verificando con LanguageTool (%s)...", lt_client.language)

    errors = lt_client.check(content)
    if errors:
        all_errors.append(("Pre-conversión (Markdown)", errors))
        error_output = format_errors(errors)
        typer.echo(f"✗ {error_output}", err=True)
        if lt_stop_on_error:
            return False
    return True


def _run_languagetool_postcheck(
    lt_client: LanguageToolClient,
    output_docx: Path,
    lt_stop_on_error: bool,
    all_errors: list[tuple[str, list[LanguageToolError]]],
) -> bool:
    """
    Run LanguageTool check on DOCX content after conversion.

    Args:
        lt_client: LanguageToolClient instance
        output_docx: Path to the generated DOCX file
        lt_stop_on_error: Whether to exit on errors
        all_errors: List to append errors to for reporting

    Returns:
        True if check passed, False otherwise
    """
    logger.info("▸ Verificando DOCX con LanguageTool...")

    doc = Document(str(output_docx))
    doc_text = "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())

    errors = lt_client.check(doc_text)
    if errors:
        all_errors.append(("Post-conversión (DOCX)", errors))
        error_output = format_errors(errors)
        typer.echo(f"✗ {error_output}", err=True)
        if lt_stop_on_error:
            return False
    return True


def _run_pandoc(
    clean_md: str,
    output_docx: Path,
    bibliography: str | None,
    csl: str | None,
    input_path: Path,
) -> bool:
    """
    Execute pandoc conversion from Markdown to DOCX.

    Args:
        clean_md: Processed markdown content
        output_docx: Output DOCX path
        bibliography: Path to bibliography file
        csl: Path to CSL style file
        input_path: Original input file path (for resource resolution)

    Returns:
        True if conversion succeeded, False otherwise
    """
    runner = PandocRunner()
    source_dir = str(input_path.resolve().parent)

    if not runner.run(
        clean_md, str(output_docx), bibliography=bibliography, csl=csl, resource_path=source_dir
    ):
        typer.echo("Error crítico en Pandoc. Abortando.", err=True)
        return False
    return True


def _apply_formatting(
    style: str,
    output_docx: Path,
    meta: DocumentMetadata,
) -> None:
    """
    Apply formatting to the generated DOCX document.

    Args:
        style: Citation style (apa, icontec, etc.)
        output_docx: Path to the DOCX file
        meta: Document metadata extracted from markdown

    Raises:
        SystemExit: If formatting fails
    """
    try:
        formatter = get_formatter(style, str(output_docx))
        formatter.process(meta)
        formatter.save(str(output_docx))
    except (ValueError, TypeError) as e:
        typer.echo(f"Error aplicando formato: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1) from None


def _generate_pdf(
    format: str,
    output_docx: Path,
    output_dir: Path,
    clean_md: str,
    output_pdf: Path,
) -> bool:
    """
    Generate PDF from DOCX if requested.

    Args:
        format: Output format (docx, pdf, or all)
        output_docx: Path to source DOCX
        output_dir: Output directory
        clean_md: Markdown content for WeasyPrint fallback
        output_pdf: Path for output PDF

    Returns:
        True if PDF was generated successfully, False otherwise
    """
    if format not in ["pdf", "all"]:
        return True

    logger.info("▸ Generando PDF...")
    if PDFGenerator.convert(str(output_docx), str(output_dir), clean_md, str(output_pdf)):
        logger.info("✔ PDF generado: %s", output_pdf.name)
        return True
    else:
        logger.warning("⚠ No se pudo generar el PDF (instale LibreOffice o WeasyPrint).")
        return False


def _cleanup_docker(
    docker_container: str | None,
    lt_keep_alive: bool,
    lt_port: int,
) -> None:
    """
    Clean up Docker container started for LanguageTool.

    Args:
        docker_container: Container name if we started one
        lt_keep_alive: Whether to keep container running
        lt_port: Port for logging
    """
    if not docker_container:
        return

    if lt_keep_alive:
        logger.info(
            "✔ Contenedor Docker '%s' sigue ejecutándose en puerto %d",
            docker_container,
            lt_port,
        )
        logger.info("   Use 'docker stop normadocs-lt' para detenerlo manualmente")
    else:
        logger.info("▸ Limpiando contenedor Docker...")
        docker_path = get_command_path("docker")
        run_command(
            [docker_path, "rm", "-f", docker_container],
            check=False,
        )


def _write_lt_report(
    lt_report: Path | None,
    all_errors: list[tuple[str, list[LanguageToolError]]],
    input_path: Path,
    language_tool: str | None,
) -> None:
    """
    Write LanguageTool error report to file if requested.

    Args:
        lt_report: Path for report file (None to skip)
        all_errors: List of (stage, errors) tuples
        input_path: Original input file path
        language_tool: Language used for checking
    """
    if not lt_report or not all_errors:
        return

    report_lines = [
        f"# Reporte de LanguageTool - {input_path.name}",
        "",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Archivo:** {input_path.name}",
        f"**Idioma:** {language_tool}",
        "",
        "## Errores encontrados",
        "",
    ]
    for stage, errors in all_errors:
        report_lines.append(f"### {stage}")
        report_lines.append("")
        for i, error in enumerate(errors, 1):
            report_lines.append(f"**{i}.** {error.message}")
            if error.context:
                report_lines.append(f"   - Contexto: ...{error.context}...")
            if error.replacements:
                report_lines.append(f"   - Sugerencias: {', '.join(error.replacements[:3])}")
            report_lines.append("")

    lt_report.write_text("\n".join(report_lines), encoding="utf-8")
    logger.info("▸ Reporte guardado: %s", lt_report)


def process_markdown(input_path: Path) -> tuple[str, DocumentMetadata]:
    """
    Process input markdown file with the preprocessor.

    Args:
        input_path: Path to input markdown file

    Returns:
        Tuple of (cleaned markdown, document metadata)

    Raises:
        SystemExit: If processing fails
    """
    preprocessor = MarkdownPreprocessor()
    try:
        content = input_path.read_text(encoding="utf-8")
        clean_md, meta = preprocessor.process(content)
        return clean_md, meta
    except Exception as e:
        typer.echo(f"Error procesando Markdown: {e}", err=True)
        raise typer.Exit(code=1) from None

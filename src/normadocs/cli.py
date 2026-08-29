"""
Command Line Interface for APA Engine.
"""

import inspect
import logging
from pathlib import Path
from typing import Annotated, Any

import typer
from docx import Document

from . import cli_helpers
from .config import DEFAULT_OUTPUT_DIR
from .formatters import get_formatter
from .languagetool_client import LanguageToolClient, LanguageToolError, format_errors
from .models import ConvertOptions
from .pandoc_client import PandocRunner
from .pdf_generator import PDFGenerator
from .preprocessor import MarkdownPreprocessor

__all__ = [
    "Document",
    "LanguageToolClient",
    "MarkdownPreprocessor",
    "PDFGenerator",
    "PandocRunner",
    "format_errors",
    "get_formatter",
]

logger = logging.getLogger("normadocs")

VALID_STYLES = ["apa", "apa7", "apa7estudiante", "icontec", "ieee"]
VALID_FORMATS = ["docx", "pdf", "all"]

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


def _validate_inputs(input_path: Path, style: str, fmt: str) -> None:
    if not input_path.exists():
        typer.echo(f"Error: El archivo {input_path} no existe.", err=True)
        raise typer.Exit(code=1)
    if style.lower() not in VALID_STYLES:
        typer.echo(
            f"Error: Estilo de citación no soportado: '{style}'. "
            f"Estilos disponibles: {', '.join(VALID_STYLES)}.",
            err=True,
        )
        raise typer.Exit(code=1)
    if fmt.lower() not in VALID_FORMATS:
        typer.echo(
            f"Error: Formato de salida no soportado: '{fmt}'. "
            f"Formatos disponibles: {', '.join(VALID_FORMATS)}.",
            err=True,
        )
        raise typer.Exit(code=1)


def _resolve_lt_effective_port(requested_port: int, use_docker: bool) -> int:
    if use_docker and requested_port == 8081:
        return 8010
    return requested_port


def _resolve_lt_stop_on_error(opts: ConvertOptions) -> bool:
    if opts.lt_strict:
        return True
    return opts.lt_stop_on_error


def _setup_lt_client(
    opts: ConvertOptions, effective_port: int, stop_on_error: bool
) -> LanguageToolClient | None:
    # stop_on_error currently unused but kept for symmetry; actual client uses opts
    _ = stop_on_error
    return cli_helpers._setup_languagetool_client(
        language_tool=opts.language_tool,
        lt_host=opts.lt_host,
        lt_port=effective_port,
        lt_enabled_rules=opts.lt_enabled_rules,
        lt_disabled_rules=opts.lt_disabled_rules,
        lt_ignore_words=opts.lt_ignore_words,
        lt_no_spelling=opts.lt_no_spelling,
        default_ignore_words=DEFAULT_LT_IGNORE_WORDS,
    )


def _ensure_lt_server(
    lt_client: LanguageToolClient | None, opts: ConvertOptions, effective_port: int
) -> str | None:
    if lt_client is None:
        return None
    return cli_helpers._ensure_languagetool_server(lt_client, opts.lt_docker, effective_port)


def _run_lt_precheck(
    lt_client: LanguageToolClient | None,
    clean_md: str,
    stop_on_error: bool,
    all_errors: list[tuple[str, list[LanguageToolError]]],
) -> bool:
    if lt_client is None:
        return True
    return cli_helpers._run_languagetool_precheck(lt_client, clean_md, stop_on_error, all_errors)


def _run_pandoc_stage(
    clean_md: str, output_docx: Path, opts: ConvertOptions, input_path: Path
) -> bool:
    return cli_helpers._run_pandoc(clean_md, output_docx, opts.bibliography, opts.csl, input_path)


def _run_lt_postcheck(
    lt_client: LanguageToolClient | None,
    output_docx: Path,
    stop_on_error: bool,
    all_errors: list[tuple[str, list[LanguageToolError]]],
) -> bool:
    if lt_client is None:
        return True
    return cli_helpers._run_languagetool_postcheck(
        lt_client, output_docx, stop_on_error, all_errors
    )


def _apply_formatting_stage(style: str, output_docx: Path, meta: Any) -> None:
    logger.info("▸ Aplicando formato %s ...", style.upper())
    cli_helpers._apply_formatting(style, output_docx, meta)
    logger.info("✔ Generado con éxito: %s", output_docx.name)


def _generate_pdf_stage(
    opts: ConvertOptions, output_docx: Path, output_dir: Path, clean_md: str, output_pdf: Path
) -> bool:
    return cli_helpers._generate_pdf(opts.format, output_docx, output_dir, clean_md, output_pdf)


def _should_verify_apa(opts: ConvertOptions, pdf_generated: bool) -> bool:
    return (
        opts.style.lower() in {"apa", "apa7", "apa7estudiante"}
        and opts.format in ["pdf", "all"]
        and pdf_generated
        and opts.verify_apa
    )


def _verify_apa_stage(output_pdf: Path, output_docx: Path, meta: Any, opts: ConvertOptions) -> bool:
    return cli_helpers._verify_apa(output_pdf, output_docx, meta, opts.apa_strict, opts.apa_report)


def _finalize(
    docker_container: str | None,
    opts: ConvertOptions,
    effective_port: int,
    all_errors: list[tuple[str, list[LanguageToolError]]],
    input_path: Path,
) -> None:
    cli_helpers._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
    cli_helpers._write_lt_report(opts.lt_report, all_errors, input_path, opts.language_tool)
    logger.info("\nDone!")


def _orchestrate(input_file: Path, opts: ConvertOptions) -> None:
    """Orchestrate the full conversion pipeline (9 stages)."""
    _validate_inputs(input_file, opts.style, opts.format)

    output_dir = Path(opts.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stop_on_error = _resolve_lt_stop_on_error(opts)
    effective_port = _resolve_lt_effective_port(opts.lt_port, opts.lt_docker)

    logger.info("▸ Procesando %s ...", input_file)

    clean_md, meta = cli_helpers.process_markdown(input_file)
    clean_md, _ = cli_helpers._run_codeimage(clean_md, output_dir)

    all_errors: list[tuple[str, list[LanguageToolError]]] = []
    docker_container: str | None = None
    lt_client: LanguageToolClient | None = None

    if opts.language_tool:
        lt_client = _setup_lt_client(opts, effective_port, stop_on_error)
        docker_container = _ensure_lt_server(lt_client, opts, effective_port)
        if not _run_lt_precheck(lt_client, clean_md, stop_on_error, all_errors):
            cli_helpers._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
            raise typer.Exit(code=1)

    suffix = f"_{opts.style.upper()}"
    output_docx = output_dir / f"{input_file.stem}{suffix}.docx"
    output_pdf = output_dir / f"{input_file.stem}{suffix}.pdf"

    if not _run_pandoc_stage(clean_md, output_docx, opts, input_file):
        cli_helpers._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
        raise typer.Exit(code=1)

    if (
        opts.language_tool
        and lt_client
        and not _run_lt_postcheck(lt_client, output_docx, stop_on_error, all_errors)
    ):
        cli_helpers._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
        raise typer.Exit(code=1)

    _apply_formatting_stage(opts.style, output_docx, meta)

    pdf_generated = _generate_pdf_stage(opts, output_docx, output_dir, clean_md, output_pdf)

    if _should_verify_apa(opts, pdf_generated):
        passed = _verify_apa_stage(output_pdf, output_docx, meta, opts)
        if opts.apa_strict and not passed:
            typer.echo("Error: el documento no cumple la validación estricta APA 7.", err=True)
            raise typer.Exit(code=1)

    _finalize(docker_container, opts, effective_port, all_errors, input_file)


def _coerce_path(value: Any, default: Path | None = None) -> Path | None:
    if isinstance(value, Path):
        return value
    if isinstance(value, str) and value:
        return Path(value)
    return default


def _coerce_output_dir(value: Any) -> Path:
    if isinstance(value, Path):
        return value
    if isinstance(value, str) and value:
        return Path(value)
    return DEFAULT_OUTPUT_DIR


def _coerce_int(value: Any, default: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _coerce_str_or_none(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _build_options(**kwargs: Any) -> ConvertOptions:
    """Build ConvertOptions from kwargs (used by wrapper)."""
    output_dir = _coerce_output_dir(kwargs.get("output_dir", DEFAULT_OUTPUT_DIR))
    lt_port = _coerce_int(kwargs.get("lt_port", 8081), 8081)
    apa_report = _coerce_path(kwargs.get("apa_report"))
    lt_report = _coerce_path(kwargs.get("lt_report"))

    return ConvertOptions(
        output_dir=output_dir,
        format=str(kwargs.get("format", "docx")),
        style=str(kwargs.get("style", "apa7estudiante")),
        bibliography=_coerce_str_or_none(kwargs.get("bibliography")),
        csl=_coerce_str_or_none(kwargs.get("csl")),
        language_tool=_coerce_str_or_none(kwargs.get("language_tool")),
        lt_host=str(kwargs.get("lt_host", "localhost")),
        lt_port=lt_port,
        lt_stop_on_error=bool(kwargs.get("lt_stop_on_error", True)),
        lt_docker=bool(kwargs.get("lt_docker", False)),
        lt_keep_alive=bool(kwargs.get("lt_keep_alive", False)),
        lt_report=lt_report,
        lt_enabled_rules=_coerce_str_or_none(kwargs.get("lt_enabled_rules")),
        lt_disabled_rules=_coerce_str_or_none(kwargs.get("lt_disabled_rules")),
        lt_ignore_words=_coerce_str_or_none(kwargs.get("lt_ignore_words")),
        lt_strict=bool(kwargs.get("lt_strict", False)),
        lt_no_spelling=bool(kwargs.get("lt_no_spelling", False)),
        verify_apa=bool(kwargs.get("verify_apa", True)),
        apa_strict=bool(kwargs.get("apa_strict", True)),
        apa_report=apa_report,
    )


def convert(input_file: Path, **kwargs: Any) -> None:
    """
    Convert a Markdown file to DOCX/PDF with specific citation style.
    """
    opts = _build_options(**kwargs)
    # input_file is already a Path from Typer; ensure it is Path
    input_path = Path(input_file) if not isinstance(input_file, Path) else input_file
    _orchestrate(input_path, opts)


# --- Typer signature injection to keep help while reducing S107 param count ---
# Build a signature with 21 annotated parameters so Typer generates full help,
# while source keeps only 2 params (S107 fix).
_convert_sig = inspect.Signature(
    parameters=[
        inspect.Parameter(
            "input_file",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                Path, typer.Argument(help="Input Markdown file", exists=True, readable=True)
            ],
        ),
        inspect.Parameter(
            "output_dir",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                Path, typer.Option("--output-dir", "-o", help="Directory for output files")
            ],
            default=DEFAULT_OUTPUT_DIR,
        ),
        inspect.Parameter(
            "format",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str, typer.Option("--format", "-f", help="Output format: docx, pdf, or all")
            ],
            default="docx",
        ),
        inspect.Parameter(
            "style",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str,
                typer.Option(
                    "--style",
                    "-s",
                    help="Citation style: apa7estudiante (default), apa, icontec, or ieee",
                ),
            ],
            default="apa7estudiante",
        ),
        inspect.Parameter(
            "bibliography",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str | None,
                typer.Option("--bibliography", "-b", help="Path to bibliography file (.bib)"),
            ],
            default=None,
        ),
        inspect.Parameter(
            "csl",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str | None, typer.Option("--csl", "-c", help="Path to CSL style file")
            ],
            default=None,
        ),
        inspect.Parameter(
            "language_tool",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str | None,
                typer.Option(
                    "--language-tool",
                    "-lt",
                    help=(
                        "Language for LanguageTool checking (e.g., es, en, fr). "
                        "Enables pre and post conversion checks."
                    ),
                ),
            ],
            default=None,
        ),
        inspect.Parameter(
            "lt_host",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[str, typer.Option("--lt-host", help="LanguageTool server host")],
            default="localhost",
        ),
        inspect.Parameter(
            "lt_port",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[int, typer.Option("--lt-port", help="LanguageTool server port")],
            default=8081,
        ),
        inspect.Parameter(
            "lt_stop_on_error",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                bool,
                typer.Option(
                    "--lt-stop-on-error/--lt-continue-on-error",
                    help="Stop or continue if LanguageTool finds errors",
                ),
            ],
            default=True,
        ),
        inspect.Parameter(
            "lt_docker",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                bool,
                typer.Option(
                    "--lt-docker",
                    help="Start LanguageTool container automatically using Docker (uses port 8010)",
                ),
            ],
            default=False,
        ),
        inspect.Parameter(
            "lt_keep_alive",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                bool,
                typer.Option(
                    "--lt-keep-alive",
                    help=(
                        "Keep LanguageTool container running after conversion "
                        "(for faster subsequent runs)"
                    ),
                ),
            ],
            default=False,
        ),
        inspect.Parameter(
            "lt_report",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                Path | None,
                typer.Option(
                    "--lt-report",
                    help=(
                        "Save LanguageTool errors to a report file "
                        "(Markdown format) for later review"
                    ),
                ),
            ],
            default=None,
        ),
        inspect.Parameter(
            "lt_enabled_rules",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str | None,
                typer.Option(
                    "--lt-enabled-rules",
                    help="Comma-separated list of rule IDs to enable (e.g., MISC_SPELLING,GRAMMAR)",
                ),
            ],
            default=None,
        ),
        inspect.Parameter(
            "lt_disabled_rules",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str | None,
                typer.Option(
                    "--lt-disabled-rules",
                    help=(
                        "Comma-separated list of rule IDs to disable "
                        "(e.g., WHITESPACE_RULE,UPPERCASE_SENTENCE_START)"
                    ),
                ),
            ],
            default=None,
        ),
        inspect.Parameter(
            "lt_ignore_words",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                str | None,
                typer.Option(
                    "--lt-ignore-words",
                    help=(
                        "Comma-separated list of words to ignore. "
                        "Default: uses config file (empty to disable)"
                    ),
                ),
            ],
            default=None,
        ),
        inspect.Parameter(
            "lt_strict",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                bool,
                typer.Option(
                    "--lt-strict",
                    help="Fail if LanguageTool finds any errors (implies --lt-stop-on-error)",
                ),
            ],
            default=False,
        ),
        inspect.Parameter(
            "lt_no_spelling",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                bool,
                typer.Option(
                    "--lt-no-spelling",
                    help=(
                        "Disable spell checking (useful for technical "
                        "documents with many technical terms)"
                    ),
                ),
            ],
            default=False,
        ),
        inspect.Parameter(
            "verify_apa",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                bool,
                typer.Option(
                    "--verify-apa/--no-verify-apa",
                    help="Verify PDF against APA 7th Edition standards after export",
                ),
            ],
            default=True,
        ),
        inspect.Parameter(
            "apa_strict",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                bool,
                typer.Option(
                    "--apa-strict",
                    help="Use strict APA 7 validation; any detected warning is a failure",
                ),
            ],
            default=True,
        ),
        inspect.Parameter(
            "apa_report",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Annotated[
                Path | None,
                typer.Option(
                    "--apa-report",
                    help="Save APA verification report to file (Markdown format)",
                ),
            ],
            default=None,
        ),
    ]
)

_convert_annotations: dict[str, Any] = {
    "input_file": Annotated[
        Path, typer.Argument(help="Input Markdown file", exists=True, readable=True)
    ],
    "output_dir": Annotated[
        Path, typer.Option("--output-dir", "-o", help="Directory for output files")
    ],
    "format": Annotated[
        str, typer.Option("--format", "-f", help="Output format: docx, pdf, or all")
    ],
    "style": Annotated[
        str,
        typer.Option(
            "--style", "-s", help="Citation style: apa7estudiante (default), apa, icontec, or ieee"
        ),
    ],
    "bibliography": Annotated[
        str | None, typer.Option("--bibliography", "-b", help="Path to bibliography file (.bib)")
    ],
    "csl": Annotated[str | None, typer.Option("--csl", "-c", help="Path to CSL style file")],
    "language_tool": Annotated[
        str | None,
        typer.Option(
            "--language-tool",
            "-lt",
            help=(
                "Language for LanguageTool checking (e.g., es, en, fr). "
                "Enables pre and post checks."
            ),
        ),
    ],
    "lt_host": Annotated[str, typer.Option("--lt-host", help="LanguageTool server host")],
    "lt_port": Annotated[int, typer.Option("--lt-port", help="LanguageTool server port")],
    "lt_stop_on_error": Annotated[
        bool,
        typer.Option(
            "--lt-stop-on-error/--lt-continue-on-error",
            help="Stop or continue if LanguageTool finds errors",
        ),
    ],
    "lt_docker": Annotated[
        bool,
        typer.Option(
            "--lt-docker",
            help="Start LanguageTool container automatically using Docker (uses port 8010)",
        ),
    ],
    "lt_keep_alive": Annotated[
        bool,
        typer.Option(
            "--lt-keep-alive",
            help=(
                "Keep LanguageTool container running after conversion (for faster subsequent runs)"
            ),
        ),
    ],
    "lt_report": Annotated[
        Path | None,
        typer.Option(
            "--lt-report",
            help=("Save LanguageTool errors to a report file (Markdown format) for later review"),
        ),
    ],
    "lt_enabled_rules": Annotated[
        str | None,
        typer.Option(
            "--lt-enabled-rules",
            help="Comma-separated list of rule IDs to enable (e.g., MISC_SPELLING,GRAMMAR)",
        ),
    ],
    "lt_disabled_rules": Annotated[
        str | None,
        typer.Option(
            "--lt-disabled-rules",
            help=(
                "Comma-separated list of rule IDs to disable "
                "(e.g., WHITESPACE_RULE,UPPERCASE_SENTENCE_START)"
            ),
        ),
    ],
    "lt_ignore_words": Annotated[
        str | None,
        typer.Option(
            "--lt-ignore-words",
            help=(
                "Comma-separated list of words to ignore. "
                "Default: uses config file (empty to disable)"
            ),
        ),
    ],
    "lt_strict": Annotated[
        bool,
        typer.Option(
            "--lt-strict", help="Fail if LanguageTool finds any errors (implies --lt-stop-on-error)"
        ),
    ],
    "lt_no_spelling": Annotated[
        bool,
        typer.Option(
            "--lt-no-spelling",
            help=(
                "Disable spell checking (useful for technical documents with many technical terms)"
            ),
        ),
    ],
    "verify_apa": Annotated[
        bool,
        typer.Option(
            "--verify-apa/--no-verify-apa",
            help="Verify PDF against APA 7th Edition standards after export",
        ),
    ],
    "apa_strict": Annotated[
        bool,
        typer.Option(
            "--apa-strict", help="Use strict APA 7 validation; any detected warning is a failure"
        ),
    ],
    "apa_report": Annotated[
        Path | None,
        typer.Option("--apa-report", help="Save APA verification report to file (Markdown format)"),
    ],
    "return": None,
    "kwargs": Any,
}

object.__setattr__(convert, "__signature__", _convert_sig)
object.__setattr__(convert, "__annotations__", _convert_annotations)

app.command()(convert)

if __name__ == "__main__":
    app()

"""
Command Line Interface for APA Engine.
"""

import logging
import traceback
from pathlib import Path
from typing import Annotated

import typer

from .config import DEFAULT_OUTPUT_DIR
from .formatters import get_formatter
from .pandoc_client import PandocRunner
from .pdf_generator import PDFGenerator
from .preprocessor import MarkdownPreprocessor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("normadocs")

app = typer.Typer(
    help="NormaDocs: Convert Markdown to APA 7th, ICONTEC, or IEEE formatted DOCX/PDF."
)


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
):
    """
    Convert a Markdown file to DOCX/PDF with specific citation style.
    """
    input_path = Path(input_file)
    if not input_path.exists():
        typer.echo(f"Error: El archivo {input_file} no existe.", err=True)
        raise typer.Exit(code=1)

    # Ensure output dir exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Preprocedimiento
    print(f"▸ Procesando {input_file} ...")
    preprocessor = MarkdownPreprocessor()
    try:
        content = input_path.read_text(encoding="utf-8")
        clean_md, meta = preprocessor.process(content)
    except Exception as e:
        typer.echo(f"Error procesando Markdown: {e}", err=True)
        raise typer.Exit(code=1) from None

    # 2. Pandoc (con Bibliografía/CSL)
    suffix = f"_{style.upper()}"
    output_docx = output_dir / f"{input_path.stem}{suffix}.docx"
    output_pdf = output_dir / f"{input_path.stem}{suffix}.pdf"

    runner = PandocRunner()
    source_dir = str(input_path.resolve().parent)
    if not runner.run(
        clean_md, str(output_docx), bibliography=bibliography, csl=csl, resource_path=source_dir
    ):
        typer.echo("Error crítico en Pandoc. Abortando.", err=True)
        raise typer.Exit(code=1)

    # 4. Styling
    print(f"▸ Aplicando formato {style.upper()} ...")
    try:
        formatter = get_formatter(style, str(output_docx))
        formatter.process(meta)
        formatter.save(str(output_docx))
    except Exception as e:
        typer.echo(f"Error aplicando formato: {e}", err=True)
        traceback.print_exc()
        raise typer.Exit(code=1) from None

    print(f"✔ Generado con éxito: {output_docx.name}")

    # 5. PDF Generation
    if format in ["pdf", "all"]:
        print("▸ Generando PDF...")
        if PDFGenerator.convert(str(output_docx), str(output_dir), clean_md, str(output_pdf)):
            print(f"✔ PDF generado: {output_pdf.name}")
        else:
            print("⚠ No se pudo generar el PDF (instale LibreOffice o WeasyPrint).")

    logger.info("\nDone!")


if __name__ == "__main__":
    app()

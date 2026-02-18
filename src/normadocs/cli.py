"""
Command Line Interface for APA Engine.
"""

import logging
from pathlib import Path
from typing import Annotated

import typer

from .config import DEFAULT_OUTPUT_DIR
from .preprocessor import MarkdownPreprocessor
from .pandoc_client import PandocRunner
from .docx_formatter import APADocxFormatter
from .pdf_generator import PDFGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("normadocs")

app = typer.Typer(help="APA Engine: Convert Markdown to APA 7th Edition DOCX/PDF.")


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
):
    """
    Convert a Markdown file to APA 7 formatting.
    """
    logger.info(f"Processing {input_file} -> {output_dir} [{format}]")

    # Ensure output dir exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read Input
    try:
        raw_md = input_file.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise typer.Exit(code=1)

    # 2. Preprocess
    logger.info("Step 1: Pre-processing Markdown...")
    preprocessor = MarkdownPreprocessor()
    processed_md, meta = preprocessor.process(raw_md)

    logger.info(f"   MetaData: {meta.title} ({meta.author})")

    # 3. Pandoc Conversion
    logger.info("Step 2: Running Pandoc...")
    output_docx = output_dir / f"{input_file.stem}_APA.docx"
    runner = PandocRunner()
    success = runner.run(processed_md, str(output_docx))

    if not success:
        logger.error("Pandoc failed.")
        raise typer.Exit(code=1)

    # 4. APA Formatting
    logger.info("Step 3: Applying APA 7 Styles...")
    formatter = APADocxFormatter(str(output_docx))
    formatter.process(meta)
    formatter.save(str(output_docx))
    logger.info(f"   DOCX Created: {output_docx}")

    # 5. PDF Generation
    if format in ["pdf", "all"]:
        logger.info("Step 4: Generating PDF...")
        # Try LibreOffice first on the finalized DOCX
        if PDFGenerator.convert_with_libreoffice(str(output_docx), str(output_dir)):
            pdf_path = output_dir / f"{input_file.stem}_APA.pdf"
            logger.info(f"   PDF Created: {pdf_path}")
        else:
            # Fallback to WeasyPrint with processed MD
            pdf_path = output_dir / f"{input_file.stem}_APA.pdf"
            if PDFGenerator.convert_with_weasyprint(processed_md, str(pdf_path)):
                logger.info(f"   PDF Created (Fallback): {pdf_path}")

    logger.info("\nDone!")


if __name__ == "__main__":
    app()

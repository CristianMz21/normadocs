"""
Core Converter API for NormaDocs.
"""

import logging
import time
from datetime import datetime
from pathlib import Path

from docx import Document

from .exceptions import ConversionError, ValidationError
from .exceptions import LanguageToolError as LTException
from .formatters import get_formatter
from .languagetool_client import LanguageToolClient, LanguageToolError, format_errors
from .models import ConvertOptions, DocumentMetadata
from .pandoc_client import PandocRunner
from .pdf_generator import PDFGenerator
from .preprocessor import MarkdownPreprocessor
from .utils.subprocess import get_command_path, run_command

logger = logging.getLogger("normadocs")


LANGUAGETOOL_IMAGE = (
    "erikvl87/languagetool@sha256:ef8fa12cbd485166c9ceeb7139d76d56d07707a624da6bb1fc1fbb5411750527"
)


class Converter:
    """Core orchestrator for document conversion."""

    @classmethod
    def convert_document(cls, input_file: Path, opts: ConvertOptions) -> None:
        """
        Orchestrate the full conversion pipeline (9 stages).

        Args:
            input_file: Path to the input markdown file.
            opts: Conversion options.
        """
        cls._validate_inputs(input_file, opts.style, opts.format)

        output_dir = Path(opts.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        stop_on_error = cls._resolve_lt_stop_on_error(opts)
        effective_port = cls._resolve_lt_effective_port(opts.lt_port, opts.lt_docker)

        logger.info("▸ Procesando %s ...", input_file)

        clean_md, meta = cls._process_markdown(input_file)
        clean_md, _ = cls._run_codeimage(clean_md, output_dir)

        all_errors: list[tuple[str, list[LanguageToolError]]] = []
        docker_container: str | None = None
        lt_client: LanguageToolClient | None = None

        if opts.language_tool:
            lt_client = cls._setup_languagetool_client(opts, effective_port)
            docker_container = cls._ensure_languagetool_server(
                lt_client, opts.lt_docker, effective_port
            )
            if not cls._run_languagetool_precheck(lt_client, clean_md, stop_on_error, all_errors):
                cls._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
                raise LTException("LanguageTool pre-check failed.")

        suffix = f"_{opts.style.upper()}"
        output_docx = output_dir / f"{input_file.stem}{suffix}.docx"
        output_pdf = output_dir / f"{input_file.stem}{suffix}.pdf"

        if not cls._run_pandoc(clean_md, output_docx, opts.bibliography, opts.csl, input_file):
            cls._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
            raise ConversionError("Pandoc conversion failed.")

        if (
            opts.language_tool
            and lt_client
            and not cls._run_languagetool_postcheck(
                lt_client, output_docx, stop_on_error, all_errors
            )
        ):
            cls._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
            raise LTException("LanguageTool post-check failed.")

        cls._apply_formatting(opts.style, output_docx, meta)

        pdf_generated = cls._generate_pdf(
            opts.format, output_docx, output_dir, clean_md, output_pdf, input_file
        )

        if cls._should_verify_apa(opts, pdf_generated):
            passed = cls._verify_apa(
                output_pdf, output_docx, meta, opts.apa_strict, opts.apa_report
            )
            if opts.apa_strict and not passed:
                raise ConversionError("El documento no cumple la validación estricta APA 7.")

        cls._finalize(docker_container, opts, effective_port, all_errors, input_file)

    @classmethod
    def _validate_inputs(cls, input_path: Path, style: str, fmt: str) -> None:
        VALID_STYLES = ["apa", "apa7", "apa7estudiante", "icontec", "ieee"]
        VALID_FORMATS = ["docx", "pdf", "all"]

        if not input_path.exists():
            raise ValidationError(f"El archivo {input_path} no existe.")
        if style.lower() not in VALID_STYLES:
            raise ValidationError(
                f"Estilo de citación no soportado: '{style}'. "
                f"Estilos disponibles: {', '.join(VALID_STYLES)}."
            )
        if fmt.lower() not in VALID_FORMATS:
            raise ValidationError(
                f"Formato de salida no soportado: '{fmt}'. "
                f"Formatos disponibles: {', '.join(VALID_FORMATS)}."
            )

    @classmethod
    def _resolve_lt_effective_port(cls, requested_port: int, use_docker: bool) -> int:
        if use_docker and requested_port == 8081:
            return 8010
        return requested_port

    @classmethod
    def _resolve_lt_stop_on_error(cls, opts: ConvertOptions) -> bool:
        if opts.lt_strict:
            return True
        return opts.lt_stop_on_error

    @classmethod
    def _setup_languagetool_client(
        cls, opts: ConvertOptions, effective_port: int
    ) -> LanguageToolClient:
        config_path = Path(__file__).parent / "config" / "lt_ignore_words.txt"
        default_ignore_words: list[str] = []
        if config_path.exists():
            words = config_path.read_text(encoding="utf-8").strip().split("\n")
            default_ignore_words = [w.strip() for w in words if w.strip() and not w.startswith("#")]

        lt_ignore_words = opts.lt_ignore_words
        language_tool = opts.language_tool
        lt_host = opts.lt_host
        lt_enabled_rules = opts.lt_enabled_rules
        lt_disabled_rules = opts.lt_disabled_rules
        lt_no_spelling = opts.lt_no_spelling

        ignored_words = list(default_ignore_words)
        if lt_ignore_words:
            extra_words = [w.strip() for w in lt_ignore_words.split(",") if w.strip()]
            ignored_words.extend(extra_words)

        enabled_rules = [r.strip() for r in lt_enabled_rules.split(",")] if lt_enabled_rules else []
        disabled_rules = (
            [r.strip() for r in lt_disabled_rules.split(",")] if lt_disabled_rules else []
        )

        if lt_no_spelling:
            disabled_rules.append("MORFOLOGIK_RULE_ES")

        return LanguageToolClient(
            host=lt_host,
            port=effective_port,
            language=language_tool or "es",
            enabled_rules=enabled_rules,
            disabled_rules=disabled_rules,
            ignore_words=ignored_words,
        )

    @classmethod
    def _ensure_languagetool_server(
        cls, client: LanguageToolClient, use_docker: bool, port: int
    ) -> str | None:
        if client.is_server_running():
            logger.info("✔ LanguageTool detectado en %s", client.base_url)
            return None

        if not use_docker:
            logger.warning(
                "⚠ LanguageTool no disponible en %s. Inicie el servidor local o use --lt-docker.",
                client.base_url,
            )
            raise LTException("LanguageTool server not available")

        logger.info("▸ Iniciando contenedor Docker para LanguageTool en puerto %d...", port)
        container_name = f"normadocs-lt-{port}"

        try:
            docker_path = get_command_path("docker")
            run_command(
                [
                    docker_path,
                    "run",
                    "-d",
                    "--rm",
                    "--name",
                    container_name,
                    "-p",
                    f"{port}:8010",
                    LANGUAGETOOL_IMAGE,
                ]
            )

            logger.info("▸ Esperando que LanguageTool esté listo...")

            for _ in range(30):
                if client.is_server_running():
                    logger.info("✔ Contenedor LanguageTool iniciado correctamente")
                    return container_name
                time.sleep(1)

            logger.error("Error: El contenedor inició pero el servidor no responde")
            raise LTException("Contenedor LT no responde")
        except Exception as e:
            logger.error("Error iniciando Docker: %s", e)
            raise LTException(f"Error iniciando Docker: {e}") from None

    @classmethod
    def _run_languagetool_precheck(
        cls,
        client: LanguageToolClient,
        text: str,
        stop_on_error: bool,
        all_errors: list[tuple[str, list[LanguageToolError]]],
    ) -> bool:
        logger.info("▸ Ejecutando revisión pre-conversión (Markdown)...")
        errors = client.check(text)
        if not errors:
            logger.info("✔ Sin errores pre-conversión")
            return True

        all_errors.append(("Revisión Pre-conversión (Markdown)", errors))
        logger.warning(format_errors(errors))

        if stop_on_error:
            logger.error("Error: Se encontraron problemas ortográficos/gramaticales.")
            return False
        return True

    @classmethod
    def _run_languagetool_postcheck(
        cls,
        client: LanguageToolClient,
        docx_path: Path,
        stop_on_error: bool,
        all_errors: list[tuple[str, list[LanguageToolError]]],
    ) -> bool:
        logger.info("▸ Ejecutando revisión post-conversión (DOCX)...")
        try:
            doc = Document(str(docx_path))
            full_text = "\n".join(para.text for para in doc.paragraphs)

            errors = client.check(full_text)
            if not errors:
                logger.info("✔ Sin errores post-conversión")
                return True

            all_errors.append(("Revisión Post-conversión (DOCX)", errors))
            logger.warning(format_errors(errors))

            if stop_on_error:
                logger.error(
                    "Error: Se encontraron problemas ortográficos/gramaticales en el DOCX."
                )
                return False
            return True
        except Exception as e:
            logger.error("Error leyendo DOCX para revisión: %s", e)
            return not stop_on_error

    @classmethod
    def _run_pandoc(
        cls,
        clean_md: str,
        output_docx: Path,
        bibliography: str | None,
        csl: str | None,
        input_path: Path,
    ) -> bool:
        logger.info("▸ Convirtiendo Markdown a DOCX con Pandoc...")
        runner = PandocRunner()
        source_dir = str(input_path.resolve().parent)
        if runner.run(
            clean_md,
            str(output_docx),
            bibliography=bibliography,
            csl=csl,
            resource_path=source_dir,
        ):
            logger.info("✔ DOCX base generado")
            return True
        else:
            logger.error("Error: Pandoc falló al generar el DOCX.")
            return False

    @classmethod
    def _run_codeimage(cls, clean_md: str, output_dir: Path) -> tuple[str, bool]:
        try:
            from .codeimage_processor import CodeImageProcessor

            processor = CodeImageProcessor(output_dir=str(output_dir / "code_images"))
            if not processor.is_available():
                return clean_md, False

            modified_md, results = processor.process(clean_md)
            generated_count = sum(1 for r in results if r.success)
            if generated_count > 0:
                logger.info("▸ Generated %d code image(s)", generated_count)
            return modified_md, generated_count > 0
        except ImportError:
            return clean_md, False

    @classmethod
    def _apply_formatting(
        cls,
        style: str,
        output_docx: Path,
        meta: DocumentMetadata,
    ) -> None:
        logger.info("▸ Aplicando formato %s ...", style.upper())
        try:
            formatter = get_formatter(style, str(output_docx))
            formatter.process(meta)
            formatter.save(str(output_docx))
            logger.info("✔ Generado con éxito: %s", output_docx.name)
        except (ValueError, TypeError) as e:
            logger.error("Error aplicando formato: %s", e)
            logger.exception("Error applying formatting")
            raise ConversionError(f"Error aplicando formato: {e}") from None

    @classmethod
    def _generate_pdf(
        cls,
        format_str: str,
        output_docx: Path,
        output_dir: Path,
        clean_md: str,
        output_pdf: Path,
        input_path: Path | None = None,
    ) -> bool:
        if format_str not in ["pdf", "all"]:
            return True

        logger.info("▸ Generando PDF...")
        source_dir = str(input_path.resolve().parent) if input_path else None
        if PDFGenerator.convert(
            str(output_docx), str(output_dir), clean_md, str(output_pdf), source_dir
        ):
            logger.info("✔ PDF generado: %s", output_pdf.name)
            return True
        else:
            logger.warning("⚠ No se pudo generar el PDF (instale LibreOffice o WeasyPrint).")
            return False

    @classmethod
    def _should_verify_apa(cls, opts: ConvertOptions, pdf_generated: bool) -> bool:
        return (
            opts.style.lower() in {"apa", "apa7", "apa7estudiante"}
            and opts.format in ["pdf", "all"]
            and pdf_generated
            and opts.verify_apa
        )

    @classmethod
    def _verify_apa(
        cls,
        output_pdf: Path,
        output_docx: Path,
        meta: DocumentMetadata | None,
        apa_strict: bool,
        apa_report: Path | None,
    ) -> bool:
        try:
            if not output_pdf.exists():
                logger.warning("⚠ PDF no encontrado para verificación: %s", output_pdf)
                return True

            logger.info("▸ Verificando cumplimiento APA 7th...")

            from .verifier.apa_verifier import APAVerifier

            verifier = APAVerifier(
                pdf_path=output_pdf,
                docx_path=output_docx,
                meta=meta,
                strict=apa_strict,
            )

            result = verifier.verify_all()
            verifier.close()

            if result.passed:
                logger.info("✔ Verificación APA 7th: PASSED (Score: %.1f/100)", result.score)
            else:
                logger.warning("✗ Verificación APA 7th: FAILED (Score: %.1f/100)", result.score)

            if result.errors:
                for issue in result.errors:
                    logger.warning("  [ERROR] %s: %s", issue.check, issue.evidence or issue.actual)

            if result.warnings:
                for issue in result.warnings:
                    logger.warning("  [WARN] %s: %s", issue.check, issue.evidence or issue.actual)

            if apa_report:
                report = verifier.generate_report(result, format="markdown")
                apa_report.write_text(report, encoding="utf-8")
                logger.info("▸ Reporte APA guardado: %s", apa_report)

            return bool(result.passed)

        except ImportError:
            logger.warning(
                "⚠ Verificador APA no disponible (instale dependencias con: "
                "pip install normadocs[pdf-verifier])"
            )
            return not apa_strict
        except Exception as e:
            logger.warning("⚠ Error en verificación APA: %s", e)
            return not apa_strict

    @classmethod
    def _cleanup_docker(
        cls,
        docker_container: str | None,
        lt_keep_alive: bool,
        lt_port: int,
    ) -> None:
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

    @classmethod
    def _write_lt_report(
        cls,
        lt_report: Path | None,
        all_errors: list[tuple[str, list[LanguageToolError]]],
        input_path: Path,
        language_tool: str | None,
    ) -> None:
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

    @classmethod
    def _process_markdown(cls, input_path: Path) -> tuple[str, DocumentMetadata]:
        preprocessor = MarkdownPreprocessor()
        try:
            content = input_path.read_text(encoding="utf-8")
            clean_md, meta = preprocessor.process(content)
            return clean_md, meta
        except Exception as e:
            logger.error("Error procesando Markdown: %s", e)
            raise ConversionError(f"Error procesando Markdown: {e}") from None

    @classmethod
    def _finalize(
        cls,
        docker_container: str | None,
        opts: ConvertOptions,
        effective_port: int,
        all_errors: list[tuple[str, list[LanguageToolError]]],
        input_path: Path,
    ) -> None:
        cls._cleanup_docker(docker_container, opts.lt_keep_alive, effective_port)
        cls._write_lt_report(opts.lt_report, all_errors, input_path, opts.language_tool)
        logger.info("\nDone!")

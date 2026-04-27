"""APA 7th Edition verifier orchestrator.

Orchestrates all verification checks and provides comprehensive reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from . import CheckCategory, VerificationIssue, VerificationResult
from .checks import (
    CoverPageCheck,
    FiguresCheck,
    FontsCheck,
    HeadingsCheck,
    MarginsCheck,
    PageSetupCheck,
    ParagraphsCheck,
    ReferencesCheck,
    RunningHeadCheck,
    SpacingCheck,
    TablesCheck,
)
from .docx_analyzer import DOCXAnalyzer
from .pdf_analyzer import PDFAnalyzer

if TYPE_CHECKING:
    from ..models import DocumentMetadata


@dataclass
class VerificationContext:
    """Context passed to all checks with access to analyzers and metadata."""

    pdf: PDFAnalyzer
    docx: DOCXAnalyzer
    meta: DocumentMetadata
    strict: bool = False


class VerificationCheck(Protocol):
    """Protocol defining the interface for APA verification checks."""

    def run(self, ctx: VerificationContext) -> list[VerificationIssue]:
        """Run verification check and return list of issues found."""
        ...


class APAVerifier:
    """Main APA 7th Edition verifier.

    Performs comprehensive verification of exported PDF documents against
    APA 7th Edition standards using multiple analysis techniques.
    """

    def __init__(
        self,
        pdf_path: str | Path,
        docx_path: str | Path | None = None,
        meta: DocumentMetadata | None = None,
        strict: bool = False,
    ) -> None:
        """Initialize the APA verifier.

        Args:
            pdf_path: Path to the exported PDF file.
            docx_path: Optional path to the DOCX source file.
                      If not provided, will look for same-named DOCX.
            meta: Optional document metadata for enhanced verification.
            strict: If True, warnings are treated as errors.
        """
        self.pdf_path = Path(pdf_path)
        self.docx_path = self._find_docx(docx_path) if docx_path is None else Path(docx_path)
        self.meta = meta
        self.strict = strict

        self._pdf_analyzer: PDFAnalyzer | None = None
        self._docx_analyzer: DOCXAnalyzer | None = None
        self._checks: list[tuple[str, object]] = []

    def _find_docx(self, docx_path: Path | None) -> Path | None:
        """Find DOCX file with same base name as PDF."""
        if docx_path and docx_path.exists():
            return docx_path

        potential_docx = self.pdf_path.with_suffix(".docx")
        if potential_docx.exists():
            return potential_docx

        suffixes_to_remove = ("_APA", "_ICONTEC", "_IEEE")
        base_stem = self.pdf_path.stem
        for suffix in suffixes_to_remove:
            base_stem = base_stem.replace(suffix, "")
        potential_docx_same_dir = self.pdf_path.parent / f"{base_stem}.docx"
        if potential_docx_same_dir.exists():
            return potential_docx_same_dir

        return None

    @property
    def pdf(self) -> PDFAnalyzer:
        """Get or create PDF analyzer."""
        if self._pdf_analyzer is None:
            self._pdf_analyzer = PDFAnalyzer(self.pdf_path)
        return self._pdf_analyzer

    @property
    def docx(self) -> DOCXAnalyzer:
        """Get or create DOCX analyzer."""
        if self._docx_analyzer is None:
            if self.docx_path is None or not self.docx_path.exists():
                raise FileNotFoundError(
                    "DOCX file not found for verification. Provide docx_path explicitly."
                )
            self._docx_analyzer = DOCXAnalyzer(self.docx_path)
        return self._docx_analyzer

    def _init_checks(self) -> list[tuple[str, VerificationCheck]]:
        """Initialize all verification checks."""
        return [
            (CheckCategory.PAGE_SETUP, PageSetupCheck()),
            (CheckCategory.MARGINS, MarginsCheck()),
            (CheckCategory.FONTS, FontsCheck()),
            (CheckCategory.RUNNING_HEAD, RunningHeadCheck()),
            (CheckCategory.SPACING, SpacingCheck()),
            (CheckCategory.PARAGRAPHS, ParagraphsCheck()),
            (CheckCategory.HEADINGS, HeadingsCheck()),
            (CheckCategory.COVER_PAGE, CoverPageCheck()),
            (CheckCategory.TABLES, TablesCheck()),
            (CheckCategory.FIGURES, FiguresCheck()),
            (CheckCategory.REFERENCES, ReferencesCheck()),
        ]

    def verify_all(self) -> VerificationResult:
        """Run all verification checks.

        Returns:
            VerificationResult with all issues found.
        """
        if self.docx_path is None:
            raise FileNotFoundError("DOCX path is required for verification")

        meta = self.meta if self.meta is not None else self._extract_meta_from_docx()
        ctx = VerificationContext(
            pdf=self.pdf,
            docx=self.docx,
            meta=meta,
            strict=self.strict,
        )

        all_issues: list[VerificationIssue] = []
        warnings: list[VerificationIssue] = []
        errors: list[VerificationIssue] = []
        infos: list[VerificationIssue] = []

        for category, check in self._init_checks():
            try:
                issues = check.run(ctx)
                for issue in issues:
                    if "." not in issue.check:
                        issue.check = f"{category}.{issue.check.split('.')[-1]}"
                    all_issues.append(issue)

                    if issue.severity == "error":
                        errors.append(issue)
                    elif issue.severity == "warning":
                        warnings.append(issue)
                    else:
                        infos.append(issue)
            except Exception as e:
                errors.append(
                    VerificationIssue(
                        check=f"{category}.check_failed",
                        severity="error",
                        expected="Check to run successfully",
                        actual=str(e),
                        evidence=f"Check '{category}' failed with exception",
                    )
                )

        total_checks = len(self._init_checks())
        errors_count = len(errors)
        warnings_count = len(warnings)

        score = 100.0
        if total_checks > 0:
            error_penalty = (errors_count / total_checks) * 60
            warning_penalty = (warnings_count / total_checks) * 30
            score = max(0.0, score - error_penalty - warning_penalty)

        passed = len(errors) == 0
        if self.strict:
            passed = passed and len(warnings) == 0

        result = VerificationResult(
            passed=passed,
            score=score,
            issues=all_issues,
            warnings=warnings,
            infos=infos,
            errors=errors,
            pdf_path=self.pdf_path,
            docx_path=self.docx_path,
        )

        return result

    def _extract_meta_from_docx(self) -> DocumentMetadata:
        """Extract metadata from DOCX document."""
        from ..models import DocumentMetadata

        doc = self.docx.doc
        core_props = doc.core_properties

        return DocumentMetadata(
            title=core_props.title or "Untitled",
            author=core_props.author,
        )

    def generate_report(self, result: VerificationResult, format: str = "text") -> str:
        """Generate a human-readable verification report.

        Args:
            result: The verification result to report on.
            format: Output format - "text", "markdown", or "html".

        Returns:
            Formatted report string.
        """
        if format == "markdown":
            return self._generate_markdown_report(result)
        elif format == "html":
            return self._generate_html_report(result)
        else:
            return self._generate_text_report(result)

    def _generate_text_report(self, result: VerificationResult) -> str:
        """Generate plain text report."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("APA 7th Edition Verification Report")
        lines.append("=" * 60)
        lines.append(f"\nFile: {result.pdf_path}")
        lines.append(f"Score: {result.score:.1f}/100")
        lines.append(f"Status: {'PASSED' if result.passed else 'FAILED'}")

        if result.errors:
            lines.append(f"\nErrors ({len(result.errors)}):")
            for issue in result.errors:
                lines.append(f"  [ERROR] {issue.check}")
                lines.append(f"          Expected: {issue.expected}")
                lines.append(f"          Actual: {issue.actual}")
                if issue.evidence:
                    lines.append(f"          Evidence: {issue.evidence}")

        if result.warnings:
            lines.append(f"\nWarnings ({len(result.warnings)}):")
            for issue in result.warnings:
                lines.append(f"  [WARN] {issue.check}")
                lines.append(f"         Expected: {issue.expected}")
                lines.append(f"         Actual: {issue.actual}")

        if result.infos:
            lines.append(f"\nInfo ({len(result.infos)}):")
            for issue in result.infos:
                lines.append(f"  [INFO] {issue.check}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    def _generate_markdown_report(self, result: VerificationResult) -> str:
        """Generate Markdown report."""
        lines: list[str] = []
        lines.append("# APA 7th Edition Verification Report")
        lines.append("")
        lines.append(f"**File**: `{result.pdf_path}`")
        lines.append(f"**Score**: {result.score:.1f}/100")
        lines.append(f"**Status**: {'✅ PASSED' if result.passed else '❌ FAILED'}")
        lines.append("")

        if result.errors:
            lines.append(f"## Errors ({len(result.errors)})")
            lines.append("")
            for issue in result.errors:
                lines.append(f"### {issue.check}")
                lines.append(f"- **Expected**: {issue.expected}")
                lines.append(f"- **Actual**: {issue.actual}")
                if issue.evidence:
                    lines.append(f"- **Evidence**: {issue.evidence}")
                lines.append("")

        if result.warnings:
            lines.append(f"## Warnings ({len(result.warnings)})")
            lines.append("")
            for issue in result.warnings:
                lines.append(f"### {issue.check}")
                lines.append(f"- **Expected**: {issue.expected}")
                lines.append(f"- **Actual**: {issue.actual}")
                lines.append("")

        if result.infos:
            lines.append(f"## Info ({len(result.infos)})")
            lines.append("")
            for issue in result.infos:
                lines.append(f"- {issue.check}: {issue.actual}")

        return "\n".join(lines)

    def _generate_html_report(self, result: VerificationResult) -> str:
        """Generate HTML report."""
        status_class = "passed" if result.passed else "failed"
        status_icon = "✅" if result.passed else "❌"

        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '    <meta charset="UTF-8">',
            "    <title>APA 7th Edition Verification Report</title>",
            "    <style>",
            "        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; }",
            "        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; }",
            "        .score { font-size: 2em; font-weight: bold; }",
            "        .passed { color: #28a745; }",
            "        .failed { color: #dc3545; }",
            "        .err { background: #f8d7da; border-left: 4px solid #dc3545; padding: 10px; }",
            "        .warn { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; }",
            "        .info { background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 10px; }",
            "        h2 { margin-top: 30px; }",
            "        .chk { font-weight: bold; color: #333; }",
            "    </style>",
            "</head>",
            "<body>",
            '    <div class="header">',
            "        <h1>APA 7th Edition Verification Report</h1>",
            f"        <p><strong>File</strong>: {result.pdf_path}</p>",
            f'        <p class="score {status_class}">'
            f"{status_icon} Score: {result.score:.1f}/100</p>",
            f'        <p class="{status_class}">'
            f"<strong>Status</strong>: "
            f"{'PASSED' if result.passed else 'FAILED'}</p>",
            "    </div>",
        ]
        html = "\n".join(html_parts) + "\n"

        if result.errors:
            html += f"<h2>Errors ({len(result.errors)})</h2>\n"
            for issue in result.errors:
                evidence_html = (
                    f"<div><strong>Evidence</strong>: {issue.evidence}</div>"
                    if issue.evidence
                    else ""
                )
                html += (
                    f'<div class="err">'
                    f'<div class="chk">{issue.check}</div>'
                    f"<div><strong>Expected</strong>: {issue.expected}</div>"
                    f"<div><strong>Actual</strong>: {issue.actual}</div>"
                    f"{evidence_html}"
                    f"</div>\n"
                )

        if result.warnings:
            html += f"<h2>Warnings ({len(result.warnings)})</h2>\n"
            for issue in result.warnings:
                html += (
                    f'<div class="warn">'
                    f'<div class="chk">{issue.check}</div>'
                    f"<div><strong>Expected</strong>: {issue.expected}</div>"
                    f"<div><strong>Actual</strong>: {issue.actual}</div>"
                    f"</div>\n"
                )

        if result.infos:
            html += f"<h2>Info ({len(result.infos)})</h2>\n"
            for issue in result.infos:
                html += f'<div class="info">{issue.check}: {issue.actual}</div>\n'

        html += "</body></html>"
        return html

    def close(self) -> None:
        """Close all resources."""
        if self._pdf_analyzer is not None:
            self._pdf_analyzer.close()
            self._pdf_analyzer = None
        self._docx_analyzer = None

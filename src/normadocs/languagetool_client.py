"""
LanguageTool client for grammar and spell checking.
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


@dataclass
class LanguageToolError:
    """Represents an error found by LanguageTool."""

    message: str
    context: str
    rule_id: str
    offset: int
    length: int
    replacements: list[str]


class LanguageToolClient:
    """Client for LanguageTool HTTP server."""

    # Default rules to disable (generate too many false positives in technical documents)
    DEFAULT_DISABLED_RULES = (
        # Spelling rules for multiple languages
        "MORFOLOGIK_RULE_ES",
        "MORFOLOGIK_RULE_EN",
        "MORFOLOGIK_RULE_FR",
        "MORFOLOGIK_RULE_DE",
        "MORFOLOGIK_RULE_PT",
        "MORFOLOGIK_RULE_IT",
        "MORFOLOGIK_RULE_NL",
        "MORFOLOGIK_RULE_PL",
        # Specific spelling variants that generate false positives
        "ES_SIMPLE_REPLACE_SIMPLE_ZOOM",
        # Grammar rules that generate false positives in technical/code documents
        "WHITESPACE_RULE",  # Multiple spaces (common in code blocks)
        "ES_UNPAIRED_BRACKETS",  # Unmatched brackets in code
        "SIGLAS",  # Plural acronyms - API/APIs issues
        "NOUN_PLURAL2",  # False plural suggestions for words like "negocio"
        "UPPERCASE_SENTENCE_START",  # Capitalization at sentence start
        "AGREEMENT_SER_ADJ_SG",  # False concordancia errors
        "ESPACIO_DESPUES_DE_PUNTO",  # Space after period (false positive with file extensions)
        "AGREEMENT_PARTICIPLE_NOUN",  # False concordancia in table headers
        "AGREEMENT_ADJ_NOUN",  # False concordancia with adjectives
    )

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8081,
        language: str = "es",
        enabled_rules: list[str] | None = None,
        disabled_rules: list[str] | None = None,
        ignore_words: list[str] | None = None,
        prefer_comma: bool | None = None,
        disable_spelling: bool = False,
    ):
        """
        Initialize LanguageTool client.

        Args:
            host: LanguageTool server host
            port: LanguageTool server port
            language: Language code (e.g., 'es', 'en', 'fr')
            enabled_rules: List of rule IDs to enable (e.g., ['MISC_SPELLING'])
            disabled_rules: List of rule IDs to disable
            ignore_words: List of words to ignore
            prefer_comma: Whether to prefer comma over other punctuation
            disable_spelling: Whether to disable spelling rules (default: True)
        """
        self.base_url = f"http://{host}:{port}"
        self.language = language
        self.enabled_rules = enabled_rules or []
        self.ignore_words = ignore_words or []
        self.prefer_comma = prefer_comma
        self.disable_spelling = disable_spelling
        self._server_process: subprocess.Popen[bytes] | None = None

        # Combine default disabled rules with user-provided ones
        self.disabled_rules = list(self.DEFAULT_DISABLED_RULES) if disable_spelling else []
        if disabled_rules:
            self.disabled_rules.extend(disabled_rules)

    def is_server_running(self) -> bool:
        """Check if the LanguageTool server is running."""
        try:
            response = requests.get(f"{self.base_url}/v2/languages", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def check(self, text: str) -> list[LanguageToolError]:
        """
        Send text to LanguageTool and return detected errors.

        Args:
            text: The text to check.

        Returns:
            List of LanguageToolError objects.
        """
        if not text.strip():
            return []

        # Build request data
        data: dict[str, str | list[str]] = {
            "text": text,
            "language": self.language,
        }

        # Add enabled rules
        if self.enabled_rules:
            data["enabledRules"] = ",".join(self.enabled_rules)

        # Add disabled rules
        if self.disabled_rules:
            data["disabledRules"] = ",".join(self.disabled_rules)

        # Add words to ignore
        if self.ignore_words:
            data["ignoreWords"] = ",".join(self.ignore_words)

        # Add prefer comma setting
        if self.prefer_comma is not None:
            data["preferComma"] = str(self.prefer_comma).lower()

        try:
            response = requests.post(
                f"{self.base_url}/v2/check",
                data=data,
                timeout=30,
            )
            response.raise_for_status()
            return self._parse_errors(response.json())
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LanguageTool request failed: {e}") from e

    def _parse_errors(self, data: dict[str, Any]) -> list[LanguageToolError]:
        """Parse LanguageTool API response into LanguageToolError objects."""
        errors: list[LanguageToolError] = []
        matches = data.get("matches", [])

        for match in matches:
            # Get context if available
            context = ""
            if "context" in match:
                context = match["context"].get("text", "")

            # Get replacements
            replacements = []
            if "replacements" in match:
                replacements = [r.get("value", "") for r in match["replacements"]]

            errors.append(
                LanguageToolError(
                    message=match.get("message", ""),
                    context=context,
                    rule_id=match.get("rule", {}).get("id", ""),
                    offset=match.get("offset", 0),
                    length=match.get("length", 0),
                    replacements=replacements,
                )
            )

        return errors

    def start_server(
        self,
        install_dir: str = "/opt/LanguageTool",
        jar_pattern: str = "languagetool-server.jar",
    ) -> None:
        """
        Start the LanguageTool server.

        Args:
            install_dir: Directory where LanguageTool is installed.
            jar_pattern: Pattern to find the server JAR file.
        """
        if self.is_server_running():
            return

        # Find the JAR file
        install_path = Path(install_dir)
        jar_file = None

        for jar in install_path.rglob(jar_pattern):
            jar_file = jar
            break

        if not jar_file:
            raise FileNotFoundError(
                f"LanguageTool server JAR not found in {install_dir}. "
                "Please install LanguageTool first."
            )

        # Start the server
        self._server_process = subprocess.Popen(
            ["java", "-jar", str(jar_file), "--port", str(self._get_port_from_url())],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for server to be ready
        for _ in range(30):
            if self.is_server_running():
                return
            time.sleep(1)

        raise RuntimeError("LanguageTool server failed to start within 30 seconds")

    def _get_port_from_url(self) -> int:
        """Extract port from base URL."""
        import re

        match = re.search(r":(\d+)", self.base_url)
        return int(match.group(1)) if match else 8081

    def stop_server(self) -> None:
        """Stop the LanguageTool server."""
        if self._server_process:
            self._server_process.terminate()
            self._server_process.wait(timeout=10)
            self._server_process = None


def format_errors(errors: list[LanguageToolError]) -> str:
    """Format LanguageTool errors for display."""
    if not errors:
        return ""

    lines = [f"LanguageTool encontró {len(errors)} error(es):\n"]
    for i, error in enumerate(errors, 1):
        lines.append(f"  {i}. {error.message}")
        if error.context:
            lines.append(f"     Contexto: ...{error.context}...")
        if error.replacements:
            lines.append(f"     Sugerencias: {', '.join(error.replacements[:3])}")
        lines.append("")

    return "\n".join(lines)

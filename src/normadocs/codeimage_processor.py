"""
Code image processor for NormaDocs.

Transforms specially marked code blocks into styled images for academic documents.
Uses Pygments for syntax highlighting and imgkit for HTML-to-image rendering.
"""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger("normadocs")


class CodeImageResult(NamedTuple):
    """Result of processing a single code block."""

    original_block: str
    image_path: str | None
    success: bool
    error: str | None


class CodeBlock(NamedTuple):
    """Represents a extracted code block."""

    full_match: str
    lang: str
    code: str
    start_pos: int
    end_pos: int


class CodeImageProcessor:
    """
    Detects specially marked code blocks and converts them to images.

    Syntax:
        ```python {code}
        def hello():
            print("world")
        ```

    The {code} marker triggers image generation with a fixed theme (monokai).
    """

    DEFAULT_THEME = "tango"
    DEFAULT_FONT_FAMILY = "Consolas, DejaVu Sans Mono, Liberation Mono, monospace"
    DEFAULT_PADDING = "16px"
    DEFAULT_BG_COLOR = "#ffffff"
    DEFAULT_TEXT_COLOR = "#2e3436"

    CODE_BLOCK_RE = re.compile(
        r"```(\w*)\s*\{code\}\s*\n(.*?)\n```",
        re.DOTALL | re.MULTILINE,
    )

    CSS_TEMPLATE = """
    .code-image {{
        background-color: {bg_color};
        padding: {padding};
        font-family: {font_family};
        font-size: 13px;
        line-height: 1.5;
        color: {text_color};
    }}
    .code-image pre {{
        margin: 0;
        padding: 0;
        background: transparent !important;
        font-family: inherit;
        font-size: inherit;
        line-height: inherit;
    }}
    .code-image .highlight {{
        background: transparent !important;
    }}
    .code-image .hll {{
        background-color: transparent !important;
    }}
    """

    def __init__(
        self,
        output_dir: str | Path | None = None,
        theme: str | None = None,
        image_format: str = "png",
        scale: float = 2.0,
    ) -> None:
        """
        Initialize CodeImageProcessor.

        Args:
            output_dir: Directory to save generated images. Defaults to ./code_images.
            theme: Pygments style to use. Defaults to "monokai".
            image_format: Output format ("png" or "jpeg").
            scale: Device pixel ratio for crisp images. Default 2.0 for Retina.
        """
        self.output_dir = Path(output_dir) if output_dir else Path("code_images")
        self.theme = theme or self.DEFAULT_THEME
        self.image_format = image_format.lower()
        self.scale = scale
        self._imgkit_available = self._check_imgkit()
        self._pygments_available = self._check_pygments()

    @staticmethod
    def _check_imgkit() -> bool:
        """Check if imgkit is available."""
        try:
            import imgkit  # noqa: F401

            return True
        except ImportError:
            return False

    @staticmethod
    def _check_pygments() -> bool:
        """Check if Pygments is available."""
        try:
            import pygments  # noqa: F401

            return True
        except ImportError:
            return False

    def is_available(self) -> bool:
        """Check if all required dependencies are installed."""
        return self._imgkit_available and self._pygments_available

    def _get_pygments_html(self, code: str, lang: str) -> str:
        """Generate highlighted HTML from code using Pygments."""
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name, guess_lexer

        try:
            lexer = get_lexer_by_name(lang)
        except Exception:
            try:
                lexer = guess_lexer(code)
            except Exception:
                from pygments.lexers import TextLexer

                lexer = TextLexer()

        formatter = HtmlFormatter(
            style=self.theme,
            cssclass="highlight",
            nowrap=True,
        )

        highlighted = highlight(code, lexer, formatter)
        pygments_styles = formatter.get_style_defs('.highlight')

        custom_css = self.CSS_TEMPLATE.format(
            bg_color=self.DEFAULT_BG_COLOR,
            padding=self.DEFAULT_PADDING,
            font_family=self.DEFAULT_FONT_FAMILY,
            text_color=self.DEFAULT_TEXT_COLOR,
        )

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{pygments_styles}
{custom_css}
</style>
</head>
<body>
<div class="code-image">
<pre>{highlighted}</pre>
</div>
</body>
</html>
"""
        return html

    def _generate_image(self, html: str, image_path: Path) -> bool:
        """Render HTML to image using imgkit."""
        import imgkit

        options = {
            "format": self.image_format,
            "quality": "100",
            "enable-local-file-access": "",
        }

        try:
            imgkit.from_string(html, str(image_path), options=options)
            return True
        except Exception as e:
            logger.error("Failed to generate image: %s", e)
            return False

    def _extract_code_blocks(self, text: str) -> list[CodeBlock]:
        """Extract all {code} marked code blocks from text."""
        blocks: list[CodeBlock] = []
        for match in self.CODE_BLOCK_RE.finditer(text):
            lang = match.group(1) or "text"
            code = match.group(2)
            blocks.append(
                CodeBlock(
                    full_match=match.group(0),
                    lang=lang,
                    code=code,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )
        return blocks

    def _hash_content(self, content: str) -> str:
        """Generate short hash for content to use in filename."""
        return hashlib.md5(content.encode("utf-8"), usedforsecurity=False).hexdigest()[:8]

    def _make_image_filename(self, index: int, lang: str, content: str) -> str:
        """Create a descriptive filename for the image."""
        short_hash = self._hash_content(content)
        lang_suffix = lang if lang != "text" else "code"
        return f"code_image_{index:03d}_{lang_suffix}_{short_hash}.{self.image_format}"

    def process(self, text: str) -> tuple[str, list[CodeImageResult]]:
        """
        Process text, converting marked code blocks to images.

        Args:
            text: Markdown text with potential {code} blocks.

        Returns:
            Tuple of (modified text with image references, list of processing results).
        """
        results: list[CodeImageResult] = []

        if not self.is_available():
            logger.warning(
                "Code image processing unavailable. Install with: pip install normadocs[codeimage]"
            )
            return text, results

        blocks = self._extract_code_blocks(text)
        if not blocks:
            return text, results

        self.output_dir.mkdir(parents=True, exist_ok=True)

        modified_text = text
        offset = 0

        for i, block in enumerate(blocks, 1):
            image_filename = self._make_image_filename(i, block.lang, block.code)
            image_path = self.output_dir / image_filename

            if image_path.exists():
                logger.debug("Using cached image: %s", image_path)
                image_ref = f"![{block.lang} code]({image_path.as_posix()})"
                results.append(
                    CodeImageResult(
                        original_block=block.full_match,
                        image_path=str(image_path),
                        success=True,
                        error=None,
                    )
                )
            else:
                html = self._get_pygments_html(block.code, block.lang)
                success = self._generate_image(html, image_path)

                if success:
                    image_ref = f"![{block.lang} code]({image_path.as_posix()})"
                    results.append(
                        CodeImageResult(
                            original_block=block.full_match,
                            image_path=str(image_path),
                            success=True,
                            error=None,
                        )
                    )
                    logger.info("Generated code image: %s", image_path.name)
                else:
                    image_ref = block.full_match
                    results.append(
                        CodeImageResult(
                            original_block=block.full_match,
                            image_path=None,
                            success=False,
                            error="Failed to render image",
                        )
                    )
                    logger.warning("Failed to generate image for block %d", i)

            adjusted_start = block.start_pos + offset
            adjusted_end = block.end_pos + offset
            modified_text = (
                modified_text[:adjusted_start] + image_ref + modified_text[adjusted_end:]
            )
            offset += len(image_ref) - (block.end_pos - block.start_pos)

        return modified_text, results


def is_code_block(text: str) -> bool:
    """
    Check if text contains any {code} marked code blocks.

    Args:
        text: Text to check.

    Returns:
        True if text contains {code} blocks.
    """
    return bool(CodeImageProcessor.CODE_BLOCK_RE.search(text))

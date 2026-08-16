"""Unit tests for preprocessor line-break and math-block handling."""

import unittest

from normadocs.config import PAGEBREAK_OPENXML
from normadocs.preprocessor import MarkdownPreprocessor


def _process(text: str) -> str:
    """Run the preprocessor and return the transformed Markdown."""
    result, _meta = MarkdownPreprocessor().process(text)
    return result


class TestHardLineBreaks(unittest.TestCase):
    """Intentional hard breaks must survive paragraph joining."""

    def test_backslash_break_is_preserved(self):
        """A trailing backslash keeps its own line so Pandoc emits <w:br/>."""
        output = _process("# Título\n\nprimera línea\\\nsegunda línea\n\nTexto normal siguiente.\n")
        self.assertIn("primera línea\\\nsegunda línea", output)

    def test_two_trailing_spaces_become_backslash(self):
        """The fragile two-space break is normalized to the backslash form."""
        output = _process("# Título\n\nverso uno  \nverso dos\n")
        self.assertIn("verso uno\\\nverso dos", output)

    def test_wrapped_prose_is_still_joined(self):
        """Ordinary soft-wrapped prose continues to be joined into a paragraph."""
        output = _process("# Título\n\nEste texto está envuelto a\nsetenta y dos caracteres.\n")
        self.assertIn("envuelto a setenta y dos caracteres.", output)
        self.assertNotIn("a\nsetenta", output)

    def test_double_backslash_is_not_a_break(self):
        """An escaped backslash at end of line is not treated as a break."""
        output = _process("# Título\n\nruta completa\\\\\nfinal\n")
        # "\\\\" is an even count: no hard-break normalization should apply
        self.assertNotIn("completo\\\\\\", output)


class TestMathBlocks(unittest.TestCase):
    """Display math blocks must pass through verbatim."""

    def test_multiline_math_block_is_not_joined(self):
        """Interior lines of a $$ block keep their physical newlines."""
        math_lines = "$$\n\\begin{aligned}\nx &= 1 + 2 \\\\\ny &= 3\n\\end{aligned}\n$$\n"
        output = _process("# Métodos\n\ntexto previo del párrafo.\n" + math_lines)
        self.assertIn("\\begin{aligned}\nx &= 1 + 2 \\\\\ny &= 3\n\\end{aligned}", output)

    def test_single_line_display_math_stays_separate(self):
        """A one-line $$…$$ equation is not merged into surrounding prose."""
        output = _process("# Métodos\n\npárrafo antes.\n$$E = mc^2$$\npárrafo después.\n")
        lines = output.split("\n")
        self.assertIn("$$E = mc^2$$", lines)
        self.assertNotIn("párrafo antes. $$E = mc^2$$", output)

    def test_tag_is_stripped_from_math(self):
        """\\tag{n} is removed: OMML cannot carry it and numbering is automatic."""
        output = _process("# Métodos\n\n$$\nx = y \\tag{3}\n$$\n")
        self.assertNotIn("\\tag", output)
        self.assertIn("x = y", output)


class TestMathFenceConversion(unittest.TestCase):
    """GitHub-style ```math fences become Pandoc $$ display math."""

    def test_math_fence_becomes_dollars(self):
        output = _process("# Métodos\n\n```math\nE = mc^2\n```\n")
        self.assertIn("$$\nE = mc^2\n$$", output)
        self.assertNotIn("```math", output)

    def test_math_fence_content_not_joined(self):
        """Multiline fence content survives the line joiner unchanged."""
        output = _process("# Métodos\n\n```math\n\\begin{cases}\na = 1\nb = 2\n\\end{cases}\n```\n")
        self.assertIn("a = 1\nb = 2", output)


class TestExplicitPageBreaks(unittest.TestCase):
    """Raw LaTeX page-break commands become real OpenXML page breaks."""

    def test_newpage_becomes_openxml_pagebreak(self):
        output = _process("# Uno\n\ntexto uno.\n\n\\newpage\n\n# Dos\n\ntexto dos.\n")
        self.assertIn('<w:br w:type="page"/>', output)
        self.assertNotIn("\\newpage", output)

    def test_pagebreak_becomes_openxml_pagebreak(self):
        output = _process("# Uno\n\ntexto uno.\n\n\\pagebreak\n\n# Dos\n\ntexto dos.\n")
        self.assertIn(PAGEBREAK_OPENXML.strip(), output)
        self.assertNotIn("\\pagebreak", output)


if __name__ == "__main__":
    unittest.main()

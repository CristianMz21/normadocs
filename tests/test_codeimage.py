"""
Tests for codeimage_processor module.
"""

import unittest
from unittest.mock import patch


class TestCodeImageProcessor(unittest.TestCase):
    """Tests for CodeImageProcessor class."""

    def setUp(self):
        self.maxDiff = None

    def test_code_block_regex_basic(self):
        """Test basic {code} block extraction."""
        from normadocs.codeimage_processor import CodeImageProcessor

        text = """Here is some text.

```python {code}
def hello():
    print("world")
```

More text.
"""
        processor = CodeImageProcessor()
        blocks = processor._extract_code_blocks(text)

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].lang, "python")
        self.assertIn("def hello", blocks[0].code)

    def test_code_block_regex_multiple(self):
        """Test multiple {code} blocks."""
        from normadocs.codeimage_processor import CodeImageProcessor

        text = """```python {code}
code1
```
```javascript {code}
code2
```
```rust {code}
code3
```
"""
        processor = CodeImageProcessor()
        blocks = processor._extract_code_blocks(text)

        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0].lang, "python")
        self.assertEqual(blocks[1].lang, "javascript")
        self.assertEqual(blocks[2].lang, "rust")

    def test_code_block_regex_no_marker(self):
        """Test that regular code blocks are NOT matched."""
        from normadocs.codeimage_processor import CodeImageProcessor

        text = """```python
def hello():
    print("world")
```
"""
        processor = CodeImageProcessor()
        blocks = processor._extract_code_blocks(text)

        self.assertEqual(len(blocks), 0)

    def test_code_block_regex_empty_language(self):
        """Test {code} block with no language specified."""
        from normadocs.codeimage_processor import CodeImageProcessor

        text = """```{code}
some code
```
"""
        processor = CodeImageProcessor()
        blocks = processor._extract_code_blocks(text)

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].lang, "text")
        self.assertIn("some code", blocks[0].code)

    def test_is_code_block_true(self):
        """Test is_code_block returns True for text with {code} blocks."""
        from normadocs.codeimage_processor import is_code_block

        text = """```python {code}
code
```
"""
        self.assertTrue(is_code_block(text))

    def test_is_code_block_false(self):
        """Test is_code_block returns False for regular code."""
        from normadocs.codeimage_processor import is_code_block

        text = """```python
code
```
"""
        self.assertFalse(is_code_block(text))

    def test_is_code_block_false_plain_text(self):
        """Test is_code_block returns False for plain text."""
        from normadocs.codeimage_processor import is_code_block

        text = "Just some plain text without code blocks."
        self.assertFalse(is_code_block(text))

    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_pygments")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_imgkit")
    def test_is_available_true(self, mock_imgkit, mock_pygments):
        """Test is_available returns True when deps installed."""
        mock_imgkit.return_value = True
        mock_pygments.return_value = True

        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        self.assertTrue(processor.is_available())

    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_pygments")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_imgkit")
    def test_is_available_false_pygments(self, mock_imgkit, mock_pygments):
        """Test is_available returns False when Pygments missing."""
        mock_imgkit.return_value = True
        mock_pygments.return_value = False

        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        self.assertFalse(processor.is_available())

    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_pygments")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_imgkit")
    def test_is_available_false_imgkit(self, mock_imgkit, mock_pygments):
        """Test is_available returns False when imgkit missing."""
        mock_imgkit.return_value = False
        mock_pygments.return_value = True

        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        self.assertFalse(processor.is_available())

    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_pygments")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_imgkit")
    def test_process_no_blocks(self, mock_imgkit, mock_pygments):
        """Test process returns unchanged text when no {code} blocks."""
        mock_imgkit.return_value = True
        mock_pygments.return_value = True

        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        text = "Just plain text without code blocks."
        result, results = processor.process(text)

        self.assertEqual(result, text)
        self.assertEqual(len(results), 0)

    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_pygments")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_imgkit")
    def test_process_unavailable(self, mock_imgkit, mock_pygments):
        """Test process returns unchanged text when deps unavailable."""
        mock_imgkit.return_value = False
        mock_pygments.return_value = False

        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        text = """```python {code}
code
```
"""
        result, results = processor.process(text)

        self.assertEqual(result, text)
        self.assertEqual(len(results), 0)

    def test_hash_content_consistent(self):
        """Test that hash is consistent for same content."""
        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        hash1 = processor._hash_content("def hello():")
        hash2 = processor._hash_content("def hello():")
        hash3 = processor._hash_content("def world():")

        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)

    def test_make_image_filename(self):
        """Test image filename generation."""
        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        filename = processor._make_image_filename(1, "python", "def hello():")

        self.assertTrue(filename.startswith("code_image_001_python_"))
        self.assertTrue(filename.endswith(".png"))
        self.assertEqual(len(filename), len("code_image_001_python_") + 8 + 4)

    def test_make_image_filename_text_lang(self):
        """Test image filename with text language."""
        from normadocs.codeimage_processor import CodeImageProcessor

        processor = CodeImageProcessor()
        filename = processor._make_image_filename(5, "text", "some code")

        self.assertTrue(filename.startswith("code_image_005_code_"))
        self.assertIn("5", filename[:20])


class TestCodeImageProcessorIntegration(unittest.TestCase):
    """Integration-like tests that mock external dependencies."""

    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_pygments")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_imgkit")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._generate_image")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._get_pygments_html")
    def test_process_replaces_block_with_image_ref(
        self, mock_html, mock_gen, mock_imgkit, mock_pygments
    ):
        """Test that code block is replaced with markdown image reference."""
        mock_imgkit.return_value = True
        mock_pygments.return_value = True
        mock_gen.return_value = True
        mock_html.return_value = "<html/>"

        import tempfile

        from normadocs.codeimage_processor import CodeImageProcessor

        with tempfile.TemporaryDirectory() as tmpdir:
            processor = CodeImageProcessor(output_dir=tmpdir)
            text = """```python {code}
def hello():
    print("world")
```"""
            result, results = processor.process(text)

            self.assertNotIn("```python {code}", result)
            self.assertIn("![python code](", result)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].success)

    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_pygments")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._check_imgkit")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._generate_image")
    @patch("normadocs.codeimage_processor.CodeImageProcessor._get_pygments_html")
    def test_process_multiple_blocks(self, mock_html, mock_gen, mock_imgkit, mock_pygments):
        """Test processing of multiple code blocks."""
        mock_imgkit.return_value = True
        mock_pygments.return_value = True
        mock_gen.return_value = True
        mock_html.return_value = "<html/>"

        import tempfile

        from normadocs.codeimage_processor import CodeImageProcessor

        with tempfile.TemporaryDirectory() as tmpdir:
            processor = CodeImageProcessor(output_dir=tmpdir)
            text = """First block:

```python {code}
print("hello")
```

Second block:

```javascript {code}
console.log("world")
```
"""
            result, results = processor.process(text)

            self.assertEqual(len(results), 2)
            self.assertTrue(all(r.success for r in results))
            self.assertIn("![python code](", result)
            self.assertIn("![javascript code](", result)


if __name__ == "__main__":
    unittest.main()

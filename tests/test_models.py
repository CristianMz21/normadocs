"""
Tests for Data Models.
"""

import unittest

from normadocs.models import DocumentMetadata, ProcessOptions


class TestModels(unittest.TestCase):
    def test_document_metadata_defaults(self):
        meta = DocumentMetadata()
        self.assertEqual(meta.title, "Sin Título")
        self.assertIsNone(meta.author)

    def test_from_dict_known_fields(self):
        data = {
            "title": "My Paper",
            "author": "John Doe",
            "date": "2023-01-01",
            "unknown_field": "some value",
        }
        meta = DocumentMetadata.from_dict(data)
        self.assertEqual(meta.title, "My Paper")
        self.assertEqual(meta.author, "John Doe")
        self.assertEqual(meta.date, "2023-01-01")
        # unknown_field should go to extra
        self.assertIn("unknown_field", meta.extra)
        self.assertEqual(meta.extra["unknown_field"], "some value")

    def test_process_options(self):
        opts = ProcessOptions(input_file="input.md", output_dir="out")
        self.assertEqual(opts.input_file, "input.md")
        self.assertEqual(opts.output_format, "docx")  # default


if __name__ == "__main__":
    unittest.main()

"""
Tests for standards/__init__.py - StandardLoader class.
"""

import tempfile
import unittest
from pathlib import Path

import yaml

from normadocs.standards import APA7_CONFIG, ICONTEC_CONFIG, StandardLoader


class TestStandardLoader(unittest.TestCase):
    def test_load_apa7_returns_dict(self):
        loader = StandardLoader()
        config = loader.load("apa7")
        self.assertIsInstance(config, dict)
        self.assertEqual(config["name"], "APA 7th Edition")

    def test_load_apa_alias(self):
        loader = StandardLoader()
        config = loader.load("apa")
        self.assertEqual(config["name"], "APA 7th Edition")

    def test_load_icontec_returns_dict(self):
        loader = StandardLoader()
        config = loader.load("icontec")
        self.assertIsInstance(config, dict)
        self.assertEqual(config["name"], "ICONTEC (NTC 1486)")

    def test_load_nonexistent_raises(self):
        loader = StandardLoader()
        with self.assertRaises(FileNotFoundError):
            loader.load("nonexistent")

    def test_load_raw_apa7(self):
        loader = StandardLoader()
        config = loader.load_raw("apa7")
        self.assertIsInstance(config, dict)
        self.assertIn("fonts", config)

    def test_load_raw_returns_yaml_directly(self):
        loader = StandardLoader()
        raw = loader.load_raw("apa7")
        self.assertIn("fonts", raw)
        self.assertIn("citation_style", raw)
        self.assertEqual(raw["citation_style"], "apa")

    def test_list_available(self):
        loader = StandardLoader()
        available = loader.list_available()
        self.assertIn("apa7", available)
        self.assertIn("icontec", available)

    def test_exists_true(self):
        loader = StandardLoader()
        self.assertTrue(loader.exists("apa7"))
        self.assertTrue(loader.exists("apa"))
        self.assertTrue(loader.exists("icontec"))

    def test_exists_false(self):
        loader = StandardLoader()
        self.assertFalse(loader.exists("nonexistent"))
        self.assertFalse(loader.exists("xyz"))

    def test_load_merges_with_defaults(self):
        loader = StandardLoader()
        config = loader.load("apa7")
        self.assertEqual(config["citation_style"], "apa")
        self.assertIn("name", config)

    def test_preloaded_configs_exist(self):
        self.assertIsInstance(APA7_CONFIG, dict)
        self.assertEqual(APA7_CONFIG["name"], "APA 7th Edition")
        self.assertIsInstance(ICONTEC_CONFIG, dict)
        self.assertEqual(ICONTEC_CONFIG["name"], "ICONTEC (NTC 1486)")


class TestStandardLoaderCustomDir(unittest.TestCase):
    def test_load_from_custom_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_yaml = {
                "fonts": {"body": {"name": "Custom Font", "size": 14}},
                "margins": {"unit": "inches", "top": 2.0, "bottom": 2.0, "left": 1.5, "right": 1.5},
            }
            yaml_path = Path(tmpdir) / "custom.yaml"
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(custom_yaml, f)

            loader = StandardLoader(standards_dir=Path(tmpdir))
            config = loader.load("custom")
            self.assertEqual(config["fonts"]["body"]["name"], "Custom Font")
            self.assertEqual(config["fonts"]["body"]["size"], 14)
            self.assertEqual(config["citation_style"], "apa")

    def test_list_from_custom_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir).joinpath("style1.yaml").write_text("key: value1", encoding="utf-8")
            Path(tmpdir).joinpath("style2.yaml").write_text("key: value2", encoding="utf-8")

            loader = StandardLoader(standards_dir=Path(tmpdir))
            available = loader.list_available()
            self.assertIn("style1", available)
            self.assertIn("style2", available)


if __name__ == "__main__":
    unittest.main()

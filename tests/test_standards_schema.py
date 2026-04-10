"""
Tests for standards/schema.py - default configs and merge utilities.
"""

import unittest

from normadocs.standards.schema import (
    deep_copy,
    deep_merge,
    get_default_config,
    merge_with_defaults,
)


class TestGetDefaultConfig(unittest.TestCase):
    def test_apa_returns_apa7_config(self):
        config = get_default_config("apa")
        self.assertEqual(config["name"], "APA 7th Edition")
        self.assertEqual(config["citation_style"], "apa")

    def test_apa7_returns_apa7_config(self):
        config = get_default_config("apa7")
        self.assertEqual(config["name"], "APA 7th Edition")

    def test_icontec_returns_icontec_config(self):
        config = get_default_config("icontec")
        self.assertEqual(config["name"], "ICONTEC (NTC 1486)")
        self.assertEqual(config["citation_style"], "icontec")

    def test_ieee_returns_ieee_config(self):
        config = get_default_config("ieee")
        self.assertEqual(config["name"], "IEEE 8th Edition")
        self.assertEqual(config["citation_style"], "ieee")

    def test_unknown_style_returns_apa7_fallback(self):
        config = get_default_config("unknown")
        self.assertEqual(config["name"], "APA 7th Edition")

    def test_apa7_config_has_required_keys(self):
        config = get_default_config("apa7")
        self.assertIn("fonts", config)
        self.assertIn("margins", config)
        self.assertIn("spacing", config)
        self.assertIn("page_setup", config)
        self.assertIn("tables", config)
        self.assertIn("figures", config)
        self.assertIn("cover", config)

    def test_icontec_config_margins_in_cm(self):
        config = get_default_config("icontec")
        self.assertEqual(config["margins"]["unit"], "cm")
        self.assertEqual(config["margins"]["top"], 3.0)

    def test_ieee_config_single_spacing(self):
        config = get_default_config("ieee")
        self.assertEqual(config["spacing"]["line"], "single")


class TestDeepCopy(unittest.TestCase):
    def test_simple_dict_copy(self):
        original = {"a": 1, "b": 2}
        result = deep_copy(original)
        self.assertEqual(result, original)
        self.assertIsNot(result, original)

    def test_nested_dict_copy(self):
        original = {"a": {"b": {"c": 1}}}
        result = deep_copy(original)
        self.assertEqual(result, original)
        self.assertIsNot(result, original)
        self.assertIsNot(result["a"], original["a"])
        self.assertIsNot(result["a"]["b"], original["a"]["b"])

    def test_copy_does_not_affect_original(self):
        original = {"fonts": {"body": {"name": "Arial"}}}
        result = deep_copy(original)
        result["fonts"]["body"]["name"] = "Times New Roman"
        self.assertEqual(original["fonts"]["body"]["name"], "Arial")


class TestDeepMerge(unittest.TestCase):
    def test_merge_simple_values(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        deep_merge(base, override)
        self.assertEqual(base["a"], 1)
        self.assertEqual(base["b"], 3)
        self.assertEqual(base["c"], 4)

    def test_merge_nested_dicts(self):
        base = {"fonts": {"body": {"name": "Arial", "size": 12}}}
        override = {"fonts": {"body": {"size": 14}}}
        deep_merge(base, override)
        self.assertEqual(base["fonts"]["body"]["name"], "Arial")
        self.assertEqual(base["fonts"]["body"]["size"], 14)

    def test_merge_adds_new_nested_keys(self):
        base = {"fonts": {"body": {"name": "Arial"}}}
        override = {"fonts": {"heading": {"name": "Times New Roman"}}}
        deep_merge(base, override)
        self.assertEqual(base["fonts"]["body"]["name"], "Arial")
        self.assertEqual(base["fonts"]["heading"]["name"], "Times New Roman")

    def test_merge_replaces_non_dict_with_dict(self):
        base = {"a": 1}
        override = {"a": {"b": 2}}
        deep_merge(base, override)
        self.assertEqual(base["a"], {"b": 2})


class TestMergeWithDefaults(unittest.TestCase):
    def test_partial_config_gets_defaults(self):
        partial = {"fonts": {"body": {"name": "Custom Font"}}}
        result = merge_with_defaults(partial, "apa7")
        self.assertEqual(result["fonts"]["body"]["name"], "Custom Font")
        self.assertEqual(result["fonts"]["body"]["size"], 12)
        self.assertEqual(result["name"], "APA 7th Edition")

    def test_empty_config_returns_full_defaults(self):
        result = merge_with_defaults({}, "apa7")
        self.assertEqual(result["fonts"]["body"]["name"], "Times New Roman")
        self.assertEqual(result["spacing"]["line"], "double")

    def test_override_preserves_other_sections(self):
        config = {"spacing": {"line": "single"}}
        result = merge_with_defaults(config, "apa7")
        self.assertEqual(result["spacing"]["line"], "single")
        self.assertEqual(result["fonts"]["body"]["name"], "Times New Roman")

    def test_does_not_mutate_original(self):
        original = {"fonts": {"body": {"name": "Custom"}}}
        original_copy = original.copy()
        merge_with_defaults(original, "apa7")
        self.assertEqual(original, original_copy)


if __name__ == "__main__":
    unittest.main()

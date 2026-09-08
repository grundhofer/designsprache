"""Regression checks for the source contracts and palette comparison."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import build
from mobile import catalog as mobile
from tools.catalog_checks import check_catalog, check_demo, check_fact_sheet

spec = importlib.util.spec_from_file_location("palette_check", build.ROOT / "tools/palette-check.py")
palette = importlib.util.module_from_spec(spec)
spec.loader.exec_module(palette)


class CatalogChecks(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((build.SRC / "swiss.json").read_text())
        self.slugs = [s for _, _, group in build.ORDER_DE for s in group]
        self.fonts = {s.split(":")[0].replace("+", " ") for s in build.FONT_SPECS}

    def errors(self, data):
        return check_fact_sheet(data, "swiss", build.ORDER_DE[0][0], self.slugs, self.fonts)

    def test_entire_catalog_satisfies_source_contract(self):
        self.assertEqual(check_catalog(build.ROOT, build.ORDER_DE, build.ORDER_EN, build.FONT_SPECS), [])

    def test_mobile_adaptations_cover_catalog_and_fail_on_missing_entry(self):
        for lang in ('de', 'en'):
            css, script = mobile.assets(self.slugs, lang)
            for slug in self.slugs:
                self.assertIn('.m-app.m-' + slug, css)
                self.assertIn(mobile.NOTES[slug][lang == 'en'], script)
                font = mobile.THEMES[slug][-2]
                self.assertTrue(font in self.fonts or font in ('Times New Roman', 'system-ui'), font)
            with self.assertRaises(ValueError):
                mobile.assets(self.slugs + ['future-style'], lang)

    def test_invalid_metadata_fails_with_field_name(self):
        for key, value in [("scores", {"longevity": True}), ("params", {}),
                           ("palette", ["red"]), ("combinesWith", ["missing"]),
                           ("googleFonts", ["Unloaded Font"]), ("finder", None),
                           ("sources", [{"title": "Unsafe", "url": "javascript:alert(1)"}])]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data[key] = value
                self.assertTrue(any(key in error for error in self.errors(data)))

    def test_finder_enumerations_and_ranges(self):
        for key, value in [("a11y", 0), ("mode", "dim"), ("tone", ["calm", "calm"]),
                           ("fits", ["unknown", "data"]), ("signature", "x" * 111)]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data["finder"][key] = value
                self.assertTrue(self.errors(data))

    def test_translation_and_inventory_drift_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(build.SRC, root / "styles")
            path = root / "styles/swiss.en.json"
            data = json.loads(path.read_text())
            data["scores"]["effort"] = 5
            data["finder"]["a11y"] = 1
            path.write_text(json.dumps(data))
            demo = root / "styles/swiss.en.html"
            demo.write_text(demo.read_text().replace("<style>", "<style>\n/* translation drift */"))
            (root / "styles/unlisted.json").write_text("{}")
            errors = check_catalog(root, build.ORDER_DE, build.ORDER_EN, build.FONT_SPECS)
            for message in ["scores differs", "finder attributes differ", "demo CSS differs", "unlisted source"]:
                self.assertTrue(any(message in e for e in errors), errors)

    def test_demo_must_remain_inert_and_complete(self):
        raw = (build.SRC / "swiss.html").read_text()
        for changed in [raw + "<script>alert(1)</script>", raw.replace("readonly", ""),
                        raw.replace("Nexus", "Unrelated"), raw.replace('<div class="style-swiss"',
                        '<div onclick="alert(1)" class="style-swiss"')]:
            self.assertTrue(check_demo(changed, "swiss", "de"))

    def test_css_rejects_leaks_and_global_resources(self):
        for css in [".style-swiss-other { color:red; }", "body { color:red; }",
                    "@media (width > 1px) { body { color:red; } }",
                    "@keyframes global { from { opacity:0; } }",
                    "@font-face { font-family:unexpected; }",
                    '@import "https://example.com/style.css";',
                    '.style-swiss { background:url("https://example.com/a.svg"); }',
                    ".style-swiss + body { color:red; }", ".style-swiss { color:red;"]:
            with self.subTest(css=css), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    build.check_scoping([css], ["swiss"], "")

    def test_css_allows_quoted_punctuation_and_scoped_animation(self):
        css = '''.style-swiss { content:"{,}"; }
        @media (max-width: 500px) { .style-swiss .row { color:red; } }
        @keyframes swiss-blink { from { opacity:0; } to { opacity:1; } }'''
        build.check_scoping([css], ["swiss"], "")


class PaletteChecks(unittest.TestCase):
    def test_one_color_cannot_count_twice(self):
        self.assertEqual(len(palette.color_matches(["#FF0000"], ["#FF0000", "#FE0000"], 2)), 1)
        self.assertEqual(len(palette.color_matches(["#FF0000", "#FE0000"], ["#FF0000"], 2)), 1)

    def test_two_distinct_colors_are_a_match(self):
        self.assertEqual(len(palette.color_matches(["#FF0000", "#0000FF"], ["#FE0000", "#0000FE"], 2)), 2)

    def test_matching_can_reassign_a_greedy_choice(self):
        distances = {("a", "x"): 0.1, ("a", "y"): 0.2, ("b", "x"): 0.3, ("b", "y"): 9}
        with patch.object(palette, "delta_e", side_effect=lambda x, y: distances[x, y]):
            self.assertEqual(len(palette.color_matches(["a", "b"], ["x", "y"], 2)), 2)

    def test_shorthand_hex_is_not_dropped(self):
        self.assertEqual(palette._oklab("#f60"), palette._oklab("#FF6600"))
        self.assertIn("#FF6600", palette.load()["portal-density"]["bunt"])


if __name__ == "__main__":
    unittest.main()

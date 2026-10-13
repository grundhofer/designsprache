"""Self-hosted fonts: provenance, licenses and no requests to other hosts. Run python3 build.py first."""
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import urlsplit

import build
from tools.catalog_checks import check_fonts, reserved_font_names, unicode_ranges

MANIFEST = json.loads((build.FONTS / "fonts.json").read_text(encoding="utf-8"))
SHEETS = {"catalog": build.catalog_fonts(), "home": build.HOME_FONTS}
# Attributes that make the browser fetch something, per element.
FETCHING = {"script": ("src",), "img": ("src", "srcset"), "source": ("src", "srcset"), "iframe": ("src",),
            "embed": ("src",), "object": ("data",), "video": ("src", "poster"), "audio": ("src",),
            "track": ("src",), "input": ("src",), "image": ("href", "xlink:href"), "use": ("href", "xlink:href")}
FETCHING_LINKS = {"stylesheet", "preload", "modulepreload", "prefetch", "preconnect", "dns-prefetch", "icon",
                  "manifest", "apple-touch-icon", "mask-icon"}


def is_local(url):
    url = url.strip()
    return url.startswith(("data:", "#")) or not (urlsplit(url).scheme or url.startswith("//"))


def css_urls(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return ([m.group(2) for m in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", css, re.S)]
            + re.findall(r"@import\s+(?:url\()?\s*['\"]?([^'\")\s;]+)", css))


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls, self.styles, self.in_style = [], [], False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and FETCHING_LINKS & set((attrs.get("rel") or "").lower().split()):
            self.urls.append(attrs.get("href") or "")
        for key in FETCHING.get(tag, ()):
            if attrs.get(key):
                self.urls += [part.split()[0] for part in attrs[key].split(",") if part.strip()] if key == "srcset" else [attrs[key]]
        if attrs.get("style"):
            self.urls += css_urls(attrs["style"])
        self.in_style = tag == "style"

    def handle_endtag(self, tag):
        self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)


def published(*suffixes):
    return sorted(p for p in build.DOCS.rglob("*") if p.suffix in suffixes)


class FontChecks(unittest.TestCase):
    def test_manifest_matches_files_licenses_and_requested_specs(self):
        self.assertEqual(check_fonts(build.ROOT, build.catalog_fonts() + build.HOME_FONTS), [])

    def test_every_catalog_family_is_served(self):
        families = {s.split(":")[0].replace("+", " ") for s in build.catalog_fonts()}
        for path in build.SRC.glob("*.json"):
            for family in json.loads(path.read_text(encoding="utf-8"))["googleFonts"]:
                self.assertIn(family, families, path.name)
        css = (build.DOCS / "fonts" / "catalog.css").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"font-family:'([^']+)'", css)), families)

    def test_stylesheets_reference_published_files_with_the_old_display_mode(self):
        for sheet, specs in SHEETS.items():
            css = (build.DOCS / "fonts" / f"{sheet}.css").read_text(encoding="utf-8")
            faces = re.findall(r"@font-face \{[^}]*\}", css)
            self.assertEqual(len(faces), sum(len(MANIFEST["specs"][s]["faces"]) for s in specs), sheet)
            for face in faces:
                self.assertIn("font-display:swap;", face)
                for url in css_urls(face):
                    self.assertTrue(is_local(url), url)
                    self.assertTrue((build.DOCS / "fonts" / url).is_file(), url)
        self.assertIn("font-display:block;", build.font_css(build.CHROME_FONTS, "block", "fonts/"))

    def test_published_font_files_are_byte_identical_to_the_recorded_sources(self):
        for rel, info in MANIFEST["files"].items():
            data = (build.DOCS / "fonts" / rel).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), info["sha256"], rel)
            self.assertTrue(info["source"].startswith("https://"), rel)
            self.assertEqual(data[:4], b"wOF2" if rel.endswith(".woff2") else b"\x00\x01\x00\x00", rel)

    def test_every_family_ships_its_license_text(self):
        css = "".join((build.DOCS / "fonts" / f"{sheet}.css").read_text(encoding="utf-8") for sheet in SHEETS)
        for family in set(re.findall(r"font-family:'([^']+)'", css)):
            info = MANIFEST["families"][family]
            repo = build.FONTS / info["license"]
            self.assertIn(b"SIL OPEN FONT LICENSE Version 1.1", repo.read_bytes(), family)
            self.assertEqual((build.DOCS / "fonts" / info["license"]).read_bytes(), repo.read_bytes(), family)

    def test_reserved_font_names_are_only_used_on_unmodified_release_files(self):
        for family, info in MANIFEST["families"].items():
            names = reserved_font_names((build.FONTS / info["license"]).read_text(encoding="utf-8"))
            files = [f["file"] for spec, entry in MANIFEST["specs"].items()
                     if spec.split(":")[0].replace("+", " ") == family for f in entry["faces"]]
            if any(n.casefold() in family.casefold() for n in names):
                self.assertTrue(all(f.startswith("release/") for f in files), family)
                self.assertEqual(info["origin"], "release", family)

    def test_release_faces_cover_every_character_google_declared(self):
        # The browser tries a family only for characters inside a declared unicode-range. Ranges that listed
        # just the characters in Google's files sent U+2011 in "Stil&#8209;Katalog" to a system font.
        for spec, entry in MANIFEST["specs"].items():
            if MANIFEST["families"][spec.split(":")[0].replace("+", " ")]["origin"] != "release":
                continue
            self.assertTrue(entry["google"], spec)
            for old in entry["google"]:
                key = (old["style"], old["weight"], old.get("stretch"))
                have = set().union(*(unicode_ranges(f["range"]) for f in entry["faces"]
                                     if (f["style"], f["weight"], f.get("stretch")) == key))
                self.assertLessEqual(unicode_ranges(old["range"]), have, (spec, key))
                self.assertIn(0x2011, have, (spec, key))

    def test_check_rejects_release_faces_that_drop_part_of_the_google_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fonts" / "release").mkdir(parents=True)
            (root / "fonts" / "licenses").mkdir()
            font = root / "fonts" / "release" / "a.ttf"
            font.write_bytes(b"\x00\x01\x00\x00")
            lic = root / "fonts" / "licenses" / "OFL-Test.txt"
            lic.write_text("Copyright 2020 Test\nThis Font Software is licensed under the SIL Open Font License, Version 1.1.\n")
            face = {"style": "normal", "weight": "400", "range": "U+0020-007E, U+2010", "file": "release/a.ttf"}
            manifest = {
                "families": {"Test": {"license": "licenses/OFL-Test.txt", "reserved_font_names": [], "origin": "release",
                                      "license_sha256": hashlib.sha256(lic.read_bytes()).hexdigest()}},
                "specs": {"Test": {"google": [{"style": "normal", "weight": "400", "range": "U+0020-007E, U+2000-206F"}],
                                   "faces": [face]}},
                "files": {"release/a.ttf": {"sha256": hashlib.sha256(font.read_bytes()).hexdigest()}},
            }
            (root / "fonts" / "fonts.json").write_text(json.dumps(manifest))
            errors = check_fonts(root, ["Test"])
            self.assertEqual(len(errors), 1, errors)
            self.assertIn("misses 111 characters of the former Google range, first U+2000", errors[0])
            face["range"] = "U+0020-007E, U+2000-206F"
            (root / "fonts" / "fonts.json").write_text(json.dumps(manifest))
            self.assertEqual(check_fonts(root, ["Test"]), [])

    def test_check_rejects_tampering_missing_licenses_and_google_subsets_under_a_reserved_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fonts" / "google" / "x").mkdir(parents=True)
            (root / "fonts" / "licenses").mkdir()
            font = root / "fonts" / "google" / "x" / "a.woff2"
            font.write_bytes(b"wOF2 original")
            lic = root / "fonts" / "licenses" / "OFL-Plex-Test.txt"
            lic.write_text('Copyright 2017 IBM Corp. with Reserved Font Name "Plex"\n'
                           "This Font Software is licensed under the SIL Open Font License, Version 1.1.\n")
            manifest = {
                "families": {"Plex Test": {"license": "licenses/OFL-Plex-Test.txt", "reserved_font_names": ["Plex"],
                                           "license_sha256": hashlib.sha256(lic.read_bytes()).hexdigest()}},
                "specs": {"Plex+Test": {"faces": [{"style": "normal", "weight": "400", "range": "U+0000-00FF",
                                                   "file": "google/x/a.woff2"}]}},
                "files": {"google/x/a.woff2": {"sha256": hashlib.sha256(b"wOF2 original").hexdigest()}},
            }
            (root / "fonts" / "fonts.json").write_text(json.dumps(manifest))
            errors = check_fonts(root, ["Plex+Test"])
            self.assertTrue(any("Reserved Font Name" in e for e in errors), errors)
            font.write_bytes(b"wOF2 changed")
            (root / "fonts" / "stray.woff2").write_bytes(b"")
            lic.unlink()
            errors = check_fonts(root, ["Plex+Test", "Missing+Family"])
            for message in ["sha256 differs", "license text missing", "no faces for Missing+Family", "not listed"]:
                self.assertTrue(any(message in e for e in errors), (message, errors))

    def test_published_pages_load_nothing_from_other_hosts(self):
        pages = published(".html")
        self.assertGreaterEqual(len(pages), 5)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            parser = Resources()
            parser.feed(text)
            urls = parser.urls + [u for css in parser.styles for u in css_urls(css)]
            for url in urls:
                self.assertTrue(is_local(url), f"{page.relative_to(build.DOCS)}: {url}")
            self.assertTrue(any(u.endswith("fonts/catalog.css") or u.endswith("fonts/home.css") for u in urls), page)
            for api in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "EventSource", "import("):
                self.assertNotIn(api, text, page)
        for sheet in published(".css"):
            for url in css_urls(sheet.read_text(encoding="utf-8")):
                self.assertTrue(is_local(url), f"{sheet.relative_to(build.DOCS)}: {url}")
        for path in published(".html", ".css", ".js", ".json", ".txt"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("fonts.googleapis.com", text, path)
            self.assertNotIn("fonts.gstatic.com", text, path)


if __name__ == "__main__":
    unittest.main()

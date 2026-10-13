"""Legal notice and sister-project links on every published page. Run python3 build.py first.

The details themselves live only in legal/notice.json; these tests read them from there.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urljoin

import build
from legal import page as legal

SITE = build.SITE_URL + "/"
LEGAL_URL = {lang: SITE + path for lang, path in legal.PATH.items()}
HEADINGS = {
    "de": ["Angaben gemäß § 5 DDG", "Kontakt", "Umsatzsteuer-ID",
           "Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV"],
    "en": ["Information pursuant to Section 5 DDG (German Digital Services Act)", "Contact", "VAT ID",
           "Responsible for content pursuant to Section 18(2) MStV"],
}
PHRASES = {
    "de": ["Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:",
           "Bitte versende keine Pakete an diese Adresse.", "E-Mail:"],
    "en": ["VAT identification number pursuant to Section 27a of the German VAT Act:",
           "Please do not send parcels to this address.", "Email:"],
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.text, self.h2, self.stack, self.lang = [], [], [], [], None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "a":
            self.links.append(attrs.get("href") or "")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        while self.stack and self.stack.pop() != tag:
            pass

    def handle_data(self, data):
        if not {"script", "style"} & set(self.stack):
            self.text.append(data)
            if "h2" in self.stack:
                self.h2.append(data)


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    rel = path.relative_to(build.DOCS).as_posix()
    url = SITE + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
    page.absolute = {urljoin(url, href) for href in page.links}
    page.visible = " ".join(" ".join(page.text).replace("\u00a0", " ").split())
    return page


def pages():
    return sorted(build.DOCS.rglob("*.html"))


# The language choice page and the 404 speak both languages and link both legal pages and both sets of siblings.
BILINGUAL = {build.DOCS / "index.html", build.DOCS / "404.html"}


class LegalNotice(unittest.TestCase):
    def test_notice_data_is_complete(self):
        data = legal.load()
        self.assertRegex(data["vat_id"], r"^DE\d{9}$")
        self.assertRegex(data["email"], r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$")
        self.assertTrue(any(line.startswith("c/o ") for line in data["address"]), data["address"])
        self.assertTrue(any(re.fullmatch(r"\d{5} \S.*", line) for line in data["address"]), data["address"])
        self.assertEqual(data["responsible"], data["name"])

    def test_notice_data_is_stored_exactly_once(self):
        data = legal.load()
        # Lines that identify this notice; the country alone would match unrelated text.
        markers = [data["vat_id"], data["email"]] + [
            line for line in data["address"] if line.startswith("c/o ") or any(ch.isdigit() for ch in line)]
        skip = {"docs", "research", ".git", "__pycache__"}
        holders = set()
        for path in build.ROOT.rglob("*"):
            if path.is_file() and not skip & set(path.relative_to(build.ROOT).parts) and path.suffix in {
                    ".py", ".json", ".html", ".md", ".js", ".css", ".txt", ".cjs", ".yml"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if any(x in text for x in markers):
                    holders.add(path.relative_to(build.ROOT).as_posix())
        self.assertEqual(holders, {"legal/notice.json"})

    def test_legal_pages_show_every_detail_in_their_language(self):
        data = legal.load()
        details = [data["name"], *data["address"], data["email"], data["vat_id"], data["responsible"]]
        for lang in ("de", "en"):
            page = parse(build.DOCS / legal.PATH[lang] / "index.html")
            self.assertEqual(page.lang, lang)
            for phrase in PHRASES[lang] + details:
                self.assertIn(phrase, page.visible, (lang, phrase))
            # Provider and person responsible for content share the address.
            self.assertEqual(page.visible.count(data["address"][0]), 2, lang)
            self.assertIn(f"mailto:{data['email']}", page.links)
            self.assertEqual([" ".join(h.replace("\u00a0", " ").split()) for h in page.h2], HEADINGS[lang])
            for absent in ("Urheberrecht", "Haftung", "Streitbeilegung", "Schlichtung", "Copyright", "Liability"):
                self.assertNotIn(absent, page.visible, (lang, absent))
        de = parse(build.DOCS / legal.PATH["de"] / "index.html").visible
        self.assertNotRegex(de, r"\b(Sie|Ihnen|Ihre?)\b")
        self.assertNotIn("!", de)

    def test_every_page_links_the_legal_notice_in_its_language(self):
        self.assertGreaterEqual(len(pages()), 6)
        self.assertLessEqual(BILINGUAL, set(pages()))
        for path in pages():
            page = parse(path)
            langs = ("de", "en") if path in BILINGUAL else (page.lang,)
            for lang in langs:
                self.assertIn(LEGAL_URL[lang], page.absolute, (path, lang))

    def test_every_page_links_both_sister_projects_in_its_language(self):
        for path in pages():
            page = parse(path)
            langs = ("de", "en") if path in BILINGUAL else (page.lang,)
            for lang in langs:
                for name, url in build.SIBLINGS:
                    self.assertIn(f"{url}{lang}/", page.absolute, (path, name))
        self.assertEqual({name for name, _ in build.SIBLINGS}, {"Bildsprache", "Farbsprache"})

    def test_not_found_page_uses_absolute_paths(self):
        # GitHub Pages serves 404.html for any missing path, so relative links would resolve against that path.
        text = (build.DOCS / "404.html").read_text(encoding="utf-8")
        base = build.SITE_URL.split("github.io", 1)[1] + "/"
        urls = re.findall(r'(?:href|src)="([^"]*)"', text)
        self.assertIn(base + "fonts/home.css", urls)
        for url in urls:
            self.assertTrue(url.startswith((base, "https://", "data:")), url)

    def test_readmes_link_both_sister_projects(self):
        # READMEs are read on GitHub, so they link the sister repositories, as Bildsprache and Farbsprache do.
        for name in ("README.md", "README.de.md"):
            text = (build.ROOT / name).read_text(encoding="utf-8")
            for sibling, _ in build.SIBLINGS:
                self.assertIn(f"](https://github.com/grundhofer/{sibling.lower()})", text, name)


if __name__ == "__main__":
    unittest.main()

"""Dependency-free source checks shared by the build and regression tests."""

import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

PARAMS = {"radius", "contrast", "density", "depth", "color", "type", "motion", "texture"}
SCORES = {"longevity", "recognition", "effort", "density"}
PLATFORMS = {"web", "mobile", "desktop"}
FITS = {"dev-tool", "data", "content", "consumer", "marketing", "creative", "civic", "internal"}
TONES = {"precise", "calm", "warm", "loud", "playful", "formal", "technical", "nostalgic", "expressive", "austere"}
TEXT_FIELDS = {"name", "family", "era", "origin", "idea", "a11y", "longevity", "verdict", "tip"}
LIST_FIELDS = {"aka", "markers", "palette", "strengths", "risks", "combinesWith", "googleFonts"}


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def is_score(value):
    return type(value) is int and 1 <= value <= 5


def check_fact_sheet(data, slug, family, slugs, fonts):
    errors = []
    if not isinstance(data, dict):
        return ["fact sheet must be an object"]
    if data.get("slug") != slug or data.get("family") != family:
        errors.append("slug/family does not match the catalog order")
    for key in TEXT_FIELDS:
        if not is_text(data.get(key)):
            errors.append(f"{key}: expected nonempty text")
    for key in LIST_FIELDS:
        value = data.get(key)
        if not isinstance(value, list) or not all(is_text(v) for v in value):
            errors.append(f"{key}: expected a list of nonempty strings")
    if errors:
        return errors
    for key, keys, valid in [("params", PARAMS, is_text), ("scores", SCORES, is_score),
                             ("platforms", PLATFORMS, is_text)]:
        value = data.get(key)
        if not isinstance(value, dict) or set(value) != keys or not all(valid(v) for v in value.values()):
            errors.append(f"{key}: expected {', '.join(sorted(keys))} with valid values")
    if not 9 <= len(data["markers"]) <= 11:
        errors.append("markers: expected 9–11 entries")
    examples = data.get("examples")
    if not isinstance(examples, list) or len(examples) < 4 or not all(
        isinstance(e, dict) and is_text(e.get("name")) and is_text(e.get("what")) for e in examples
    ):
        errors.append("examples: expected at least four named examples with observations")
    if not data["palette"] or not all(re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in data["palette"]):
        errors.append("palette: expected six-digit hex colors")
    for key, allowed in [("combinesWith", set(slugs) - {slug}), ("googleFonts", fonts)]:
        if len(data[key]) != len(set(data[key])) or set(data[key]) - allowed:
            errors.append(f"{key}: duplicate or unknown reference")
    finder = data.get("finder")
    if not isinstance(finder, dict):
        return errors + ["finder: expected an object"]
    if finder.get("mode") not in {"light", "dark", "both"} or not is_score(finder.get("a11y")):
        errors.append("finder: invalid mode or accessibility score")
    platform = finder.get("platform")
    if not isinstance(platform, dict) or set(platform) != PLATFORMS or not all(is_score(v) for v in platform.values()):
        errors.append("finder.platform: expected three scores from 1–5")
    for key, allowed in [("fits", FITS), ("tone", TONES)]:
        value = finder.get(key)
        if (not isinstance(value, list) or not 2 <= len(value) <= 4
                or not all(isinstance(v, str) for v in value)
                or len(value) != len(set(value)) or set(value) - allowed):
            errors.append(f"finder.{key}: expected 2–4 distinct allowed values")
    if not is_text(finder.get("signature")) or len(finder["signature"]) > 110:
        errors.append("finder.signature: expected 1–110 characters")
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not all(
        isinstance(s, dict) and is_text(s.get("title")) and isinstance(s.get("url"), str)
        and urlsplit(s["url"]).scheme == "https" and urlsplit(s["url"]).netloc
        for s in sources
    ):
        errors.append("sources: expected titled HTTPS links")
    return errors


class DemoParser(HTMLParser):
    """Check the deliberately small, inert HTML fragment contract."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    FORBIDDEN = {"script", "link", "iframe", "object", "embed", "img", "audio", "video", "base", "meta"}

    def __init__(self):
        super().__init__()
        self.stack, self.roots, self.errors, self.text = [], [], [], []
        self.styles, self.inputs = 0, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if not self.stack:
            self.roots.append((tag, attrs))
        if tag in self.FORBIDDEN or any(k.startswith("on") for k in attrs):
            self.errors.append(f"line {self.getpos()[0]}: executable or external resource: <{tag}>")
        for key in ("src", "srcset", "href", "xlink:href", "action", "formaction"):
            if key in attrs and not (attrs[key] or "").startswith("#"):
                self.errors.append(f"line {self.getpos()[0]}: external {key} is not allowed in a demo")
        if tag == "style":
            self.styles += 1
        if tag == "input":
            self.inputs.append(attrs)
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"line {self.getpos()[0]}: unbalanced </{tag}>")
        else:
            self.stack.pop()

    def handle_data(self, value):
        if "style" not in self.stack:
            if value.strip() and not self.stack:
                self.errors.append("text outside the demo root")
            self.text.append(value)


def check_demo(raw, slug, lang):
    demo = DemoParser()
    demo.feed(raw)
    if demo.stack or demo.styles != 1 or len(demo.roots) != 2 or [r[0] for r in demo.roots] != ["style", "div"]:
        demo.errors.append("expected one <style> followed by one balanced root <div>")
    elif f"style-{slug}" not in demo.roots[1][1].get("class", "").split():
        demo.errors.append("root class must match the style slug")
    search_inputs = [i for i in demo.inputs if i.get("type", "text") in {"text", "search"}]
    if len(search_inputs) != 1 or "readonly" not in search_inputs[0]:
        demo.errors.append("expected one readonly search input")
    if any("readonly" not in i and "disabled" not in i for i in demo.inputs):
        demo.errors.append("demo inputs must be readonly or disabled")
    text = " ".join(" ".join(demo.text).split()).casefold()
    reference = ["Nexus", "Autowrite Studio", "Balance Ally", "12"]
    reference += (["Projekte", "vor 2 Std.", "gestern", "vor 4 Tagen", "Aktiv", "Pausiert", "Neues Projekt", "Importieren"]
                  if lang == "de" else ["Projects", "2 hrs ago", "yesterday", "4 days ago", "Active", "Paused", "New project", "Import"])
    for part in reference:
        if part.casefold() not in text:
            demo.errors.append(f"missing reference text: {part}")
    return demo.errors


def check_catalog(root, order_de, order_en, font_specs):
    """Validate both languages before publishing any generated files."""
    errors, records, css = [], {}, {}
    slugs = [s for _, _, group in order_de for s in group]
    if [g for _, _, g in order_de] != [g for _, _, g in order_en] or len(slugs) != len(set(slugs)):
        errors.append("catalog order: languages must contain the same unique slugs in the same families")
    expected = {f"{s}{suffix}.{ext}" for s in slugs for suffix in ("", ".en") for ext in ("html", "json")}
    actual = {p.name for p in (root / "styles").iterdir() if p.suffix in {".html", ".json"}}
    errors.extend(f"missing source: styles/{name}" for name in sorted(expected - actual))
    errors.extend(f"unlisted source: styles/{name}" for name in sorted(actual - expected))
    fonts = {s.split(":")[0].replace("+", " ") for s in font_specs}
    for lang, suffix, order in [("de", "", order_de), ("en", ".en", order_en)]:
        for family, _, group in order:
            for slug in group:
                name = f"{slug}{suffix}"
                if not {f"{name}.html", f"{name}.json"} <= actual:
                    continue
                try:
                    data = json.loads((root / "styles" / f"{name}.json").read_text(encoding="utf-8"))
                except (ValueError, OSError) as exc:
                    errors.append(f"styles/{name}.json: {exc}")
                    continue
                records[slug, lang] = data
                errors.extend(f"styles/{name}.json: {e}" for e in check_fact_sheet(data, slug, family, slugs, fonts))
                raw = (root / "styles" / f"{name}.html").read_text(encoding="utf-8")
                errors.extend(f"styles/{name}.html: {e}" for e in check_demo(raw, slug, lang))
                match = re.search(r"<style>(.*?)</style>", raw, re.S)
                if match:
                    css[slug, lang] = match[1]
    for slug in slugs:
        de, en = records.get((slug, "de")), records.get((slug, "en"))
        if isinstance(de, dict) and isinstance(en, dict):
            for key in ("slug", "palette", "scores", "googleFonts", "combinesWith"):
                if de.get(key) != en.get(key):
                    errors.append(f"{slug}: {key} differs between languages")
            if isinstance(de.get("finder"), dict) and isinstance(en.get("finder"), dict):
                if {k: v for k, v in de["finder"].items() if k != "signature"} != {k: v for k, v in en["finder"].items() if k != "signature"}:
                    errors.append(f"{slug}: finder attributes differ between languages")
            if [s.get("url") for s in de.get("sources", []) if isinstance(s, dict)] != [s.get("url") for s in en.get("sources", []) if isinstance(s, dict)]:
                errors.append(f"{slug}: source URLs differ between languages")
        if css.get((slug, "de")) != css.get((slug, "en")):
            errors.append(f"{slug}: demo CSS differs between languages")
    return errors

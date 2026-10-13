"""Impressum (de) and legal notice (en).

Die Angaben selbst (Name, Anschrift, E-Mail, Umsatzsteuer-ID) stehen nur in notice.json; hier stehen
Ueberschriften und Saetze. Einen Absatz zum Urheberrecht gibt es bewusst nicht: Er widerspraeche den
offenen Lizenzen des Projekts (LICENSE, LICENSE-CONTENT.md). Paragrafen mit geschuetztem Leerzeichen.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
FIELDS = ("name", "address", "email", "vat_id", "responsible")
ADDRESS_LANG = "de"
# Page location below docs/. build.py links it from every footer.
PATH = {"de": "de/impressum/", "en": "en/legal-notice/"}
LINK = {"de": "Impressum", "en": "Legal notice"}

COPY = {
    "de": {
        "title": "Impressum · Designsprache",
        "desc": "Angaben zum Anbieter von Designsprache nach §\u00a05 DDG und §\u00a018 Abs.\u00a02 MStV.",
        "h1": "Impressum",
        "provider": "Angaben gemäß §\u00a05 DDG",
        "parcels": "Bitte versende keine Pakete an diese Adresse.",
        "contact": "Kontakt",
        "email": "E-Mail:",
        "vat_heading": "Umsatzsteuer-ID",
        "vat": "Umsatzsteuer-Identifikationsnummer gemäß §\u00a027\u00a0a Umsatzsteuergesetz:",
        "responsible": "Verantwortlich für den Inhalt nach §\u00a018 Abs.\u00a02 MStV",
    },
    "en": {
        "title": "Legal notice · Designsprache",
        "desc": "Information about the provider of Designsprache pursuant to Section\u00a05 DDG and Section\u00a018(2) MStV.",
        "h1": "Legal notice",
        "provider": "Information pursuant to Section\u00a05 DDG (German Digital Services Act)",
        "parcels": "Please do not send parcels to this address.",
        "contact": "Contact",
        "email": "Email:",
        "vat_heading": "VAT ID",
        "vat": "VAT identification number pursuant to Section\u00a027a of the German VAT Act:",
        "responsible": "Responsible for content pursuant to Section\u00a018(2) MStV",
    },
}


def esc(value):
    return html.escape(str(value), quote=True)


def load():
    """Read notice.json; a missing or empty field fails the build instead of shipping a gap."""
    data = json.loads((ROOT / "notice.json").read_text(encoding="utf-8"))
    missing = [key for key in FIELDS if not data.get(key)]
    if missing or not isinstance(data["address"], list) or not all(
            isinstance(line, str) and line.strip() for line in data["address"]):
        raise ValueError("legal/notice.json: Angabe fehlt oder ist leer: " + ", ".join(missing or ["address"]))
    return data


def content(lang):
    """The <main> content: provider, contact, VAT ID and the person responsible for content."""
    t, d = COPY[lang], load()

    def postal(name):
        lines = "<br>".join(esc(line) for line in d["address"])
        if lang != ADDRESS_LANG:
            lines = f'<span lang="{ADDRESS_LANG}">{lines}</span>'
        return f"<p>{esc(name)}<br>{lines}</p>"

    def section(heading, body):
        return f"<section><h2>{esc(heading)}</h2>{body}</section>"

    return (f'<h1>{esc(t["h1"])}</h1>\n'
            + section(t["provider"], postal(d["name"]) + f'<p>{esc(t["parcels"])}</p>') + "\n"
            + section(t["contact"], f'<p>{esc(t["email"])} <a href="mailto:{esc(d["email"])}">{esc(d["email"])}</a></p>') + "\n"
            + section(t["vat_heading"], f'<p>{esc(t["vat"])}<br>{esc(d["vat_id"])}</p>') + "\n"
            + section(t["responsible"], postal(d["responsible"])))


def css():
    return (ROOT / "page.css").read_text(encoding="utf-8")

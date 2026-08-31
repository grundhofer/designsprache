#!/usr/bin/env python3
"""Findet Palettendubletten zwischen Katalogeintraegen.

    python3 tools/palette-check.py              # Prueflauf, Exit 1 bei Befund
    python3 tools/palette-check.py --report     # volle Rangliste, Exit immer 0
    python3 tools/palette-check.py --at HEAD~5  # ein aelterer Stand

Finds palette duplicates between catalog entries. Method and calibration below.

WAS GEPRUEFT WIRD
Zwei Eintraege duerfen nicht zwei oder mehr bunte Farben fuehren, die praktisch
dieselben sind. Gemessen wird in OKLab-Delta-E, weil sRGB-Hex-Naehe nichts ueber
wahrgenommene Naehe aussagt. Neutrale bleiben aussen vor - dass jeder helle Stil ein
gebrochenes Weiss und jeder dunkle ein Fast-Schwarz fuehrt, ist kein Fehler.

WIE DIE SCHWELLE ZUSTANDE KAM
Der Anlass war ein echter Befund: memphis und maximalism fuehrten #FF3B7F und #FF3D81
(Delta-E 0,3) sowie #2B33E0 und #2B36D6 (Delta-E 1,6). Das ist dieselbe Farbe mit
anderer letzter Hex-Stelle, und beide Eintraege lasen sich im Katalog als ein Stil.

Ein erster Entwurf dieses Skripts wollte zusaetzlich die STRUKTUR vergleichen, unter
der Annahme, dass Farbnaehe erst zusammen mit struktureller Naehe stoert. Diese Annahme
liess sich am Datenmaterial widerlegen: Gegen den Stand vor der Reparatur gelaufen hat
der Strukturfilter ausgerechnet den bekannten Defekt herausgefiltert, weil memphis und
maximalism trotz identischer Farben unterschiedliche Grundflaechen und Radien hatten.
Der Filter wurde daraufhin verworfen. Die Strukturwerte werden in --report weiterhin
ausgegeben, aber nur als Zusatzinformation fuer den Menschen, nie als Kriterium.

An early draft also compared structure, assuming color proximity only matters alongside
structural proximity. Running it against the pre-fix state falsified that: the structure
filter removed the very defect it was written to catch. It is now reported, never gated.

Kalibrierung, jederzeit nachvollziehbar:
    python3 tools/palette-check.py --at <Stand vor der Reparatur>   -> Exit 1
    python3 tools/palette-check.py                                  -> Exit 0

AUSNAHMEN
Ein Paar mit belegter gemeinsamer Abstammung gehoert nach ALLOWED. Bedingung: Die
Begruendung steht im Feld "risks" BEIDER Faktenblaetter, sodass sie im Katalog sichtbar
ist. Ohne diesen Beleg ist die Ausnahme eine Ausrede.
"""
import json
import math
import pathlib
import re
import subprocess
import sys
from itertools import combinations

ROOT = pathlib.Path(__file__).resolve().parent.parent
STYLES = ROOT / "styles"

DUPE_DE = 2.0      # darunter sind zwei Farben praktisch dieselbe
MIN_DUPE = 2       # so viele braucht ein Befund
CHROMA_MIN = 0.09  # darunter zaehlt eine Farbe als neutral
NEAR_DE = 10.0     # nur fuer --report: "auffaellig nah"

ALLOWED = {
    frozenset({"glassmorphism", "vaporwave"}):
        "Gemeinsame Neon-Abstammung der 2010er; beide fuehren dasselbe Cyan und dasselbe "
        "Bernstein. In den risks beider Faktenblaetter benannt.",
}

# Nur zur Einordnung in --report. Diese Paare liegen ueber DUPE_DE und loesen
# keinen Befund aus; die Notiz erspart die wiederholte Nachfrage.
KONTEXT = {
    frozenset({"bauhaus", "de-stijl"}): "beide fuehren dieselben Primaerfarben",
    frozenset({"data-dense", "retro-futurism"}): "CRT-Leuchtstoffe Bernstein und Gruen",
    frozenset({"data-dense", "pixel-8bit"}): "Terminal- und Konsolenpalette",
    frozenset({"pixel-8bit", "retro-futurism"}): "gemeinsames CRT-Erbe",
}


def _oklab(hx):
    hx = hx.strip().lstrip("#")
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = f(r), f(g), f(b)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def chroma(hx):
    _, a, b = _oklab(hx)
    return math.hypot(a, b)


def delta_e(a, b):
    return 100 * math.dist(_oklab(a), _oklab(b))


def ground_of(css, palette):
    """Grundflaeche: Hintergrund der Wurzelregel, sonst hellster Palettenwert."""
    root = re.search(r"\.style-[\w-]+\s*\{([^}]*)\}", css)
    if root:
        m = re.search(r"background(?:-color)?:\s*(#[0-9a-fA-F]{6})", root.group(1))
        if m:
            return m.group(1)
    return max(palette, key=lambda h: _oklab(h)[0]) if palette else None


def load(at=None):
    if at:
        names = subprocess.run(["git", "ls-tree", "--name-only", f"{at}:styles"],
                               capture_output=True, text=True, cwd=ROOT, check=True).stdout.split()
        slugs = sorted(n[:-5] for n in names if n.endswith(".json") and not n.endswith(".en.json"))
        read = lambda p: subprocess.run(["git", "show", f"{at}:styles/{p}"],
                                        capture_output=True, text=True, cwd=ROOT, check=True).stdout
    else:
        slugs = sorted(p.stem for p in STYLES.glob("*.json") if not p.stem.endswith(".en"))
        read = lambda p: (STYLES / p).read_text(encoding="utf-8")

    out = {}
    for slug in slugs:
        data = json.loads(read(f"{slug}.json"))
        css = re.search(r"<style>(.*?)</style>", read(f"{slug}.html"), re.S)
        css = css.group(1) if css else ""
        palette = [h for h in data.get("palette", [])
                   if isinstance(h, str) and h.startswith("#") and len(h) == 7]
        out[slug] = {
            "bunt": [h for h in palette if chroma(h) > CHROMA_MIN],
            "ground": ground_of(css, palette),
        }
    return out


def pairs(styles, limit):
    for a, b in combinations(sorted(styles), 2):
        near = sorted(((x, y, delta_e(x, y))
                       for x in styles[a]["bunt"] for y in styles[b]["bunt"]
                       if delta_e(x, y) < limit), key=lambda t: t[2])
        if len(near) >= MIN_DUPE:
            yield a, b, near


def main():
    argv = sys.argv[1:]
    at = argv[argv.index("--at") + 1] if "--at" in argv else None
    styles = load(at)

    print(f"{len(styles)} Stile, {len(styles) * (len(styles) - 1) // 2} Paare"
          + (f", Stand {at}" if at else ""))

    if "--report" in argv:
        print(f"\nPaare mit mindestens {MIN_DUPE} bunten Farben unter Delta-E {NEAR_DE}, "
              f"nach Naehe sortiert:\n")
        rows = sorted(pairs(styles, NEAR_DE), key=lambda r: r[2][0][2])
        for a, b, near in rows:
            key = frozenset({a, b})
            tag = ("DUBLETTE" if near[0][2] < DUPE_DE and len(
                [1 for *_, d in near if d < DUPE_DE]) >= MIN_DUPE and key not in ALLOWED
                else "erlaubt " if key in ALLOWED else "        ")
            note = ALLOWED.get(key) or KONTEXT.get(key) or ""
            gl = "  gleiche Grundflaeche" if (styles[a]["ground"] and
                                              styles[a]["ground"] == styles[b]["ground"]) else ""
            print(f"  {tag} {a:18} {b:18} "
                  + ", ".join(f"{x}/{y} dE{d:.1f}" for x, y, d in near[:3]) + gl)
            if note:
                print(f"           -> {note}")
        print(f"\n{len(rows)} Paare gelistet. Nur als DUBLETTE markierte fuehren zu Exit 1.")
        return 0

    findings = [(a, b, [t for t in near if t[2] < DUPE_DE])
                for a, b, near in pairs(styles, DUPE_DE)
                if frozenset({a, b}) not in ALLOWED]

    if not findings:
        skipped = sum(1 for a, b, _ in pairs(styles, DUPE_DE) if frozenset({a, b}) in ALLOWED)
        print(f"Keine Palettendublette."
              + (f" {skipped} Paar(e) per ALLOWED uebersprungen." if skipped else ""))
        return 0

    print(f"\n{len(findings)} Palettendublette(n):\n")
    for a, b, near in findings:
        print(f"  {a} <-> {b}")
        for x, y, d in near:
            print(f"    {x} / {y}   Delta-E {d:.1f} - "
                  + ("nicht zu unterscheiden" if d < 1 else "praktisch dieselbe Farbe"))
        if styles[a]["ground"] == styles[b]["ground"]:
            print(f"    dazu dieselbe Grundflaeche {styles[a]['ground']}")
        print()
    print("Zu tun: eine der beiden Paletten trennen - oder, wenn die Naehe eine belegte")
    print("gemeinsame Abstammung hat, das Paar in ALLOWED eintragen UND die Begruendung")
    print("in \"risks\" beider Faktenblaetter aufnehmen, damit sie im Katalog sichtbar ist.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

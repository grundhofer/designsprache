#!/usr/bin/env python3
"""Baut den Stil-Katalog aus styles/*.html und styles/*.json.

    python3 build.py            -> docs/index.html, docs/de/, docs/en/
    python3 build.py --artifact -> zusaetzlich stil-katalog.html (Fragment ohne <head>)

Quelldateien je Stil:  <slug>.html  <slug>.json  <slug>.en.html  <slug>.en.json
Die .html enthaelt genau ein <style>-Element und genau ein <div class="style-SLUG">.
Jeder CSS-Selektor darin beginnt mit .style-SLUG, damit 27 Stylesheets kollisionsfrei
auf einer Seite koexistieren. build.py prueft das und bricht sonst ab.

Build a bilingual catalog of 27 UI styles. See README.md.
"""
import json, pathlib, re, html, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "styles"
DOCS = ROOT / "docs"

SITE_URL = "https://grundhofer.github.io/designsprache"
REPO_URL = "https://github.com/grundhofer/designsprache"

# Curated order: narrative, not alphabetical.
ORDER_DE = [
    ("Modernistische Schulen",
     "Das Fundament. Hier wurde entschieden, dass ein Raster, eine Grundform und ein Abstand "
     "Bedeutung tragen können — alles Spätere ist Zustimmung oder Widerspruch dazu.",
     ["swiss", "bauhaus", "de-stijl"]),
    ("Postmoderne & Rebellion",
     "Die Gegenbewegungen. Jede bricht eine Regel der Modernisten — und braucht sie dafür "
     "als Bezugspunkt.",
     ["memphis", "swiss-punk", "web-brutalism"]),
    ("Digitale Epochen",
     "Die drei Wellen, die Bildschirmoberflächen tatsächlich durchlaufen haben. Sie erklären, "
     "warum heutige Erwartungen so aussehen, wie sie aussehen.",
     ["skeuomorph", "flat", "material-expressive"]),
    ("Weiche Materialität",
     "Drei Versuche, Tiefe zurückzuholen, ohne zum Skeuomorphismus zurückzukehren. Einer davon "
     "ist ein Lehrstück in Barrierefreiheit.",
     ["neumorphism", "glassmorphism", "claymorphism"]),
    ("Produkt-Ästhetik heute",
     "Was 2026 tatsächlich gebaut wird. Sechs Sprachen, die sich in echten Produkten bewährt "
     "haben — und die realistischsten Kandidaten für eine eigene Marke.",
     ["dev-noir", "warm-editorial", "neo-brutalism", "terminal-mono", "data-dense", "spatial-depth"]),
    ("Norm & Beschränkung",
     "Stile, deren Werte nicht der Gestalter gesetzt hat, sondern eine Prüfvorschrift, eine "
     "Darstellungsnorm oder die Physik des Displays. Hier war nichts Geschmack.",
     ["civic-service", "e-paper"]),
    ("Nostalgie & Subkultur",
     "Stile, die eine bestimmte Zeit zitieren. Sie erzeugen sofort Zugehörigkeit — und altern "
     "genau deshalb am schnellsten.",
     ["y2k-aero", "vaporwave", "retro-futurism"]),
    ("Ausdruck & Geste",
     "Von der weichen Form über die bewusste Überfüllung bis zur sichtbaren Handschrift. Was "
     "sie verbindet, ist der Widerspruch gegen die Anonymität des Rasters.",
     ["organic-blob", "maximalism", "aurora-mesh", "hand-drawn"]),
    ("Weitere Pole",
     "Vier Extreme, die als Zutat oft nützlicher sind denn als ganzer Stil.",
     ["editorial-print", "pixel-8bit", "playful-chunky", "portal-density"]),
]

# Family names must match the "family" field in the .en.json files.
ORDER_EN = [
    ("Modernist Schools",
     "The foundation. This is where it was decided that a grid, a primitive shape and a "
     "measure of space can carry meaning — everything later either agrees or argues with it.",
     ["swiss", "bauhaus", "de-stijl"]),
    ("Postmodernism & Revolt",
     "The counter-movements. Each one breaks a modernist rule — and needs that rule as its "
     "reference point.",
     ["memphis", "swiss-punk", "web-brutalism"]),
    ("Digital Eras",
     "The three waves screen interfaces actually went through. They explain why today's "
     "expectations look the way they do.",
     ["skeuomorph", "flat", "material-expressive"]),
    ("Soft Materiality",
     "Three attempts to bring depth back without returning to skeuomorphism. One of them is "
     "a case study in accessibility failure.",
     ["neumorphism", "glassmorphism", "claymorphism"]),
    ("Product Aesthetics Today",
     "What actually gets built in 2026. Six languages proven in real products — and the most "
     "realistic candidates for a brand of your own.",
     ["dev-noir", "warm-editorial", "neo-brutalism", "terminal-mono", "data-dense", "spatial-depth"]),
    ("Norm & Constraint",
     "Styles whose values were not chosen by a designer but set by a compliance standard, a "
     "display convention, or the physics of a screen. Here, nothing was taste.",
     ["civic-service", "e-paper"]),
    ("Nostalgia & Subculture",
     "Styles that quote a specific moment. They create belonging instantly — and age fastest "
     "for exactly that reason.",
     ["y2k-aero", "vaporwave", "retro-futurism"]),
    ("Expression & Gesture",
     "From the soft form through deliberate excess to a visible hand. What unites them is the "
     "argument against the anonymity of the grid.",
     ["organic-blob", "maximalism", "aurora-mesh", "hand-drawn"]),
    ("Further Poles",
     "Four extremes that are often more useful as an ingredient than as a whole style.",
     ["editorial-print", "pixel-8bit", "playful-chunky", "portal-density"]),
]

FONT_SPECS = [
    "Archivo:ital,wght@0,100..900;1,100..900",
    "Bitter:ital,wght@0,100..900;1,100..900",
    "Bricolage+Grotesque:opsz,wght@12..96,200..800",
    "Chakra+Petch:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400;1,700",
    "Fraunces:ital,opsz,wght@0,9..144,100..900;1,9..144,100..900",
    "Fredoka:wght@300..700",
    "Geist+Mono:wght@100..900",
    "IBM+Plex+Mono:ital,wght@0,100;0,400;0,500;0,600;0,700;1,400",
    "IBM+Plex+Sans+Condensed:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400",
    "Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900",
    "Istok+Web:ital,wght@0,400;0,700;1,400;1,700",
    "Jost:ital,wght@0,100..900;1,100..900",
    "Lato:ital,wght@0,300;0,400;0,700;0,900;1,400",
    "Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800",
    "Noto+Sans+JP:wght@100..900",
    "Nunito:ital,wght@0,200..1000;1,200..1000",
    "Orbitron:wght@400..900",
    "Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,700",
    "Roboto:ital,wght@0,100..900;1,100..900",
    "Roboto+Flex:opsz,wght@8..144,100..1000",
    "Silkscreen:wght@400;700",
    "Space+Grotesk:wght@300..700",
    "Space+Mono:ital,wght@0,400;0,700;1,400;1,700",
    "Work+Sans:ital,wght@0,100..900;1,100..900",
    "Anton", "Archivo+Black", "Audiowide",
    "DM+Serif+Display:ital,wght@0,400;1,400",
    "Instrument+Serif:ital,wght@0,400;1,400",
    "Michroma", "Press+Start+2P", "Share+Tech+Mono", "VT323",
    # ab Runde zwei: civic-service, e-paper, hand-drawn
    "Public+Sans:ital,wght@0,300..900;1,300..900",
    "Literata:ital,opsz,wght@0,7..72,200..900;1,7..72,200..900",
    "Cabin+Sketch:wght@400;700",
    "Neucha",
]

# Load the page's own three families first so the chrome is never left without type.
CHROME_FONTS = [
    "IBM+Plex+Sans+Condensed:ital,wght@0,400;0,500;0,600;0,700;1,400",
    "Newsreader:ital,opsz,wght@0,6..72,200..700;1,6..72,200..700",
    "IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400",
]


def font_links():
    def link(specs):
        return ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
                + "&".join("family=" + s for s in specs) + '&display=swap">')
    out = [link(CHROME_FONTS)]
    rest = [s for s in FONT_SPECS if not s.startswith(("IBM+Plex+Sans+Cond", "Newsreader", "IBM+Plex+Mono"))]
    for i in range(0, len(rest), 8):          # split into blocks: one failed request does not take the rest down
        out.append(link(rest[i:i + 8]))
    return "\n".join(out)


N_ENTRIES = sum(len(x) for _, _, x in ORDER_DE)
N_FAMILIES = len(ORDER_DE)


def load(suffix=""):
    sheets, demos, data = [], {}, {}
    for _, _, slugs in ORDER:
        for slug in slugs:
            src_html = SRC / f"{slug}{suffix}.html"
            src_json = SRC / f"{slug}{suffix}.json"
            for f in (src_html, src_json):
                if not f.exists():
                    sys.exit(f"{f.relative_to(ROOT)} fehlt. Ein Stil braucht vier Dateien: "
                             f"{slug}.html, {slug}.json, {slug}.en.html, {slug}.en.json "
                             f"(siehe CONTRIBUTING.md).")
            raw = src_html.read_text(encoding="utf-8")
            m = re.search(r"<style>(.*?)</style>", raw, re.S)
            if not m:
                sys.exit(f"kein <style> in {slug}{suffix}")
            sheets.append(m.group(1).strip())
            demos[slug] = raw[m.end():].strip()
            data[slug] = json.loads(src_json.read_text(encoding="utf-8"))
    return sheets, demos, data


def esc(s):
    return html.escape(str(s), quote=True)


METRICS_DE = {
    "longevity":   {"label": "Haltbarkeit", "short": "Haltbar", "good": "hoch",
                    "hint": "5 = altert praktisch nicht · 1 = in zwei Jahren datiert"},
    "recognition": {"label": "Wiedererkennung", "short": "Erkennbar", "good": "hoch",
                    "hint": "5 = auf 200 ms unverwechselbar · 1 = austauschbar"},
    "effort":      {"label": "Aufwand", "short": "Aufwand", "good": "niedrig",
                    "hint": "5 = sehr aufwendig sauber umzusetzen · 1 = trivial"},
    "density":     {"label": "Dichte", "short": "Dichte", "good": None,
                    "hint": "5 = sehr informationsdicht · 1 = sehr luftig"},
}

METRICS_EN = {
    "longevity":   {"label": "Longevity", "short": "Lasting", "good": "hoch",
                    "hint": "5 = barely ages · 1 = dated within two years"},
    "recognition": {"label": "Recognisability", "short": "Distinct", "good": "hoch",
                    "hint": "5 = unmistakable in 200 ms · 1 = interchangeable"},
    "effort":      {"label": "Effort", "short": "Effort", "good": "niedrig",
                    "hint": "5 = very demanding to execute well · 1 = trivial"},
    "density":     {"label": "Density", "short": "Density", "good": None,
                    "hint": "5 = highly information-dense · 1 = very airy"},
}

METRICS = METRICS_DE          # swapped per language inside build()



# ---------------------------------------------------------------------------
# Translation of the page chrome. The 27 fact sheets and demos live in their own
# .en files; only the page's own prose is listed here.
# Each pair is replaced verbatim in the template; page_en() asserts that no pair
# misses, so editing the German copy without updating the English one fails the
# build instead of silently shipping a half-German English page.
# ---------------------------------------------------------------------------
L10N = [
 ("Referenzkatalog · Designsprache", "Reference catalog · Designsprache"),
 ("Stil&#8209;Katalog<br><em>{n} Wege, dieselbe Oberfläche zu bauen</em>",
  "Style&#8209;Catalog<br><em>{n} ways to build the same interface</em>"),
 ("""Jeder Eintrag zeigt <strong>exakt dieselbe Oberfläche</strong> — eine
        Projektliste mit Kopfzeile, drei Einträgen, Suchfeld und zwei Schaltflächen. Was sich
        ändert, ist ausschließlich die Gestaltung. Dadurch wird sichtbar, was ein Stil
        tatsächlich entscheidet — und was nur Geschmack ist.""",
  """Every entry shows <strong>exactly the same interface</strong> — a project list with a
        header, three rows, a search field and two buttons. The only thing that changes is the
        design. That makes visible what a style actually decides — and what is merely
        taste."""),
 ("<b>{n}</b><span>Einträge</span>", "<b>{n}</b><span>Entries</span>"),
 ("<b>{nfam}</b><span>Familien</span>", "<b>{nfam}</b><span>Families</span>"),
 ("<b>1</b><span>Referenz&#8209;UI</span>", "<b>1</b><span>Reference&nbsp;UI</span>"),
 ("<b>7</b><span>Parameter</span>", "<b>7</b><span>Parameters</span>"),

 ("<h2>Die sieben Parameter</h2>", "<h2>The seven parameters</h2>"),
 ("""Stilnamen sind austauschbar. Was einen Stil ausmacht, sind sieben Größen — und
        jede davon ist eine Entscheidung, die man in Tokens schreiben kann. Wer sie kennt, kann
        Stile mischen statt kopieren.""",
  """Style names are interchangeable. What actually constitutes a style are seven
        quantities — and every one of them is a decision you can write down as a token. Know
        them, and you can mix styles instead of copying them."""),

 ("""<dt>Radius<i>01</i></dt><dd>Von 0&#8239;px bis vollrund. Der am stärksten
        unterschätzte Marken­träger.<em>0 kompromisslos · 6 werkzeughaft · 16+ freundlich</em>""",
  """<dt>Radius<i>01</i></dt><dd>From 0&#8239;px to fully round. The most underrated carrier
        of brand identity.<em>0 uncompromising · 6 tool-like · 16+ friendly</em>"""),
 ("""<dt>Kontrast<i>02</i></dt><dd>Der Abstand zwischen Grund und Schrift. Entscheidet, ob
        eine Oberfläche ruhig oder laut wirkt.<em>1,5:1 Neumorphismus → 18:1 Swiss</em>""",
  """<dt>Contrast<i>02</i></dt><dd>The distance between ground and type. Decides whether an
        interface reads as calm or loud.<em>1.5:1 neumorphism → 18:1 Swiss</em>"""),
 ("""<dt>Tiefe<i>03</i></dt><dd>Wie Hierarchie entsteht: gar nicht, über Linien, über
        Schatten, über Unschärfe oder über echte z&#8209;Achse.<em>Der teuerste Parameter im
        Cross&#8209;Platform&#8209;Betrieb</em>""",
  """<dt>Depth<i>03</i></dt><dd>How hierarchy is produced: not at all, through rules, through
        shadows, through blur, or on a real z&#8209;axis.<em>The most expensive parameter to run
        cross&#8209;platform</em>"""),
 ("""<dt>Dichte<i>04</i></dt><dd>Information pro Bildschirm. Zwischen den Extremen liegt
        Faktor fünf.<em>Bloomberg → Apple&#8209;Marketing</em>""",
  """<dt>Density<i>04</i></dt><dd>Information per screen. The extremes are a factor of five
        apart.<em>Bloomberg → Apple marketing</em>"""),
 ("""<dt>Farbe<i>05</i></dt><dd>Wie viel Bedeutung Farbe trägt: monochrom plus Akzent,
        Flächenfarbe oder Verlauf.<em>Der stärkste Wiedererkennungsträger</em>""",
  """<dt>Color<i>05</i></dt><dd>How much meaning color carries: monochrome plus an accent,
        flat fills, or gradients.<em>The strongest driver of recognition</em>"""),
 ("""<dt>Typografie<i>06</i></dt><dd>Grotesk, Serif, Monospace oder Display — und in
        welchem Gewichtsband.<em>Der zweitstärkste, meist zu vorsichtig gewählt</em>""",
  """<dt>Typography<i>06</i></dt><dd>Grotesque, serif, monospace or display — and in which
        weight range.<em>The second strongest, usually chosen too timidly</em>"""),
 ("""<dt>Motion<i>07</i></dt><dd>Dauer und Kurve. Die Persönlichkeit einer Oberfläche —
        und der Parameter, der am häufigsten vergessen wird.<em>0&#8239;ms · 120&#8239;ms linear ·
        400&#8239;ms Spring mit Überschwingen</em>""",
  """<dt>Motion<i>07</i></dt><dd>Duration and curve. The personality of an interface — and the
        parameter most often forgotten.<em>0&#8239;ms · 120&#8239;ms linear · 400&#8239;ms spring
        with overshoot</em>"""),

 ('aria-label="Katalog filtern und sortieren"', 'aria-label="Filter and sort the catalog"'),
 ('aria-label="Nach Familie filtern"', 'aria-label="Filter by family"'),
 ('data-fam="*" aria-pressed="true">Alle<', 'data-fam="*" aria-pressed="true">All<'),
 ('<label for="q">Suche</label>', '<label for="q">Search</label>'),
 ('placeholder="Stil, Merkmal …"', 'placeholder="Style, marker …"'),
 ('<label for="sort">Sortierung</label>', '<label for="sort">Sort by</label>'),
 ('<option value="cat">Katalog</option>', '<option value="cat">Catalog</option>'),
 ('<option value="longevity">Haltbarkeit</option>', '<option value="longevity">Longevity</option>'),
 ('<option value="recognition">Wiedererkennung</option>', '<option value="recognition">Recognisability</option>'),
 ('<option value="effort">Aufwand (wenig zuerst)</option>', '<option value="effort">Effort (least first)</option>'),
 ('<option value="density">Dichte</option>', '<option value="density">Density</option>'),
 ('<option value="name">Name</option>', '<option value="name">Name</option>'),
 ('aria-live="polite">{n} von {n}<', 'aria-live="polite">{n} of {n}<'),
 ('hidden>Kein Eintrag passt zu dieser Auswahl.<', 'hidden>No entry matches this selection.<'),

 ('<span class="eyebrow">Entscheidungsraster</span>', '<span class="eyebrow">Decision grid</span>'),
 ('<h2>Haltbarkeit gegen Wiedererkennung</h2>', '<h2>Longevity versus recognisability</h2>'),
 ("""Die beiden Größen stehen in Spannung: Was sofort erkennbar ist, altert meist
        schneller. Alle Werte sind ganzzahlig von 1 bis 5, deshalb ein Raster statt eines
        Streudiagramms — Einträge auf derselben Position verdecken sich hier nicht.""",
  """The two pull against each other: what is instantly recognisable usually ages faster.
        All values are integers from 1 to 5, so this is a grid rather than a scatter plot —
        entries sharing a position do not hide each other here."""),
 ('<label for="mx">Waagerecht</label>', '<label for="mx">Horizontal</label>'),
 ('<label for="my">Senkrecht</label>', '<label for="my">Vertical</label>'),

 ('<h2>Alle {n} im Vergleich</h2>', '<h2>All {n} compared</h2>'),
 ("""Die harten Parameter nebeneinander. Spalten mit Zahlen sind sortierbar — Kopfzeile
    anklicken. Ein Klick auf den Namen öffnet den vollständigen Eintrag.""",
  """The hard parameters side by side. Numeric columns are sortable — click the header.
    Clicking a name opens the full entry."""),
 ('<th>Nr.</th><th>Stil</th><th>Radius</th><th>Kontrast</th><th>Dichte</th><th>Tiefe</th>',
  '<th>No.</th><th>Style</th><th>Radius</th><th>Contrast</th><th>Density</th><th>Depth</th>'),
 ('aria-sort="none">Haltb.</th>', 'aria-sort="none">Lasting</th>'),
 ('aria-sort="none">Wiedererk.</th>', 'aria-sort="none">Distinct</th>'),
 ('aria-sort="none">Aufwand</th>', 'aria-sort="none">Effort</th>'),

 ('<span class="eyebrow">Wie es weitergeht</span>', '<span class="eyebrow">Where to go from here</span>'),
 ('<h2>Vom Katalog zur eigenen Sprache</h2>', '<h2>From catalog to a language of your own</h2>'),
 ("""Ein Katalog ist keine Entscheidung. Drei Dinge sind beim Durchsehen nützlicher als die
    Frage „welcher gefällt mir“ — denn die beantwortet man in fünf Jahren anders.""",
  """A catalog is not a decision. Three things are more useful while browsing than the
    question &ldquo;which one do I like&rdquo; — because you will answer that differently in
    five years."""),
 ('<h3>Marken sind Hybride</h3>', '<h3>Brands are hybrids</h3>'),
 ("""Kein starkes Produkt trägt einen Reinstil. Linear ist Swiss&#8209;Raster plus
        Dark&#8209;Mode plus Terminal&#8209;Dichte. Notion ist Warm Editorial plus Flat. Stripe ist
        Swiss plus Aurora. Ein Reinstil wirkt wie ein Kostüm; eine Mischung aus zwei Familien
        mit einer klaren Hauptstimme wirkt wie eine Haltung. Jeder Eintrag nennt unter
        „Kombiniert sich mit“ die tragfähigen Paarungen.""",
  """No strong product wears a pure style. Linear is a Swiss grid plus dark mode plus terminal
        density. Notion is warm editorial plus flat. Stripe is Swiss plus aurora. A pure style
        reads as a costume; a blend of two families with one clear dominant voice reads as a
        position. Every entry lists the workable pairings under
        &ldquo;Combines with&rdquo;."""),
 ('<h3>Haltbarkeit schlägt Wirkung</h3>', '<h3>Longevity beats impact</h3>'),
 ("""Für einen Fundus, der viele Apps über Jahre tragen soll, ist Haltbarkeit
        wertvoller als Schockwirkung. Ein Stil mit Wiedererkennung 5 und Haltbarkeit 1 kostet
        dich in drei Jahren einen vollständigen Neuentwurf — über alle Projekte gleichzeitig.
        Das Raster oben macht diesen Handel sichtbar.""",
  """For a kit meant to carry many apps over years, longevity is worth more than shock value.
        A style scoring 5 on recognisability and 1 on longevity costs you a complete redesign in
        three years — across every project at once. The grid above makes that trade
        visible."""),
 ('<h3>Der Stil bestimmt die Kosten</h3>', '<h3>The style sets your costs</h3>'),
 ("""Flächenfarbe, Radius und Typografie lassen sich aus Tokens sauber nach CSS,
        Compose und SwiftUI generieren. Unschärfe, mehrschichtige Verläufe und Materialien
        nicht — die musst du auf jeder Plattform von Hand nachbauen. Glassmorphism und
        Skeuomorphismus kosten über Web, Tauri und Android ein Vielfaches von Swiss oder
        Dev&#8209;Noir. Das ist keine Geschmacksfrage, sondern eine Aufwandsschätzung.""",
  """Flat fills, radius and typography generate cleanly from tokens into CSS, Compose and
        SwiftUI. Blur, layered gradients and materials do not — those you rebuild by hand on
        every platform. Across web, Tauri and Android, glassmorphism and skeuomorphism cost a
        multiple of Swiss or dev&#8209;noir. That is not a matter of taste but an
        estimate."""),
 ("""Alle {n} Demos sind handgebautes HTML und CSS — keine Bilder, keine
    Skripte, keine Bibliotheken. Jede zeigt dieselben dreizehn Textbausteine. Die Schriften
    stammen von Google Fonts, alle Farbwerte, Radien und Zeitangaben in den Faktenblättern
    sind aus den jeweiligen Vorbildern belegt. Die vier Kennzahlen sind fachliche
    Einschätzungen, keine Messwerte.""",
  """All {n} demos are hand-built HTML and CSS — no images, no scripts, no libraries. Each shows
    the same thirteen pieces of text. Type comes from Google Fonts; the color values, radii and
    timings quoted in the fact sheets are sourced from the products they describe. The four
    scores are professional judgements, not measurements."""),

 ('aria-label="Voriger Eintrag"', 'aria-label="Previous entry"'),
 ('aria-label="Nächster Eintrag"', 'aria-label="Next entry"'),
 ('id="s-close">Schließen · Esc<', 'id="s-close">Close · Esc<'),

 # --- Zeichenketten im Skript ---
 ('blk("Kernidee"', 'blk("Core idea"'),
 ('blk("Herkunft"', 'blk("Origin"'),
 ('blk("Woran man ihn erkennt"', 'blk("How to spot it"'),
 ('blk("Parameter"', 'blk("Parameters"'),
 ('blk("Kennzahlen"', 'blk("Scores"'),
 ('blk("Echte Vertreter"', 'blk("Real examples"'),
 ('blk("Stärken"', 'blk("Strengths"'),
 ('blk("Risiken"', 'blk("Risks"'),
 ('blk("Barrierefreiheit"', 'blk("Accessibility"'),
 ('blk("Alterungsverhalten"', 'blk("How it ages"'),
 ('blk("Plattformen"', 'blk("Platforms"'),
 ('blk("Praxistipp"', 'blk("Practical tip"'),
 ('blk("Als Basis für eine Eigenmarke"', 'blk("As a basis for your own brand"'),
 ('blk("Kombiniert sich mit"', 'blk("Combines with"'),
 ('blk("Auch bekannt als"', 'blk("Also known as"'),
 ('[["Radius", p.radius], ["Kontrast", p.contrast], ["Dichte", p.density],\n       ["Tiefe", p.depth], ["Farbe", p.color], ["Typografie", p.type],\n       ["Motion", p.motion], ["Textur", p.texture]]',
  '[["Radius", p.radius], ["Contrast", p.contrast], ["Density", p.density],\n       ["Depth", p.depth], ["Color", p.color], ["Typography", p.type],\n       ["Motion", p.motion], ["Texture", p.texture]]'),
 ('" von 5</dd></div>"', '" of 5</dd></div>"'),
 ('sCap.textContent = "Dieselbe Referenz-UI wie in allen {n} Einträgen, hier in voller Größe.";',
  'sCap.textContent = "The same reference UI as in all {n} entries, here at full size.";'),
 ('shown + " von {n}"', 'shown + " of {n}"'),
 ('"Getönt: der günstige Bereich — "', '"Tinted: the favourable region — "'),
 ('(xGood === "hoch" ? "hoch" : "niedrig") + " und "', '(xGood === "hoch" ? "high" : "low") + " and "'),
 ('" " + (yGood === "hoch" ? "hoch" : "niedrig") + "."', '" " + (yGood === "hoch" ? "high" : "low") + "."'),
 ('"Für diese Kombination gibt es keine objektiv bessere Ecke — Dichte ist eine "\n        + "Eigenschaft, kein Gütekriterium. Deshalb ohne Tönung."',
  '"There is no objectively better corner for this combination — density is a property, "\n        + "not a mark of quality. Hence no tint."'),
 ('.localeCompare(DATA[b.dataset.slug].name, "de")', '.localeCompare(DATA[b.dataset.slug].name, "en")'),
 # Der gesamte Textblock des Stil-Finders als EIN Paar - dreissig Einzelpaare waeren
 # weder zu pflegen noch zu pruefen.
 ('  var FT = {{\n    lede: "Neun Fragen. Die Empfehlung entsteht aus den Merkmalen der Faktenblätter, nicht aus Geschmack — jeder Treffer wird begründet. Du kannst die Eigenschaften des empfohlenen Stils anschließend als Anweisung für einen KI-Agenten kopieren.",\n    go: "Empfehlung zeigen", answered: "% von 9 beantwortet", need: "Beantworte mindestens die erste Frage.",\n    resTitle: "Deine Empfehlung", resLede: "Die % am besten passenden Einträge von %. Die Prozentzahl ist der Anteil der erreichten Punkte, keine Note.",\n    open: "Eintrag öffnen", copy: "Als Prompt kopieren", copied: "Kopiert", show: "Text anzeigen",\n    manual: "Automatisches Kopieren ist hier gesperrt. Der Text ist markiert — mit Strg+C bzw. Cmd+C kopieren.",\n    caption: "Dieselbe Referenz-UI wie in allen % Einträgen.",\n    note: "Die Empfehlung gewichtet neun Merkmale. Sie ersetzt kein eigenes Urteil — sieh dir die Demos an und lies das Faktenblatt. Ein Stil, der auf Platz vier steht, kann für dein Projekt der richtige sein.",\n    pIntro: "Verwende die folgende Designsprache als visuelle Grundlage für dieses Projekt. Weiche nicht davon ab, ohne es zu begründen.",\n    pIdea: "Kernidee", pParams: "Harte Parameter", pPalette: "Palette", pFonts: "Schriften",\n    pRules: "Regeln, die einzuhalten sind", pAvoid: "Bekannte Fehlerquellen dieses Stils — vermeide sie",\n    pA11y: "Barrierefreiheit", pTip: "Praxistipp", pSource: "Quelle",\n    pRadius: "Radius", pContrast: "Kontrast", pDensity: "Dichte", pDepth: "Tiefe",\n    pColor: "Farbe", pType: "Typografie", pMotion: "Motion", pTexture: "Textur",\n    pFontNote: "über Google Fonts, jeweils mit generischem Fallback",\n    why: {{\n      useYes: "Ausdrücklich für % geeignet", useNo: "Nicht auf % ausgelegt",\n      tone: "Trifft % der gewünschten Wirkung: %", toneNo: "Trifft keine der gewünschten Wirkungen",\n      modeYes: "Modus passt: %", modeNo: "Ist %, du wolltest %",\n      density: "Dichte % von 5", longevity: "Haltbarkeit % von 5",\n      recognition: "Wiedererkennung % von 5", effort: "Aufwand % von 5",\n      a11y: "Barrierefreiheit % von 5", platform: "Plattform-Eignung: %"\n    }},\n    modeName: {{ light: "hell", dark: "dunkel", both: "hell und dunkel", any: "egal" }},\n    platName: {{ web: "Web", mobile: "Mobile", desktop: "Desktop" }},\n    q: [\n      {{ id: "use", h: "Was baust du?", s: "bestimmt die Grundeignung", o: [\n        ["dev-tool","Entwicklerwerkzeug"],["data","Datenwerkzeug, Dashboard"],\n        ["content","Text, Doku, Redaktion"],["consumer","App für Endkunden"],\n        ["marketing","Landingpage, Portfolio"],["creative","Werkzeug zum Gestalten"],\n        ["civic","Behörde, Bildung, Gesundheit"],["internal","internes Werkzeug"]] }},\n      {{ id: "tone", multi: true, max: 3, h: "Wie soll es wirken?", s: "zwei bis drei auswählen", o: [\n        ["precise","präzise"],["calm","ruhig"],["warm","warm"],["loud","laut"],\n        ["playful","verspielt"],["formal","seriös"],["technical","technisch"],\n        ["nostalgic","nostalgisch"],["expressive","eigenwillig"],["austere","streng"]] }},\n      {{ id: "mode", h: "Hell oder dunkel?", s: "der Modus, in dem es hauptsächlich läuft", o: [\n        ["light","hell"],["dark","dunkel"],["any","egal"]] }},\n      {{ id: "density", h: "Wie viel Information pro Bildschirm?", s: "", o: [\n        ["1","sehr luftig"],["3","mittel"],["5","sehr dicht"],["any","egal"]] }},\n      {{ id: "longevity", h: "Wie lange soll es tragen?", s: "kurzlebige Stile kosten später einen Neuentwurf", o: [\n        ["5","ein Jahrzehnt"],["3","einige Jahre"],["1","kurzlebig, Hauptsache jetzt"],["any","egal"]] }},\n      {{ id: "recognition", h: "Auffallen oder vertraut wirken?", s: "", o: [\n        ["5","unverwechselbar"],["3","eigen, aber ruhig"],["1","bewusst vertraut"],["any","egal"]] }},\n      {{ id: "effort", h: "Wie viel Aufwand kannst du investieren?", s: "aufwendige Stile brauchen mehr Handarbeit je Plattform", o: [\n        ["1","wenig"],["3","mittel"],["5","viel"]] }},\n      {{ id: "a11y", h: "Wie wichtig ist Barrierefreiheit?", s: "", o: [\n        ["5","kritisch"],["3","wichtig"],["1","nachrangig"]] }},\n      {{ id: "platform", multi: true, h: "Für welche Plattformen?", s: "mehrere möglich", o: [\n        ["web","Web"],["mobile","Mobile"],["desktop","Desktop"]] }}\n    ]\n  }};\n',
  '  var FT = {{\n    lede: "Nine questions. The recommendation comes from the fact sheets\' own attributes, not from taste — every match is justified. You can then copy the recommended style\'s properties as an instruction for an AI agent.",\n    go: "Show recommendation", answered: "% of 9 answered", need: "Answer at least the first question.",\n    resTitle: "Your recommendation", resLede: "The % closest matches out of %. The percentage is the share of points reached, not a grade.",\n    open: "Open entry", copy: "Copy as prompt", copied: "Copied", show: "Show text",\n    manual: "Automatic copying is blocked here. The text is selected \u2014 press Ctrl+C or Cmd+C.",\n    caption: "The same reference UI as in all % entries.",\n    note: "The recommendation weighs nine attributes. It does not replace your own judgement — look at the demos and read the fact sheet. A style ranked fourth may still be the right one for your project.",\n    pIntro: "Use the following design language as the visual foundation for this project. Do not deviate from it without stating why.",\n    pIdea: "Core idea", pParams: "Hard parameters", pPalette: "Palette", pFonts: "Type",\n    pRules: "Rules to follow", pAvoid: "Known failure modes of this style — avoid them",\n    pA11y: "Accessibility", pTip: "Practical tip", pSource: "Source",\n    pRadius: "Radius", pContrast: "Contrast", pDensity: "Density", pDepth: "Depth",\n    pColor: "Color", pType: "Typography", pMotion: "Motion", pTexture: "Texture",\n    pFontNote: "via Google Fonts, each with a generic fallback",\n    why: {{\n      useYes: "Explicitly suited to %", useNo: "Not built for %",\n      tone: "Matches % of the intended feel: %", toneNo: "Matches none of the intended feel",\n      modeYes: "Mode fits: %", modeNo: "Is %, you wanted %",\n      density: "Density % of 5", longevity: "Longevity % of 5",\n      recognition: "Recognisability % of 5", effort: "Effort % of 5",\n      a11y: "Accessibility % of 5", platform: "Platform fit: %"\n    }},\n    modeName: {{ light: "light", dark: "dark", both: "light and dark", any: "either" }},\n    platName: {{ web: "Web", mobile: "Mobile", desktop: "Desktop" }},\n    q: [\n      {{ id: "use", h: "What are you building?", s: "sets the baseline fit", o: [\n        ["dev-tool","Developer tool"],["data","Data tool, dashboard"],\n        ["content","Text, docs, editorial"],["consumer","Consumer app"],\n        ["marketing","Landing page, portfolio"],["creative","Tool for making things"],\n        ["civic","Government, education, health"],["internal","Internal tool"]] }},\n      {{ id: "tone", multi: true, max: 3, h: "How should it feel?", s: "pick two or three", o: [\n        ["precise","precise"],["calm","calm"],["warm","warm"],["loud","loud"],\n        ["playful","playful"],["formal","formal"],["technical","technical"],\n        ["nostalgic","nostalgic"],["expressive","expressive"],["austere","austere"]] }},\n      {{ id: "mode", h: "Light or dark?", s: "the mode it mainly runs in", o: [\n        ["light","light"],["dark","dark"],["any","either"]] }},\n      {{ id: "density", h: "How much information per screen?", s: "", o: [\n        ["1","very airy"],["3","medium"],["5","very dense"],["any","either"]] }},\n      {{ id: "longevity", h: "How long should it last?", s: "short-lived styles cost a redesign later", o: [\n        ["5","a decade"],["3","a few years"],["1","short-lived, it just has to land now"],["any","either"]] }},\n      {{ id: "recognition", h: "Stand out or feel familiar?", s: "", o: [\n        ["5","unmistakable"],["3","distinct but quiet"],["1","deliberately familiar"],["any","either"]] }},\n      {{ id: "effort", h: "How much effort can you invest?", s: "demanding styles need more hand work per platform", o: [\n        ["1","little"],["3","moderate"],["5","a lot"]] }},\n      {{ id: "a11y", h: "How important is accessibility?", s: "", o: [\n        ["5","critical"],["3","important"],["1","secondary"]] }},\n      {{ id: "platform", multi: true, h: "Which platforms?", s: "several possible", o: [\n        ["web","Web"],["mobile","Mobile"],["desktop","Desktop"]] }}\n    ]\n  }};\n'),
 ('<button class="fi-open" type="button" id="fi-open">Stil finden</button>',
  '<button class="fi-open" type="button" id="fi-open">Find a style</button>'),
 ('<h2 id="fi-title">Welcher Stil passt zu deinem Projekt?</h2>',
  '<h2 id="fi-title">Which style fits your project?</h2>'),
 ('id="fi-again" hidden>Antworten ändern<', 'id="fi-again" hidden>Change answers<'),
 ('id="fi-close">Schließen · Esc<', 'id="fi-close">Close · Esc<'),
]

UI = {
    "de": {"entries": "Einträge", "ofFive": "von 5",
           "openAria": "Eintrag {i}: {name} — vollständiges Faktenblatt öffnen"},
    "en": {"entries": "entries", "ofFive": "of 5",
           "openAria": "Entry {i}: {name} — open the full fact sheet"},
}


def build(lang="de", mode="site"):
    global ORDER, METRICS
    ORDER = ORDER_DE if lang == "de" else ORDER_EN
    METRICS = METRICS_DE if lang == "de" else METRICS_EN
    U = UI[lang]
    suffix = "" if lang == "de" else ".en"

    sheets, demos, data = load(suffix)
    n = sum(len(s) for _, _, s in ORDER)
    assert n == N_ENTRIES, n
    check_scoping(sheets, [x for _, _, ss in ORDER for x in ss], suffix)

    # ---------- Plates ----------
    idx, sections = 0, []
    for fam, intro, slugs in ORDER:
        plates = []
        for slug in slugs:
            idx += 1
            d = data[slug]
            sc = d["scores"]
            bars = "".join(
                f'<div class="sc" title="{esc(METRICS[k]["label"])}: {sc.get(k,0)} {U["ofFive"]} — {esc(METRICS[k]["hint"])}">'
                f'<span class="sc-k">{esc(METRICS[k]["short"])}</span>'
                f'<span class="sc-bar" aria-hidden="true">'
                + "".join(f'<i class="{"on" if j <= sc.get(k, 0) else ""}"></i>' for j in range(1, 6))
                + f'</span><span class="sc-v">{sc.get(k, 0)}</span></div>'
                for k in METRICS)
            plates.append(f'''
<article class="k-plate" data-slug="{esc(slug)}" data-family="{esc(fam)}"
  data-longevity="{sc.get('longevity',0)}" data-recognition="{sc.get('recognition',0)}"
  data-effort="{sc.get('effort',0)}" data-density="{sc.get('density',0)}" data-idx="{idx}"
  data-search="{esc((d['name'] + ' ' + ' '.join(d.get('aka') or []) + ' ' + fam + ' ' + d.get('idea','')).lower())}">
  <div class="plate-frame" data-open><div class="demo-host" inert>{demos[slug]}</div></div>
  <div class="plate-meta">
    <div class="plate-line">
      <span class="ent">{idx:02d}</span>
      <h3><button class="plate-open" type="button"
        aria-label="{esc(U['openAria'].format(i=idx, name=d['name']))}"
        >{esc(d['name'])}</button></h3>
      <span class="era">{esc(d.get('era',''))}</span>
    </div>
    <p class="idea">{esc(d.get('idea',''))}</p>
    <div class="scores">{bars}</div>
  </div>
</article>''')
        sections.append(f'''
<section class="fam" data-family="{esc(fam)}">
  <header class="fam-head">
    <h2>{esc(fam)}</h2>
    <p>{esc(intro)}</p>
    <span class="fam-count">{len(slugs)} {U['entries']}</span>
  </header>
  <div class="grid">{''.join(plates)}</div>
</section>''')

    # ---------- Vergleichstabelle ----------
    rows = []
    i = 0
    for fam, _, slugs in ORDER:
        for slug in slugs:
            i += 1
            d, p, sc = data[slug], data[slug]["params"], data[slug]["scores"]
            rows.append(f'''<tr data-slug="{esc(slug)}">
<td class="k-num">{i:02d}</td>
<td class="nm"><button type="button" class="row-open">{esc(d['name'])}</button><span class="row-fam">{esc(fam)}</span></td>
<td>{esc(p.get('radius',''))}</td>
<td>{esc(p.get('contrast',''))}</td>
<td>{esc(p.get('density',''))}</td>
<td class="wide">{esc(p.get('depth',''))}</td>
<td class="k-num" data-v="{sc.get('longevity',0)}">{sc.get('longevity',0)}</td>
<td class="k-num" data-v="{sc.get('recognition',0)}">{sc.get('recognition',0)}</td>
<td class="k-num" data-v="{sc.get('effort',0)}">{sc.get('effort',0)}</td>
</tr>''')

    payload = json.dumps(
        {s: {k: v for k, v in d.items()} for s, d in data.items()},
        ensure_ascii=False, separators=(",", ":")
    ).replace("</", "<\\/")

    fam_chips = "".join(
        f'<button class="k-chip" type="button" data-fam="{esc(f)}">{esc(f)}</button>'
        for f, _, _ in ORDER)

    metric_opts = "".join(f'<option value="{k}">{esc(v["label"])}</option>' for k, v in METRICS.items())

    tpl = PAGE if lang == "de" else page_en()
    body = tpl.format(
        n=N_ENTRIES, nfam=N_FAMILIES, site=SITE_URL, lang=lang,
        topbar="" if mode == "artifact" else TOPBAR[lang].format(repo=REPO_URL),
        fonts=font_links(),
        sheets="\n".join(f"<style>\n{s}\n</style>" for s in sheets),
        sections="".join(sections),
        rows="".join(rows),
        chips=fam_chips,
        payload=payload,
        mx=metric_opts.replace('value="longevity"', 'value="longevity" selected'),
        my=metric_opts.replace('value="recognition"', 'value="recognition" selected'),
    )

    if mode == "artifact":
        out = ROOT / "stil-katalog.html"
        out.write_text(body, encoding="utf-8")
    else:
        body = re.sub(r"^<title>.*?</title>\n", "", body, count=1, flags=re.S)
        out = DOCS / lang / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(HEAD[lang] + body + "\n</body>\n</html>\n", encoding="utf-8")
    print(f"  {out.relative_to(ROOT)}  ({out.stat().st_size/1024:.0f} KB, {n} Eintraege)")


PAGE = r'''<title>Stil-Katalog</title>
{fonts}
<style>
/* ============ Tokens ============ */
:root {{
  --ground:#E9EBE6; --surface:#F5F7F2; --surface-2:#FCFDFA;
  --ink:#171A17; --ink-2:#565D58; --ink-3:#838A84;
  --rule:#C6CBC2; --rule-soft:#DCE0D8;
  --accent:#1E4A45; --accent-ink:#FCFDFA; --accent-soft:#D9E5E1;
  --brass:#8A6A2F;
  --shadow:0 1px 2px rgba(23,26,23,.05), 0 8px 24px -12px rgba(23,26,23,.18);
  --maxw:1460px;
  --f-disp:"IBM Plex Sans Condensed", "Helvetica Neue", Arial, sans-serif;
  --f-body:"Newsreader", Georgia, "Times New Roman", serif;
  --f-mono:"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#141614; --surface:#1B1E1B; --surface-2:#232722;
    --ink:#E7EAE4; --ink-2:#99A099; --ink-3:#6F766F;
    --rule:#333833; --rule-soft:#252A25;
    --accent:#77BFB1; --accent-ink:#101413; --accent-soft:#20342F;
    --brass:#C7A55F;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -14px rgba(0,0,0,.7);
  }}
}}
:root[data-theme="dark"] {{
  --ground:#141614; --surface:#1B1E1B; --surface-2:#232722;
  --ink:#E7EAE4; --ink-2:#99A099; --ink-3:#6F766F;
  --rule:#333833; --rule-soft:#252A25;
  --accent:#77BFB1; --accent-ink:#101413; --accent-soft:#20342F;
  --brass:#C7A55F;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -14px rgba(0,0,0,.7);
}}

/* ============ Grundlagen ============ */
body {{ background:var(--ground); color:var(--ink); font-family:var(--f-body);
  font-size:16px; line-height:1.6; -webkit-font-smoothing:antialiased; }}
.wrap {{ box-sizing:border-box; max-width:var(--maxw); margin:0 auto;
  padding:0 clamp(16px,3vw,40px); }}
h1,h2,h3,h4 {{ font-family:var(--f-disp); font-weight:600; letter-spacing:-.01em;
  text-wrap:balance; margin:0; }}
p {{ margin:0; }}
a {{ color:var(--accent); text-underline-offset:3px; }}
:where(button,select,input,a):focus-visible {{ outline:2px solid var(--accent);
  outline-offset:3px; border-radius:2px; }}
.eyebrow {{ font-family:var(--f-mono); font-size:11px; font-weight:500;
  letter-spacing:.14em; text-transform:uppercase; color:var(--brass); }}
.mono {{ font-family:var(--f-mono); font-variant-numeric:tabular-nums; }}

/* ============ Top bar (website only, omitted in the artifact build) ============ */
.topbar {{ border-bottom:1px solid var(--rule-soft); background:var(--surface); }}
/* padding-block, nicht die Kurzform: sonst faellt der horizontale Rand von .wrap weg. */
.topbar-in {{ display:flex; align-items:center; gap:12px; padding-block:8px;
  font-family:var(--f-mono); font-size:11.5px; flex-wrap:wrap; }}
.tb-brand {{ font-weight:600; color:var(--ink); text-decoration:none;
  letter-spacing:.03em; text-transform:uppercase; }}
.tb-brand:hover {{ color:var(--accent); }}
.tb-lang {{ margin-left:auto; display:flex; gap:3px; }}
.tb-lang a {{ padding:3px 9px; color:var(--ink-3); text-decoration:none;
  border:1px solid var(--rule); border-radius:2px; }}
.tb-lang a:hover {{ color:var(--ink); border-color:var(--ink-3); }}
.tb-lang a[aria-current="page"] {{ color:var(--accent-ink); background:var(--accent);
  border-color:var(--accent); }}
.tb-repo {{ color:var(--ink-3); text-decoration:none; }}
.tb-repo:hover {{ color:var(--accent); }}

/* ============ Masthead ============ */
.mast {{ border-bottom:1px solid var(--rule); padding:clamp(28px,5vw,56px) 0 0; }}
.mast-in {{ display:grid; grid-template-columns:minmax(0,1fr); gap:22px;
  padding-bottom:clamp(24px,4vw,40px); }}
@media (min-width:900px) {{ .mast-in {{ grid-template-columns:minmax(0,7fr) minmax(0,5fr);
  gap:clamp(32px,5vw,72px); align-items:end; }} }}
.mast h1 {{ font-size:clamp(40px,7vw,76px); line-height:.95; letter-spacing:-.025em;
  font-weight:700; margin:10px 0 0; }}
.mast h1 em {{ font-family:var(--f-body); font-style:italic; font-weight:400;
  letter-spacing:-.01em; color:var(--ink-2); }}
.mast .k-lede {{ font-size:clamp(17px,1.5vw,20px); line-height:1.5; color:var(--ink-2);
  max-width:56ch; margin-top:18px; }}
.mast .k-lede strong {{ color:var(--ink); font-weight:500; }}
.facts {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  border-top:1px solid var(--rule); }}
@media (min-width:520px) {{ .facts {{ grid-template-columns:repeat(4,minmax(0,1fr)); }} }}
.facts div {{ padding:14px 14px 14px 0; border-right:1px solid var(--rule-soft); }}
.facts div:last-child {{ border-right:0; }}
.facts b {{ display:block; font-family:var(--f-disp); font-size:26px; font-weight:600;
  font-variant-numeric:tabular-nums; line-height:1.1; }}
.facts span {{ font-family:var(--f-mono); font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); }}

/* ============ Primer ============ */
.primer {{ border-bottom:1px solid var(--rule); padding:clamp(28px,4vw,44px) 0; }}
.primer-head {{ max-width:64ch; margin-bottom:26px; }}
.primer-head h2 {{ font-size:clamp(20px,2.2vw,26px); margin-bottom:8px; }}
.primer-head p {{ color:var(--ink-2); }}
.params {{ display:grid; gap:1px; background:var(--rule-soft);
  border:1px solid var(--rule-soft); grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); }}
.params > div {{ background:var(--surface); padding:14px 16px 16px; }}
.params dt {{ font-family:var(--f-disp); font-weight:600; font-size:15px;
  display:flex; align-items:baseline; gap:8px; }}
.params dt i {{ font-family:var(--f-mono); font-style:normal; font-size:10px;
  color:var(--brass); letter-spacing:.1em; }}
.params dd {{ margin:5px 0 0; font-size:13.5px; line-height:1.5; color:var(--ink-2); }}
.params dd em {{ font-family:var(--f-mono); font-style:normal; font-size:11.5px;
  color:var(--ink-3); display:block; margin-top:5px; }}

/* ============ Steuerleiste ============ */
.k-bar {{ position:sticky; top:0; z-index:40; background:var(--ground);
  border-bottom:1px solid var(--rule); }}
.bar-in {{ display:flex; flex-wrap:wrap; gap:10px 14px; align-items:center;
  padding:11px 0; }}
.chips {{ display:flex; flex-wrap:wrap; gap:6px; flex:1 1 auto; min-width:0; }}
/* On narrow screens eight chips would swell the sticky bar to five rows and cover half
   the viewport, so there they become one horizontally scrollable row. */
@media (max-width:820px) {{
  .chips {{ flex-wrap:nowrap; overflow-x:auto; scrollbar-width:none;
    padding-bottom:2px; -webkit-overflow-scrolling:touch; }}
  .chips::-webkit-scrollbar {{ display:none; }}
  .k-chip {{ flex:0 0 auto; }}
}}
.k-chip {{ font-family:var(--f-mono); font-size:11.5px; letter-spacing:.02em;
  padding:5px 10px; border:1px solid var(--rule); background:transparent;
  color:var(--ink-2); cursor:pointer; border-radius:2px; }}
.k-chip:hover {{ border-color:var(--ink-3); color:var(--ink); }}
.k-chip[aria-pressed="true"] {{ background:var(--accent); border-color:var(--accent);
  color:var(--accent-ink); }}
.ctl {{ display:flex; align-items:center; gap:7px; }}
.ctl label {{ font-family:var(--f-mono); font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); }}
.k-bar select, .k-bar input {{ font-family:var(--f-mono); font-size:12px; color:var(--ink);
  background:var(--surface); border:1px solid var(--rule); border-radius:2px;
  padding:5px 8px; }}
.k-bar input {{ width:150px; }}
.k-bar input::placeholder {{ color:var(--ink-3); }}
#tally {{ font-family:var(--f-mono); font-size:11px; color:var(--ink-3);
  font-variant-numeric:tabular-nums; }}

/* ============ Familien & Raster ============ */
.fam {{ padding:clamp(30px,4vw,52px) 0 0; }}
.fam-head {{ display:grid; gap:8px; padding-bottom:22px; border-bottom:1px solid var(--rule);
  margin-bottom:26px; }}
@media (min-width:860px) {{ .fam-head {{
  grid-template-columns:minmax(0,1fr) minmax(0,1.4fr) auto;
  gap:8px clamp(24px,4vw,60px); align-items:start; }} }}
.fam-head h2 {{ font-size:clamp(23px,2.6vw,31px); }}
.fam-head p {{ color:var(--ink-2); font-size:15.5px; max-width:62ch; }}
.fam-count {{ font-family:var(--f-mono); font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); }}
@media (min-width:860px) {{ .fam-count {{ justify-self:end; padding-top:6px;
  white-space:nowrap; }} }}
.grid {{ display:grid; gap:clamp(20px,2.4vw,32px);
  grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr)); }}

/* ============ Plate ============ */
.plate-frame {{ position:relative; overflow:hidden; border:1px solid var(--rule);
  background:var(--surface-2); transition:border-color .16s, box-shadow .16s;
  min-height:120px; cursor:pointer; }}
.k-plate:hover .plate-frame {{ border-color:var(--ink-3); box-shadow:var(--shadow); }}
/* A demo is exhibit, not control: `inert` removes it from the tab order and the
   accessibility tree, pointer-events removes it from the click path. */
.demo-host {{ width:780px; transform-origin:0 0; pointer-events:none; }}
.plate-open {{ font:inherit; font-family:var(--f-disp); font-size:19px; font-weight:600;
  letter-spacing:-.01em; background:none; border:0; padding:0; margin:0;
  color:inherit; cursor:pointer; text-align:left; }}
.k-plate:hover .plate-open {{ color:var(--accent); }}
.plate-open:hover {{ text-decoration:underline; text-underline-offset:3px; }}
/* Equal-height grid cells plus margin-auto put every score strip in a row on one
   baseline, even though the demos have different heights. */
.k-plate {{ display:flex; flex-direction:column; }}
.plate-meta {{ padding-top:12px; display:flex; flex-direction:column; flex:1 1 auto; }}
.plate-line {{ display:flex; align-items:baseline; gap:9px; flex-wrap:wrap; }}
.ent {{ font-family:var(--f-mono); font-size:11px; font-weight:600; color:var(--brass);
  font-variant-numeric:tabular-nums; }}
.plate-line h3 {{ font-size:19px; flex:1 1 auto; min-width:0; font-weight:600; }}
.era {{ font-family:var(--f-mono); font-size:10.5px; color:var(--ink-3);
  font-variant-numeric:tabular-nums; }}
.idea {{ font-size:14.5px; line-height:1.5; color:var(--ink-2); margin-top:6px;
  display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical;
  line-clamp:3; overflow:hidden; }}
.scores {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:9px;
  margin-top:auto; padding-top:10px; border-top:1px solid var(--rule-soft); }}
.sc {{ display:grid; gap:3px; }}
.sc-k {{ font-family:var(--f-mono); font-size:9.5px; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3); }}
.sc-bar {{ display:flex; gap:2px; align-items:center; }}
.sc-bar i {{ display:block; height:3px; flex:1 1 0; background:var(--rule);
  border-radius:1px; }}
.sc-bar i.on {{ background:var(--accent); }}
.sc-v {{ display:none; }}

/* ============ Detail ============ */
.k-sheet {{ position:fixed; inset:0; z-index:100; background:var(--ground);
  overflow-y:auto; overscroll-behavior:contain; }}
.sheet-bar {{ position:sticky; top:0; z-index:5; background:var(--ground);
  border-bottom:1px solid var(--rule); }}
.sheet-bar-in {{ display:flex; align-items:center; gap:12px; padding:10px 0; }}
.sheet-bar .ent {{ font-size:12px; }}
.sheet-bar h2 {{ font-size:19px; flex:1 1 auto; min-width:0; }}
.nav-b {{ font-family:var(--f-mono); font-size:12px; padding:5px 10px;
  border:1px solid var(--rule); background:var(--surface); color:var(--ink);
  cursor:pointer; border-radius:2px; }}
.nav-b:hover:not(:disabled) {{ border-color:var(--ink-3); }}
.nav-b:disabled {{ opacity:.35; cursor:default; }}
.sheet-body {{ display:grid; gap:clamp(24px,3vw,44px); padding:clamp(20px,3vw,36px) 0 90px;
  align-items:start; }}
@media (min-width:1040px) {{ .sheet-body {{ grid-template-columns:minmax(0,1fr) minmax(0,1fr); }}
  .sheet-left {{ position:sticky; top:66px; }} }}
.sheet-frame {{ position:relative; overflow:hidden; border:1px solid var(--rule);
  background:var(--surface-2); }}
.sheet-host {{ width:780px; transform-origin:0 0; pointer-events:none; }}
.k-cap {{ font-family:var(--f-mono); font-size:10.5px; color:var(--ink-3); margin-top:9px;
  line-height:1.5; }}
.swatches {{ display:flex; flex-wrap:wrap; gap:0; margin-top:16px;
  border:1px solid var(--rule-soft); }}
.swatches div {{ flex:1 1 74px; }}
.swatches i {{ display:block; height:44px; }}
.swatches span {{ display:block; font-family:var(--f-mono); font-size:10px;
  padding:5px 6px; color:var(--ink-2); border-top:1px solid var(--rule-soft);
  background:var(--surface); }}
.sheet-right > * + * {{ margin-top:26px; }}
.blk h4 {{ font-family:var(--f-mono); font-size:10.5px; font-weight:500;
  letter-spacing:.13em; text-transform:uppercase; color:var(--brass);
  padding-bottom:7px; border-bottom:1px solid var(--rule); margin-bottom:11px; }}
.blk p {{ font-size:15.5px; line-height:1.62; }}
.blk p + p {{ margin-top:9px; }}
.blk ul {{ list-style:none; padding:0; margin:0; display:grid; gap:8px; }}
.blk li {{ font-size:14.5px; line-height:1.55; padding-left:17px; position:relative; }}
.blk li::before {{ content:""; position:absolute; left:0; top:.6em; width:7px; height:1px;
  background:var(--brass); }}
.blk.risks li::before {{ background:var(--ink-3); }}
.kv {{ display:grid; gap:1px; background:var(--rule-soft); border:1px solid var(--rule-soft); }}
.kv > div {{ background:var(--surface); padding:9px 12px; display:grid;
  grid-template-columns:104px minmax(0,1fr); gap:12px; align-items:baseline; }}
.kv dt {{ font-family:var(--f-mono); font-size:10.5px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-3); }}
.kv dd {{ margin:0; font-size:14px; line-height:1.5; }}
.ex {{ display:grid; gap:10px; }}
.ex > div {{ border-left:2px solid var(--rule); padding-left:13px; }}
.ex b {{ font-family:var(--f-disp); font-size:15px; font-weight:600; display:block; }}
.ex span {{ font-size:13.5px; line-height:1.5; color:var(--ink-2); }}
.tip {{ background:var(--accent-soft); border-left:2px solid var(--accent);
  padding:14px 16px; }}
.tip p {{ font-size:14.5px; line-height:1.6; }}
.verdict {{ border:1px solid var(--rule); padding:16px 18px; background:var(--surface); }}
.tags {{ display:flex; flex-wrap:wrap; gap:6px; }}
.k-tag {{ font-family:var(--f-mono); font-size:11px; padding:4px 9px;
  border:1px solid var(--rule); color:var(--ink-2); background:transparent;
  cursor:pointer; border-radius:2px; }}
.k-tag:hover {{ border-color:var(--accent); color:var(--accent); }}
.k-tag.static {{ cursor:default; }}
.k-tag.static:hover {{ border-color:var(--rule); color:var(--ink-2); }}

/* ============ Stil-Finder ============ */
.fi-open {{ font-family:var(--f-mono); font-size:11.5px; letter-spacing:.02em;
  padding:5px 11px; border:1px solid var(--accent); background:var(--accent);
  color:var(--accent-ink); cursor:pointer; border-radius:2px; white-space:nowrap; }}
.fi-open:hover {{ filter:brightness(1.12); }}
.k-finder {{ position:fixed; inset:0; z-index:110; background:var(--ground);
  overflow-y:auto; overscroll-behavior:contain; }}
.fi-bar {{ position:sticky; top:0; z-index:5; background:var(--ground);
  border-bottom:1px solid var(--rule); }}
.fi-bar-in {{ display:flex; align-items:center; gap:12px; padding:10px 0; flex-wrap:wrap; }}
.fi-bar h2 {{ font-size:19px; flex:1 1 auto; min-width:0; }}
.fi-body {{ padding:clamp(22px,3vw,40px) 0 90px; }}
.fi-lede {{ max-width:62ch; color:var(--ink-2); font-size:15.5px; margin-bottom:26px; }}

.fi-q {{ border-top:1px solid var(--rule); padding:18px 0 20px; display:grid; gap:10px; }}
@media (min-width:900px) {{ .fi-q {{ grid-template-columns:minmax(0,280px) minmax(0,1fr);
  gap:10px clamp(24px,4vw,56px); align-items:start; }} }}
.fi-q > div:first-child {{ display:grid; gap:4px; align-content:start; }}
.fi-q h3 {{ font-size:17px; }}
.fi-q p {{ font-family:var(--f-mono); font-size:11px; color:var(--ink-3); line-height:1.5; }}
.fi-opts {{ display:flex; flex-wrap:wrap; gap:7px; }}
.fi-opt {{ font-family:var(--f-disp); font-size:14px; font-weight:500; padding:7px 13px;
  border:1px solid var(--rule); background:var(--surface); color:var(--ink-2);
  cursor:pointer; border-radius:2px; text-align:left; }}
.fi-opt:hover {{ border-color:var(--ink-3); color:var(--ink); }}
.fi-opt[aria-pressed="true"] {{ background:var(--accent); border-color:var(--accent);
  color:var(--accent-ink); }}
.fi-go {{ position:sticky; bottom:0; background:var(--ground); border-top:1px solid var(--rule);
  padding:14px 0; display:flex; gap:14px; align-items:center; flex-wrap:wrap; margin-top:8px; }}
.fi-go button {{ font-family:var(--f-disp); font-size:16px; font-weight:600; padding:10px 22px;
  border:1px solid var(--accent); background:var(--accent); color:var(--accent-ink);
  cursor:pointer; border-radius:2px; }}
.fi-go button:disabled {{ opacity:.4; cursor:default; }}
.fi-go span {{ font-family:var(--f-mono); font-size:11.5px; color:var(--ink-3); }}

.fi-res {{ display:grid; gap:clamp(20px,2.5vw,34px); }}
.fi-card {{ border:1px solid var(--rule); background:var(--surface); }}
.fi-card-head {{ display:flex; align-items:baseline; gap:11px; padding:14px 16px 12px;
  flex-wrap:wrap; border-bottom:1px solid var(--rule-soft); }}
.fi-rank {{ font-family:var(--f-mono); font-size:12px; font-weight:600; color:var(--accent-ink);
  background:var(--accent); padding:2px 8px; border-radius:2px; }}
.fi-card-head h3 {{ font-size:21px; flex:1 1 auto; min-width:0; }}
.fi-score {{ font-family:var(--f-mono); font-size:12px; color:var(--ink-3);
  font-variant-numeric:tabular-nums; }}
.fi-card-body {{ display:grid; gap:clamp(16px,2vw,28px); padding:16px; }}
@media (min-width:940px) {{ .fi-card-body {{ grid-template-columns:minmax(0,1fr) minmax(0,1fr); }} }}
.fi-frame {{ position:relative; overflow:hidden; border:1px solid var(--rule);
  background:var(--surface-2); }}
.fi-host {{ width:780px; transform-origin:0 0; pointer-events:none; }}
.fi-sig {{ font-size:15px; line-height:1.55; }}
.fi-why {{ list-style:none; padding:0; margin:12px 0 0; display:grid; gap:6px; }}
.fi-why li {{ font-size:13.5px; line-height:1.5; padding-left:18px; position:relative;
  color:var(--ink-2); }}
.fi-why li::before {{ content:""; position:absolute; left:0; top:.62em; width:8px; height:1px;
  background:var(--brass); }}
.fi-why li.no::before {{ background:var(--ink-3); }}
.fi-why li.no {{ color:var(--ink-3); }}
.fi-acts {{ display:flex; gap:9px; flex-wrap:wrap; margin-top:16px; }}
.fi-acts button {{ font-family:var(--f-mono); font-size:12px; padding:7px 12px;
  border:1px solid var(--rule); background:var(--surface-2); color:var(--ink);
  cursor:pointer; border-radius:2px; }}
.fi-acts button:hover {{ border-color:var(--accent); color:var(--accent); }}
.fi-acts button.prim {{ border-color:var(--accent); background:var(--accent);
  color:var(--accent-ink); }}
.fi-acts button.prim:hover {{ filter:brightness(1.12); color:var(--accent-ink); }}
.fi-acts button.ok {{ border-color:var(--brass); color:var(--brass); }}
.fi-hint {{ margin-top:12px; font-family:var(--f-mono); font-size:11.5px;
  color:var(--brass); line-height:1.5; }}
.fi-hint + .fi-pre {{ margin-top:6px; }}
.fi-pre {{ margin-top:12px; background:var(--surface-2); border:1px solid var(--rule);
  padding:12px; font-family:var(--f-mono); font-size:11px; line-height:1.55;
  white-space:pre-wrap; max-height:300px; overflow:auto; color:var(--ink-2); }}
.fi-note {{ font-family:var(--f-mono); font-size:11.5px; color:var(--ink-3);
  border-top:1px solid var(--rule-soft); margin-top:30px; padding-top:16px;
  line-height:1.7; max-width:74ch; }}

/* ============ Matrix ============ */
.mx {{ border-top:1px solid var(--rule); padding:clamp(38px,5vw,64px) 0 0; }}
.mx-head {{ display:grid; gap:14px; margin-bottom:24px; }}
@media (min-width:900px) {{ .mx-head {{ grid-template-columns:minmax(0,1fr) auto;
  align-items:end; gap:30px; }} }}
.mx-head h2 {{ font-size:clamp(23px,2.6vw,31px); }}
.mx-head p {{ color:var(--ink-2); max-width:60ch; margin-top:7px; }}
.mx-ctl {{ display:flex; gap:14px; flex-wrap:wrap; }}
.mx-ctl select {{ font-family:var(--f-mono); font-size:12px; color:var(--ink);
  background:var(--surface); border:1px solid var(--rule); border-radius:2px; padding:5px 8px; }}
.mx-ctl label {{ font-family:var(--f-mono); font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); display:block; margin-bottom:4px; }}
.mx-scroll {{ overflow-x:auto; }}
.mx-plot {{ display:grid; grid-template-columns:auto repeat(5,minmax(126px,1fr));
  min-width:700px; }}
.mx-yl {{ grid-row:2/7; grid-column:1; display:flex; align-items:center;
  justify-content:center; }}
.mx-yl span {{ writing-mode:vertical-rl; transform:rotate(180deg);
  font-family:var(--f-mono); font-size:10.5px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--ink-3); }}
.mx-cell {{ border-right:1px solid var(--rule-soft); border-bottom:1px solid var(--rule-soft);
  padding:8px; min-height:78px; display:flex; flex-direction:column; gap:4px;
  background:var(--surface); }}
.mx-cell.hot {{ background:var(--accent-soft); }}
.mx-cell b {{ font-family:var(--f-mono); font-size:9.5px; color:var(--ink-3);
  font-variant-numeric:tabular-nums; }}
.mx-chip {{ font-family:var(--f-disp); font-size:12.5px; font-weight:500;
  text-align:left; background:none; border:0; padding:1px 0; cursor:pointer;
  color:var(--ink); line-height:1.3; }}
.mx-chip:hover {{ color:var(--accent); text-decoration:underline; }}
.mx-ax {{ font-family:var(--f-mono); font-size:10.5px; color:var(--ink-3);
  padding:7px 8px; text-align:center; font-variant-numeric:tabular-nums; }}
.mx-corner {{ grid-column:1; }}
.mx-note {{ font-family:var(--f-mono); font-size:11px; color:var(--ink-3);
  margin-top:11px; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
.mx-note i {{ display:inline-block; width:13px; height:13px; background:var(--accent-soft);
  border:1px solid var(--rule); }}

/* ============ Tabelle ============ */
.tbl-sec {{ border-top:1px solid var(--rule); padding:clamp(38px,5vw,64px) 0 0;
  margin-top:clamp(38px,5vw,64px); }}
.tbl-sec h2 {{ font-size:clamp(23px,2.6vw,31px); }}
.tbl-sec > p {{ color:var(--ink-2); max-width:62ch; margin:7px 0 22px; }}
.tbl-scroll {{ overflow-x:auto; border:1px solid var(--rule); }}
table {{ border-collapse:collapse; width:100%; min-width:900px; background:var(--surface); }}
th, td {{ text-align:left; padding:8px 12px; border-bottom:1px solid var(--rule-soft);
  font-size:13.5px; vertical-align:top; }}
thead th {{ position:sticky; top:0; background:var(--surface-2); z-index:2;
  font-family:var(--f-mono); font-size:10px; font-weight:500; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink-3); border-bottom:1px solid var(--rule);
  white-space:nowrap; }}
thead th.sortable {{ cursor:pointer; user-select:none; }}
thead th.sortable:hover {{ color:var(--ink); }}
thead th[aria-sort]:not([aria-sort="none"]) {{ color:var(--accent); }}
td.k-num {{ font-family:var(--f-mono); font-variant-numeric:tabular-nums; text-align:right;
  white-space:nowrap; }}
td.nm {{ min-width:190px; }}
td.nm button {{ font-family:var(--f-disp); font-size:14.5px; font-weight:600;
  background:none; border:0; padding:0; cursor:pointer; color:var(--ink);
  text-align:left; display:block; }}
td.nm button:hover {{ color:var(--accent); text-decoration:underline; }}
.row-fam {{ font-family:var(--f-mono); font-size:10px; color:var(--ink-3);
  display:block; margin-top:2px; }}
td.wide {{ min-width:250px; color:var(--ink-2); font-size:13px; }}
tbody tr:hover {{ background:var(--surface-2); }}

/* ============ Schluss ============ */
.k-close {{ border-top:1px solid var(--rule); margin-top:clamp(38px,5vw,64px);
  padding:clamp(38px,5vw,64px) 0 clamp(60px,7vw,100px); }}
.k-close h2 {{ font-size:clamp(23px,2.6vw,31px); margin-bottom:10px; }}
.close-grid {{ display:grid; gap:clamp(20px,3vw,40px); margin-top:26px;
  grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr)); }}
.close-grid > div {{ border-top:2px solid var(--accent); padding-top:14px; }}
.close-grid h3 {{ font-size:17px; margin-bottom:7px; }}
.close-grid p {{ font-size:14.5px; line-height:1.6; color:var(--ink-2); }}
.k-close > p {{ max-width:66ch; color:var(--ink-2); }}
.k-colophon {{ font-family:var(--f-mono); font-size:11px; color:var(--ink-3);
  border-top:1px solid var(--rule-soft); margin-top:40px; padding-top:16px;
  line-height:1.7; }}

.empty {{ padding:60px 0; text-align:center; color:var(--ink-3);
  font-family:var(--f-mono); font-size:13px; }}

@media (prefers-reduced-motion: reduce) {{
  *, .demo-host *, .sheet-host * {{ animation-duration:.001ms !important;
    animation-iteration-count:1 !important; transition-duration:.001ms !important; }}
}}
</style>

{sheets}

{topbar}
<header class="mast">
  <div class="wrap mast-in">
    <div>
      <span class="eyebrow">Referenzkatalog · Designsprache</span>
      <h1>Stil&#8209;Katalog<br><em>{n} Wege, dieselbe Oberfläche zu bauen</em></h1>
    </div>
    <div>
      <p class="k-lede">Jeder Eintrag zeigt <strong>exakt dieselbe Oberfläche</strong> — eine
        Projektliste mit Kopfzeile, drei Einträgen, Suchfeld und zwei Schaltflächen. Was sich
        ändert, ist ausschließlich die Gestaltung. Dadurch wird sichtbar, was ein Stil
        tatsächlich entscheidet — und was nur Geschmack ist.</p>
    </div>
  </div>
  <div class="wrap">
    <div class="facts">
      <div><b>{n}</b><span>Einträge</span></div>
      <div><b>{nfam}</b><span>Familien</span></div>
      <div><b>1</b><span>Referenz&#8209;UI</span></div>
      <div><b>7</b><span>Parameter</span></div>
    </div>
  </div>
</header>

<section class="primer">
  <div class="wrap">
    <div class="primer-head">
      <h2>Die sieben Parameter</h2>
      <p>Stilnamen sind austauschbar. Was einen Stil ausmacht, sind sieben Größen — und
        jede davon ist eine Entscheidung, die man in Tokens schreiben kann. Wer sie kennt, kann
        Stile mischen statt kopieren.</p>
    </div>
    <dl class="params">
      <div><dt>Radius<i>01</i></dt><dd>Von 0&#8239;px bis vollrund. Der am stärksten
        unterschätzte Marken­träger.<em>0 kompromisslos · 6 werkzeughaft · 16+ freundlich</em></dd></div>
      <div><dt>Kontrast<i>02</i></dt><dd>Der Abstand zwischen Grund und Schrift. Entscheidet, ob
        eine Oberfläche ruhig oder laut wirkt.<em>1,5:1 Neumorphismus → 18:1 Swiss</em></dd></div>
      <div><dt>Tiefe<i>03</i></dt><dd>Wie Hierarchie entsteht: gar nicht, über Linien, über
        Schatten, über Unschärfe oder über echte z&#8209;Achse.<em>Der teuerste Parameter im
        Cross&#8209;Platform&#8209;Betrieb</em></dd></div>
      <div><dt>Dichte<i>04</i></dt><dd>Information pro Bildschirm. Zwischen den Extremen liegt
        Faktor fünf.<em>Bloomberg → Apple&#8209;Marketing</em></dd></div>
      <div><dt>Farbe<i>05</i></dt><dd>Wie viel Bedeutung Farbe trägt: monochrom plus Akzent,
        Flächenfarbe oder Verlauf.<em>Der stärkste Wiedererkennungsträger</em></dd></div>
      <div><dt>Typografie<i>06</i></dt><dd>Grotesk, Serif, Monospace oder Display — und in
        welchem Gewichtsband.<em>Der zweitstärkste, meist zu vorsichtig gewählt</em></dd></div>
      <div><dt>Motion<i>07</i></dt><dd>Dauer und Kurve. Die Persönlichkeit einer Oberfläche —
        und der Parameter, der am häufigsten vergessen wird.<em>0&#8239;ms · 120&#8239;ms linear ·
        400&#8239;ms Spring mit Überschwingen</em></dd></div>
    </dl>
  </div>
</section>

<nav class="k-bar" aria-label="Katalog filtern und sortieren">
  <div class="wrap bar-in">
    <div class="chips" role="group" aria-label="Nach Familie filtern">
      <button class="k-chip" type="button" data-fam="*" aria-pressed="true">Alle</button>
      {chips}
    </div>
    <div class="ctl">
      <label for="q">Suche</label>
      <input id="q" type="search" placeholder="Stil, Merkmal …" autocomplete="off">
    </div>
    <div class="ctl">
      <label for="sort">Sortierung</label>
      <select id="sort">
        <option value="cat">Katalog</option>
        <option value="longevity">Haltbarkeit</option>
        <option value="recognition">Wiedererkennung</option>
        <option value="effort">Aufwand (wenig zuerst)</option>
        <option value="density">Dichte</option>
        <option value="name">Name</option>
      </select>
    </div>
    <span id="tally" aria-live="polite">{n} von {n}</span>
    <button class="fi-open" type="button" id="fi-open">Stil finden</button>
  </div>
</nav>

<main class="wrap" id="cat">{sections}
  <p class="empty" id="empty" hidden>Kein Eintrag passt zu dieser Auswahl.</p>
</main>

<section class="mx wrap">
  <div class="mx-head">
    <div>
      <span class="eyebrow">Entscheidungsraster</span>
      <h2>Haltbarkeit gegen Wiedererkennung</h2>
      <p>Die beiden Größen stehen in Spannung: Was sofort erkennbar ist, altert meist
        schneller. Alle Werte sind ganzzahlig von 1 bis 5, deshalb ein Raster statt eines
        Streudiagramms — Einträge auf derselben Position verdecken sich hier nicht.</p>
    </div>
    <div class="mx-ctl">
      <div><label for="mx">Waagerecht</label><select id="mx">{mx}</select></div>
      <div><label for="my">Senkrecht</label><select id="my">{my}</select></div>
    </div>
  </div>
  <div class="mx-scroll"><div class="mx-plot" id="plot"></div></div>
  <p class="mx-note"><i></i> <span id="mxnote"></span></p>
</section>

<section class="tbl-sec wrap">
  <h2>Alle {n} im Vergleich</h2>
  <p>Die harten Parameter nebeneinander. Spalten mit Zahlen sind sortierbar — Kopfzeile
    anklicken. Ein Klick auf den Namen öffnet den vollständigen Eintrag.</p>
  <div class="tbl-scroll">
    <table>
      <thead><tr>
        <th>Nr.</th><th>Stil</th><th>Radius</th><th>Kontrast</th><th>Dichte</th><th>Tiefe</th>
        <th class="sortable k-num" data-col="6" aria-sort="none">Haltb.</th>
        <th class="sortable k-num" data-col="7" aria-sort="none">Wiedererk.</th>
        <th class="sortable k-num" data-col="8" aria-sort="none">Aufwand</th>
      </tr></thead>
      <tbody id="tbody">{rows}</tbody>
    </table>
  </div>
</section>

<section class="k-close wrap">
  <span class="eyebrow">Wie es weitergeht</span>
  <h2>Vom Katalog zur eigenen Sprache</h2>
  <p>Ein Katalog ist keine Entscheidung. Drei Dinge sind beim Durchsehen nützlicher als die
    Frage „welcher gefällt mir“ — denn die beantwortet man in fünf Jahren anders.</p>
  <div class="close-grid">
    <div>
      <h3>Marken sind Hybride</h3>
      <p>Kein starkes Produkt trägt einen Reinstil. Linear ist Swiss&#8209;Raster plus
        Dark&#8209;Mode plus Terminal&#8209;Dichte. Notion ist Warm Editorial plus Flat. Stripe ist
        Swiss plus Aurora. Ein Reinstil wirkt wie ein Kostüm; eine Mischung aus zwei Familien
        mit einer klaren Hauptstimme wirkt wie eine Haltung. Jeder Eintrag nennt unter
        „Kombiniert sich mit“ die tragfähigen Paarungen.</p>
    </div>
    <div>
      <h3>Haltbarkeit schlägt Wirkung</h3>
      <p>Für einen Fundus, der viele Apps über Jahre tragen soll, ist Haltbarkeit
        wertvoller als Schockwirkung. Ein Stil mit Wiedererkennung 5 und Haltbarkeit 1 kostet
        dich in drei Jahren einen vollständigen Neuentwurf — über alle Projekte gleichzeitig.
        Das Raster oben macht diesen Handel sichtbar.</p>
    </div>
    <div>
      <h3>Der Stil bestimmt die Kosten</h3>
      <p>Flächenfarbe, Radius und Typografie lassen sich aus Tokens sauber nach CSS,
        Compose und SwiftUI generieren. Unschärfe, mehrschichtige Verläufe und Materialien
        nicht — die musst du auf jeder Plattform von Hand nachbauen. Glassmorphism und
        Skeuomorphismus kosten über Web, Tauri und Android ein Vielfaches von Swiss oder
        Dev&#8209;Noir. Das ist keine Geschmacksfrage, sondern eine Aufwandsschätzung.</p>
    </div>
  </div>
  <p class="k-colophon">Alle {n} Demos sind handgebautes HTML und CSS — keine Bilder, keine
    Skripte, keine Bibliotheken. Jede zeigt dieselben dreizehn Textbausteine. Die Schriften
    stammen von Google Fonts, alle Farbwerte, Radien und Zeitangaben in den Faktenblättern
    sind aus den jeweiligen Vorbildern belegt. Die vier Kennzahlen sind fachliche
    Einschätzungen, keine Messwerte.</p>
</section>

<div class="k-finder" id="finder" hidden>
  <div class="fi-bar"><div class="wrap fi-bar-in">
    <h2 id="fi-title">Welcher Stil passt zu deinem Projekt?</h2>
    <button class="nav-b" type="button" id="fi-again" hidden>Antworten ändern</button>
    <button class="nav-b" type="button" id="fi-close">Schließen · Esc</button>
  </div></div>
  <div class="wrap fi-body">
    <p class="fi-lede" id="fi-lede">Acht Fragen. Die Empfehlung entsteht aus den Merkmalen der
      Faktenblätter, nicht aus Geschmack — jeder Treffer wird begründet. Du kannst die
      Eigenschaften des empfohlenen Stils anschließend als Anweisung für einen KI-Agenten
      kopieren.</p>
    <div id="fi-quiz"></div>
    <div id="fi-results" hidden></div>
  </div>
</div>

<div class="k-sheet" id="sheet" hidden>
  <div class="sheet-bar"><div class="wrap sheet-bar-in">
    <span class="ent" id="s-ent"></span>
    <h2 id="s-name"></h2>
    <button class="nav-b" type="button" id="s-prev" aria-label="Voriger Eintrag">←</button>
    <button class="nav-b" type="button" id="s-next" aria-label="Nächster Eintrag">→</button>
    <button class="nav-b" type="button" id="s-close">Schließen · Esc</button>
  </div></div>
  <div class="wrap sheet-body">
    <div class="sheet-left">
      <div class="sheet-frame"><div class="sheet-host" id="s-host" inert></div></div>
      <p class="k-cap" id="s-cap"></p>
      <div class="swatches" id="s-pal"></div>
    </div>
    <div class="sheet-right" id="s-right"></div>
  </div>
</div>

<script type="application/json" id="payload">{payload}</script>
<script>
(function () {{
  "use strict";
  var DATA = JSON.parse(document.getElementById("payload").textContent);
  var W = 780;
  var SITE = "{site}", LANG = "{lang}";
  var plates = Array.prototype.slice.call(document.querySelectorAll(".k-plate"));
  var order = plates.map(function (p) {{ return p.dataset.slug; }});
  var METRIC = {{
    longevity: {{ label: "Haltbarkeit", good: "hoch" }},
    recognition: {{ label: "Wiedererkennung", good: "hoch" }},
    effort: {{ label: "Aufwand", good: "niedrig" }},
    density: {{ label: "Dichte", good: null }}
  }};

  /* ---------- Demos in ihre Rahmen skalieren ---------- */
  function fit(host) {{
    var frame = host.parentElement;
    if (!frame || !frame.clientWidth) return;
    var k = frame.clientWidth / W;
    host.style.transform = "scale(" + k + ")";
    frame.style.height = Math.round(host.scrollHeight * k) + "px";
  }}
  function fitAll() {{
    document.querySelectorAll(".demo-host").forEach(fit);
    if (!sheet.hidden) fit(sHost);
  }}
  /* setTimeout rather than requestAnimationFrame on purpose: rAF never fires in a
     hidden tab, and this page is often opened in a background tab. */
  var tmr = 0;
  function schedule() {{ clearTimeout(tmr); tmr = setTimeout(fitAll, 50); }}
  window.addEventListener("resize", schedule);
  document.addEventListener("visibilitychange", schedule);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(schedule);
  [0, 250, 900, 2200].forEach(function (d) {{ setTimeout(schedule, d); }});

  /* React to frame width changes without a window resize
     (sorting, filtering, an appearing scrollbar). */
  if (window.ResizeObserver) {{
    var seen = new WeakMap();
    var ro = new ResizeObserver(function (entries) {{
      var need = false;
      entries.forEach(function (e) {{
        var w = Math.round(e.contentRect.width);
        if (seen.get(e.target) !== w) {{ seen.set(e.target, w); need = true; }}
      }});
      if (need) schedule();
    }});
    document.querySelectorAll(".plate-frame, .sheet-frame").forEach(function (f) {{ ro.observe(f); }});
  }}

  /* ---------- Filtern & Sortieren ---------- */
  var chips = Array.prototype.slice.call(document.querySelectorAll(".k-chip"));
  var q = document.getElementById("q");
  var sortSel = document.getElementById("sort");
  var tally = document.getElementById("tally");
  var empty = document.getElementById("empty");
  var fam = "*";

  function apply() {{
    var term = q.value.trim().toLowerCase();
    var shown = 0;
    document.querySelectorAll(".fam").forEach(function (sec) {{
      var any = 0;
      sec.querySelectorAll(".k-plate").forEach(function (p) {{
        var ok = (fam === "*" || p.dataset.family === fam) &&
                 (!term || p.dataset.search.indexOf(term) !== -1);
        p.hidden = !ok;
        if (ok) {{ any++; shown++; }}
      }});
      sec.hidden = !any;
    }});
    tally.textContent = shown + " von {n}";
    empty.hidden = shown !== 0;
    schedule();
  }}

  chips.forEach(function (c) {{
    c.addEventListener("click", function () {{
      fam = c.dataset.fam;
      chips.forEach(function (o) {{ o.setAttribute("aria-pressed", String(o === c)); }});
      apply();
    }});
  }});
  q.addEventListener("input", apply);

  sortSel.addEventListener("change", function () {{
    var v = sortSel.value;
    document.querySelectorAll(".fam").forEach(function (sec) {{
      var grid = sec.querySelector(".grid");
      var items = Array.prototype.slice.call(grid.children);
      items.sort(function (a, b) {{
        if (v === "cat") return +a.dataset.idx - +b.dataset.idx;
        if (v === "name") return DATA[a.dataset.slug].name.localeCompare(DATA[b.dataset.slug].name, "de");
        var d = +b.dataset[v] - +a.dataset[v];
        if (v === "effort") d = -d;
        return d || (+a.dataset.idx - +b.dataset.idx);
      }});
      items.forEach(function (i) {{ grid.appendChild(i); }});
    }});
    schedule();
  }});

  /* ---------- Detailansicht ---------- */
  var sheet = document.getElementById("sheet");
  var sHost = document.getElementById("s-host");
  var sRight = document.getElementById("s-right");
  var sName = document.getElementById("s-name");
  var sEnt = document.getElementById("s-ent");
  var sCap = document.getElementById("s-cap");
  var sPal = document.getElementById("s-pal");
  var prevB = document.getElementById("s-prev");
  var nextB = document.getElementById("s-next");
  var cur = -1, lastFocus = null;

  function esc(s) {{
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {{
      return {{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }}[c];
    }});
  }}
  function list(items, cls) {{
    return '<ul class="' + (cls ||"") + '">' +
      (items || []).map(function (x) {{ return "<li>" + esc(x) + "</li>"; }}).join("") + "</ul>";
  }}
  function blk(title, inner, cls) {{
    return '<div class="blk ' + (cls ||"") + '"><h4>' + esc(title) + "</h4>" + inner + "</div>";
  }}

  function open(i) {{
    if (i < 0 || i >= order.length) return;
    cur = i;
    var slug = order[i], d = DATA[slug];
    var src = document.querySelector('.k-plate[data-slug="' + slug + '"] .demo-host');
    sHost.textContent = "";
    sHost.appendChild(src.firstElementChild.cloneNode(true));
    sEnt.textContent = String(i + 1).padStart(2, "0");
    sName.textContent = d.name;
    sCap.textContent = "Dieselbe Referenz-UI wie in allen {n} Einträgen, hier in voller Größe.";

    sPal.innerHTML = (d.palette || []).map(function (h) {{
      return '<div><i style="background:' + esc(h) + '"></i><span>' + esc(h) + "</span></div>";
    }}).join("");

    var p = d.params || {{}}, pl = d.platforms || {{}}, sc = d.scores || {{}};
    var html = "";
    html += blk("Kernidee", "<p>" + esc(d.idea) + "</p>");
    html += blk("Herkunft", "<p>" + esc(d.origin) + "</p>");
    html += blk("Woran man ihn erkennt", list(d.markers));
    html += blk("Parameter",
      '<dl class="kv">' +
      [["Radius", p.radius], ["Kontrast", p.contrast], ["Dichte", p.density],
       ["Tiefe", p.depth], ["Farbe", p.color], ["Typografie", p.type],
       ["Motion", p.motion], ["Textur", p.texture]]
      .filter(function (r) {{ return r[1]; }})
      .map(function (r) {{ return "<div><dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd></div>"; }})
      .join("") + "</dl>");
    html += blk("Kennzahlen",
      '<dl class="kv">' + Object.keys(METRIC).map(function (k) {{
        return "<div><dt>" + esc(METRIC[k].label) + "</dt><dd>" + (sc[k] || 0) +
          " von 5</dd></div>";
      }}).join("") + "</dl>");
    html += blk("Echte Vertreter", '<div class="ex">' + (d.examples || []).map(function (e) {{
      return "<div><b>" + esc(e.name) + "</b><span>" + esc(e.what) + "</span></div>";
    }}).join("") + "</div>");
    html += blk("Stärken", list(d.strengths));
    html += blk("Risiken", list(d.risks, "risks-x"), "risks");
    html += blk("Barrierefreiheit", "<p>" + esc(d.a11y) + "</p>");
    html += blk("Alterungsverhalten", "<p>" + esc(d.longevity) + "</p>");
    html += blk("Plattformen",
      '<dl class="kv">' +
      [["Web", pl.web], ["Mobile", pl.mobile], ["Desktop", pl.desktop]]
      .filter(function (r) {{ return r[1]; }})
      .map(function (r) {{ return "<div><dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd></div>"; }})
      .join("") + "</dl>");
    html += blk("Praxistipp", '<div class="tip"><p>' + esc(d.tip) + "</p></div>");
    html += blk("Als Basis für eine Eigenmarke",
      '<div class="verdict"><p>' + esc(d.verdict) + "</p></div>");
    html += blk("Kombiniert sich mit", '<div class="tags">' +
      (d.combinesWith || []).filter(function (s) {{ return DATA[s]; }}).map(function (s) {{
        return '<button class="k-tag" type="button" data-go="' + esc(s) + '">' +
          esc(DATA[s].name) + "</button>";
      }}).join("") + "</div>");
    if ((d.aka || []).length) {{
      html += blk("Auch bekannt als", '<div class="tags">' + d.aka.map(function (a) {{
        return '<span class="k-tag static">' + esc(a) + "</span>";
      }}).join("") + "</div>");
    }}
    sRight.innerHTML = html;

    prevB.disabled = i === 0;
    nextB.disabled = i === order.length - 1;
    sheet.hidden = false;
    document.body.style.overflow = "hidden";
    sheet.scrollTop = 0;
    [0, 60, 300].forEach(function (d) {{ setTimeout(function () {{ fit(sHost); }}, d); }});
  }}

  function close() {{
    sheet.hidden = true;
    document.body.style.overflow = "";
    sHost.textContent = "";
    if (lastFocus) {{ try {{ lastFocus.focus(); }} catch (e) {{}} }}
  }}

  /* Both the title button (keyboard, screen reader) and the demo surface itself
     (mouse) open the entry. */
  document.getElementById("cat").addEventListener("click", function (e) {{
    var hit = e.target.closest(".plate-open, [data-open]");
    if (!hit) return;
    var plate = hit.closest(".k-plate");
    if (!plate) return;
    lastFocus = plate.querySelector(".plate-open");
    open(order.indexOf(plate.dataset.slug));
    document.getElementById("s-close").focus();
  }});
  document.getElementById("s-close").addEventListener("click", close);
  prevB.addEventListener("click", function () {{ open(cur - 1); }});
  nextB.addEventListener("click", function () {{ open(cur + 1); }});
  sRight.addEventListener("click", function (e) {{
    var t = e.target.closest("[data-go]");
    if (t) open(order.indexOf(t.dataset.go));
  }});
  document.addEventListener("keydown", function (e) {{
    if (sheet.hidden) return;
    if (e.key === "Escape") {{ e.preventDefault(); close(); }}
    else if (e.key === "ArrowLeft" && cur > 0) open(cur - 1);
    else if (e.key === "ArrowRight" && cur < order.length - 1) open(cur + 1);
  }});

  /* ---------- Entscheidungsraster ---------- */
  var mxS = document.getElementById("mx"), myS = document.getElementById("my");
  var plot = document.getElementById("plot"), mxnote = document.getElementById("mxnote");

  function drawPlot() {{
    var xk = mxS.value, yk = myS.value;
    var cells = {{}};
    order.forEach(function (s) {{
      var d = DATA[s], x = (d.scores || {{}})[xk] || 0, y = (d.scores || {{}})[yk] || 0;
      (cells[x + ":" + y] = cells[x + ":" + y] || []).push(s);
    }});
    var xGood = METRIC[xk].good, yGood = METRIC[yk].good;
    var hot = xGood && yGood && xk !== yk;
    var h = "";
    for (var y = 5; y >= 1; y--) {{
      if (y === 5) h += '<div class="mx-yl" style="grid-row:1/6;grid-column:1"><span>' +
        esc(METRIC[yk].label) + " →</span></div>";
      for (var x = 1; x <= 5; x++) {{
        var isHot = hot &&
          (xGood === "hoch" ? x >= 4 : x <= 2) && (yGood === "hoch" ? y >= 4 : y <= 2);
        h += '<div class="mx-cell' + (isHot ?" hot" : "") + '" style="grid-row:' + (6 - y) +
          ";grid-column:" + (x + 1) + '"><b>' + x + "·" + y + "</b>" +
          (cells[x + ":" + y] || []).map(function (s) {{
            return '<button class="mx-chip" type="button" data-go2="' + esc(s) + '">' +
              esc(DATA[s].name) + "</button>";
          }}).join("") + "</div>";
      }}
    }}
    for (var x2 = 1; x2 <= 5; x2++)
      h += '<div class="mx-ax" style="grid-row:6;grid-column:' + (x2 + 1) + '">' + x2 + "</div>";
    h += '<div class="mx-ax mx-corner" style="grid-row:6;grid-column:1">' +
      esc(METRIC[xk].label) + " →</div>";
    plot.innerHTML = h;
    mxnote.textContent = hot
      ? "Getönt: der günstige Bereich — " + METRIC[xk].label + " " +
        (xGood === "hoch" ? "hoch" : "niedrig") + " und " + METRIC[yk].label +
        " " + (yGood === "hoch" ? "hoch" : "niedrig") + "."
      : "Für diese Kombination gibt es keine objektiv bessere Ecke — Dichte ist eine "
        + "Eigenschaft, kein Gütekriterium. Deshalb ohne Tönung.";
  }}
  mxS.addEventListener("change", drawPlot);
  myS.addEventListener("change", drawPlot);
  plot.addEventListener("click", function (e) {{
    var t = e.target.closest("[data-go2]");
    if (t) {{ lastFocus = t; open(order.indexOf(t.dataset.go2)); }}
  }});
  drawPlot();

  /* ---------- Tabelle ---------- */
  var tbody = document.getElementById("tbody");
  document.querySelectorAll("th.sortable").forEach(function (th) {{
    th.addEventListener("click", function () {{
      var col = +th.dataset.col;
      var asc = th.getAttribute("aria-sort") === "descending";
      document.querySelectorAll("th.sortable").forEach(function (o) {{
        o.setAttribute("aria-sort", "none");
      }});
      th.setAttribute("aria-sort", asc ? "ascending" : "descending");
      var rows = Array.prototype.slice.call(tbody.rows);
      rows.sort(function (a, b) {{
        var d = (+b.cells[col].dataset.v) - (+a.cells[col].dataset.v);
        return (asc ? -d : d) || (+a.cells[0].textContent - +b.cells[0].textContent);
      }});
      rows.forEach(function (r) {{ tbody.appendChild(r); }});
    }});
  }});
  tbody.addEventListener("click", function (e) {{
    var b = e.target.closest(".row-open");
    if (!b) return;
    lastFocus = b;
    open(order.indexOf(b.closest("tr").dataset.slug));
  }});

  /* ---------- Stil-Finder ----------
     Bewertet jeden Eintrag gegen die Antworten und begruendet jeden Treffer.
     Die Merkmale stammen aus dem finder-Block der Faktenblaetter, nicht aus Geschmack. */

  var FT = {{
    lede: "Neun Fragen. Die Empfehlung entsteht aus den Merkmalen der Faktenblätter, nicht aus Geschmack — jeder Treffer wird begründet. Du kannst die Eigenschaften des empfohlenen Stils anschließend als Anweisung für einen KI-Agenten kopieren.",
    go: "Empfehlung zeigen", answered: "% von 9 beantwortet", need: "Beantworte mindestens die erste Frage.",
    resTitle: "Deine Empfehlung", resLede: "Die % am besten passenden Einträge von %. Die Prozentzahl ist der Anteil der erreichten Punkte, keine Note.",
    open: "Eintrag öffnen", copy: "Als Prompt kopieren", copied: "Kopiert", show: "Text anzeigen",
    manual: "Automatisches Kopieren ist hier gesperrt. Der Text ist markiert — mit Strg+C bzw. Cmd+C kopieren.",
    caption: "Dieselbe Referenz-UI wie in allen % Einträgen.",
    note: "Die Empfehlung gewichtet neun Merkmale. Sie ersetzt kein eigenes Urteil — sieh dir die Demos an und lies das Faktenblatt. Ein Stil, der auf Platz vier steht, kann für dein Projekt der richtige sein.",
    pIntro: "Verwende die folgende Designsprache als visuelle Grundlage für dieses Projekt. Weiche nicht davon ab, ohne es zu begründen.",
    pIdea: "Kernidee", pParams: "Harte Parameter", pPalette: "Palette", pFonts: "Schriften",
    pRules: "Regeln, die einzuhalten sind", pAvoid: "Bekannte Fehlerquellen dieses Stils — vermeide sie",
    pA11y: "Barrierefreiheit", pTip: "Praxistipp", pSource: "Quelle",
    pRadius: "Radius", pContrast: "Kontrast", pDensity: "Dichte", pDepth: "Tiefe",
    pColor: "Farbe", pType: "Typografie", pMotion: "Motion", pTexture: "Textur",
    pFontNote: "über Google Fonts, jeweils mit generischem Fallback",
    why: {{
      useYes: "Ausdrücklich für % geeignet", useNo: "Nicht auf % ausgelegt",
      tone: "Trifft % der gewünschten Wirkung: %", toneNo: "Trifft keine der gewünschten Wirkungen",
      modeYes: "Modus passt: %", modeNo: "Ist %, du wolltest %",
      density: "Dichte % von 5", longevity: "Haltbarkeit % von 5",
      recognition: "Wiedererkennung % von 5", effort: "Aufwand % von 5",
      a11y: "Barrierefreiheit % von 5", platform: "Plattform-Eignung: %"
    }},
    modeName: {{ light: "hell", dark: "dunkel", both: "hell und dunkel", any: "egal" }},
    platName: {{ web: "Web", mobile: "Mobile", desktop: "Desktop" }},
    q: [
      {{ id: "use", h: "Was baust du?", s: "bestimmt die Grundeignung", o: [
        ["dev-tool","Entwicklerwerkzeug"],["data","Datenwerkzeug, Dashboard"],
        ["content","Text, Doku, Redaktion"],["consumer","App für Endkunden"],
        ["marketing","Landingpage, Portfolio"],["creative","Werkzeug zum Gestalten"],
        ["civic","Behörde, Bildung, Gesundheit"],["internal","internes Werkzeug"]] }},
      {{ id: "tone", multi: true, max: 3, h: "Wie soll es wirken?", s: "zwei bis drei auswählen", o: [
        ["precise","präzise"],["calm","ruhig"],["warm","warm"],["loud","laut"],
        ["playful","verspielt"],["formal","seriös"],["technical","technisch"],
        ["nostalgic","nostalgisch"],["expressive","eigenwillig"],["austere","streng"]] }},
      {{ id: "mode", h: "Hell oder dunkel?", s: "der Modus, in dem es hauptsächlich läuft", o: [
        ["light","hell"],["dark","dunkel"],["any","egal"]] }},
      {{ id: "density", h: "Wie viel Information pro Bildschirm?", s: "", o: [
        ["1","sehr luftig"],["3","mittel"],["5","sehr dicht"],["any","egal"]] }},
      {{ id: "longevity", h: "Wie lange soll es tragen?", s: "kurzlebige Stile kosten später einen Neuentwurf", o: [
        ["5","ein Jahrzehnt"],["3","einige Jahre"],["1","kurzlebig, Hauptsache jetzt"],["any","egal"]] }},
      {{ id: "recognition", h: "Auffallen oder vertraut wirken?", s: "", o: [
        ["5","unverwechselbar"],["3","eigen, aber ruhig"],["1","bewusst vertraut"],["any","egal"]] }},
      {{ id: "effort", h: "Wie viel Aufwand kannst du investieren?", s: "aufwendige Stile brauchen mehr Handarbeit je Plattform", o: [
        ["1","wenig"],["3","mittel"],["5","viel"]] }},
      {{ id: "a11y", h: "Wie wichtig ist Barrierefreiheit?", s: "", o: [
        ["5","kritisch"],["3","wichtig"],["1","nachrangig"]] }},
      {{ id: "platform", multi: true, h: "Für welche Plattformen?", s: "mehrere möglich", o: [
        ["web","Web"],["mobile","Mobile"],["desktop","Desktop"]] }}
    ]
  }};

  var ANS = {{}}, FI = document.getElementById("finder");
  var fiQuiz = document.getElementById("fi-quiz"), fiRes = document.getElementById("fi-results");
  var fiAgain = document.getElementById("fi-again");
  var fiFocus = null;
  var f1 = function (t, a) {{ return String(t).replace("%", a); }};
  var f2 = function (t, a, b) {{ return String(t).replace("%", a).replace("%", b); }};
  var labelOf = function (qid, val) {{
    var q = FT.q.filter(function (x) {{ return x.id === qid; }})[0];
    if (!q) return val;
    var o = q.o.filter(function (x) {{ return x[0] === val; }})[0];
    return o ? o[1] : val;
  }};

  /* ---------- Bewertung ---------- */
  function rate(slug) {{
    var d = DATA[slug], f = d.finder || {{}}, sc = d.scores || {{}};
    var pts = 0, max = 0, why = [];
    function add(w, got, text, ok) {{
      max += w; pts += w * got;
      if (text) why.push({{ t: text, ok: ok !== false, w: w * got }});
    }}
    var fits = f.fits || [], tone = f.tone || [], plat = f.platform || {{}};

    if (ANS.use) {{
      var hit = fits.indexOf(ANS.use) !== -1;
      add(25, hit ? 1 : 0, f1(hit ? FT.why.useYes : FT.why.useNo, labelOf("use", ANS.use)), hit);
    }}
    if (ANS.tone && ANS.tone.length) {{
      var m = ANS.tone.filter(function (t) {{ return tone.indexOf(t) !== -1; }});
      add(20, m.length / ANS.tone.length,
        m.length ? f2(FT.why.tone, m.length + "/" + ANS.tone.length,
          m.map(function (t) {{ return labelOf("tone", t); }}).join(", ")) : FT.why.toneNo,
        m.length > 0);
    }}
    if (ANS.mode) {{
      var g = ANS.mode === "any" ? 0.7 : (f.mode === ANS.mode || f.mode === "both" ? 1 : 0);
      add(12, g, ANS.mode === "any" ? null
        : (g ? f1(FT.why.modeYes, FT.modeName[f.mode] || f.mode)
             : f2(FT.why.modeNo, FT.modeName[f.mode] || f.mode, FT.modeName[ANS.mode])), g > 0);
    }}
    [["density", 12], ["longevity", 14], ["recognition", 12]].forEach(function (pair) {{
      var k = pair[0], w = pair[1], v = ANS[k];
      if (!v) return;
      if (v === "any") {{ add(w, 0.6, null); return; }}
      var have = sc[k] || 0, g = 1 - Math.abs(have - (+v)) / 4;
      add(w, Math.max(0, g), f1(FT.why[k], have), g >= 0.5);
    }});
    if (ANS.effort) {{
      var e = sc.effort || 3, cap = +ANS.effort;
      var g2 = e <= cap ? 1 : Math.max(0, 1 - (e - cap) / 2);
      add(10, g2, f1(FT.why.effort, e), g2 >= 0.5);
    }}
    if (ANS.a11y) {{
      var imp = (+ANS.a11y - 1) / 4, q = ((f.a11y || 3) - 1) / 4;
      add(14, 1 - imp * (1 - q), imp > 0 ? f1(FT.why.a11y, f.a11y || 3) : null, q >= 0.5);
    }}
    if (ANS.platform && ANS.platform.length) {{
      var vals = ANS.platform.map(function (p) {{ return plat[p] || 3; }});
      var avg = vals.reduce(function (a, b) {{ return a + b; }}, 0) / vals.length;
      add(12, (avg - 1) / 4, f1(FT.why.platform, ANS.platform.map(function (p, i) {{
        return FT.platName[p] + " " + vals[i]; }}).join(", ")), avg >= 3);
    }}
    why.sort(function (a, b) {{ return (a.ok === b.ok) ? b.w - a.w : (a.ok ? -1 : 1); }});
    return {{ slug: slug, pct: max ? Math.round(100 * pts / max) : 0, why: why }};
  }}

  /* ---------- Prompt ---------- */
  function buildPrompt(slug) {{
    var d = DATA[slug], p = d.params || {{}}, L = [];
    L.push(FT.pIntro, "", "# " + d.name, "", "## " + FT.pIdea, d.idea, "", "## " + FT.pParams);
    [[FT.pRadius, p.radius], [FT.pContrast, p.contrast], [FT.pDensity, p.density],
     [FT.pDepth, p.depth], [FT.pColor, p.color], [FT.pType, p.type],
     [FT.pMotion, p.motion], [FT.pTexture, p.texture]].forEach(function (r) {{
      if (r[1]) L.push("- **" + r[0] + ":** " + r[1]);
    }});
    if ((d.palette || []).length) L.push("", "## " + FT.pPalette, d.palette.join("  "));
    if ((d.googleFonts || []).length)
      L.push("", "## " + FT.pFonts, d.googleFonts.join(", ") + " (" + FT.pFontNote + ")");
    if ((d.markers || []).length) {{
      L.push("", "## " + FT.pRules);
      d.markers.forEach(function (m) {{ L.push("- " + m); }});
    }}
    if ((d.risks || []).length) {{
      L.push("", "## " + FT.pAvoid);
      d.risks.forEach(function (r) {{ L.push("- " + r); }});
    }}
    if (d.a11y) L.push("", "## " + FT.pA11y, d.a11y);
    if (d.tip) L.push("", "## " + FT.pTip, d.tip);
    L.push("", "---", FT.pSource + ": " + SITE + "/" + LANG + "/ — " + d.name);
    return L.join("\n");
  }}

  /* ---------- Fragebogen ---------- */
  function renderQuiz() {{
    fiQuiz.innerHTML = FT.q.map(function (q) {{
      return '<div class="fi-q"><div><h3>' + esc(q.h) + "</h3>"
        + (q.s ? "<p>" + esc(q.s) + "</p>" : "") + '</div><div class="fi-opts">'
        + q.o.map(function (o) {{
            return '<button class="fi-opt" type="button" data-q="' + q.id + '" data-v="'
              + esc(o[0]) + '" aria-pressed="false">' + esc(o[1]) + "</button>";
          }}).join("") + "</div></div>";
    }}).join("")
      + '<div class="fi-go"><button type="button" id="fi-go" disabled></button>'
      + '<span id="fi-count"></span></div>';
    document.getElementById("fi-go").textContent = FT.go;
    updateCount();
  }}

  function updateCount() {{
    var n = FT.q.filter(function (q) {{
      var v = ANS[q.id]; return q.multi ? (v && v.length) : !!v;
    }}).length;
    document.getElementById("fi-count").textContent =
      n ? f1(FT.answered, n) : FT.need;
    document.getElementById("fi-go").disabled = !ANS.use;
  }}

  fiQuiz.addEventListener("click", function (e) {{
    var b = e.target.closest(".fi-opt");
    if (!b) return;
    var qid = b.dataset.q, v = b.dataset.v;
    var q = FT.q.filter(function (x) {{ return x.id === qid; }})[0];
    if (q.multi) {{
      ANS[qid] = ANS[qid] || [];
      var i = ANS[qid].indexOf(v);
      if (i >= 0) ANS[qid].splice(i, 1);
      else {{ if (q.max && ANS[qid].length >= q.max) ANS[qid].shift(); ANS[qid].push(v); }}
      fiQuiz.querySelectorAll('[data-q="' + qid + '"]').forEach(function (o) {{
        o.setAttribute("aria-pressed", String(ANS[qid].indexOf(o.dataset.v) !== -1));
      }});
    }} else {{
      ANS[qid] = ANS[qid] === v ? null : v;
      fiQuiz.querySelectorAll('[data-q="' + qid + '"]').forEach(function (o) {{
        o.setAttribute("aria-pressed", String(ANS[qid] === o.dataset.v));
      }});
    }}
    updateCount();
  }});

  /* ---------- Ergebnis ---------- */
  function showResults() {{
    var ranked = order.map(rate).sort(function (a, b) {{ return b.pct - a.pct; }}).slice(0, 5);
    fiRes.innerHTML = "<h3 style=\"font-size:21px;margin-bottom:6px\">" + esc(FT.resTitle)
      + '</h3><p class="fi-lede">' + esc(f2(FT.resLede, ranked.length, order.length))
      + '</p><div class="fi-res">'
      + ranked.map(function (r, i) {{
          var d = DATA[r.slug];
          return '<article class="fi-card"><div class="fi-card-head">'
            + '<span class="fi-rank">' + (i + 1) + "</span><h3>" + esc(d.name) + "</h3>"
            + '<span class="fi-score">' + r.pct + " %</span></div>"
            + '<div class="fi-card-body"><div><div class="fi-frame" data-demo="' + esc(r.slug)
            + '"><div class="fi-host"></div></div><p class="cap">'
            + esc(f1(FT.caption, order.length)) + "</p></div><div>"
            + '<p class="fi-sig">' + esc((d.finder && d.finder.signature) || d.idea) + "</p>"
            + '<ul class="fi-why">' + r.why.slice(0, 6).map(function (w) {{
                return '<li class="' + (w.ok ? "" : "no") + '">' + esc(w.t) + "</li>";
              }}).join("") + "</ul>"
            + '<div class="fi-acts"><button type="button" class="prim" data-go3="' + esc(r.slug)
            + '">' + esc(FT.open) + '</button><button type="button" data-copy="' + esc(r.slug)
            + '">' + esc(FT.copy) + '</button><button type="button" data-show="' + esc(r.slug)
            + '">' + esc(FT.show) + "</button></div></div></div></article>";
        }}).join("")
      + '</div><p class="fi-note">' + esc(FT.note) + "</p>";

    /* Erst sichtbar machen, dann messen - in einem hidden-Element ist clientWidth 0
       und die Rahmen fielen auf Randstaerke zusammen. */
    fiQuiz.hidden = true; fiRes.hidden = false; fiAgain.hidden = false;
    fiRes.querySelectorAll("[data-demo]").forEach(function (fr) {{
      var src = document.querySelector('.k-plate[data-slug="' + fr.dataset.demo + '"] .demo-host');
      if (!src || !src.firstElementChild) return;
      var host = fr.querySelector(".fi-host");
      host.textContent = "";
      host.appendChild(src.firstElementChild.cloneNode(true));
    }});
    fitFinder();
    [60, 300].forEach(function (d) {{ setTimeout(fitFinder, d); }});
    FI.scrollTop = 0;
  }}

  fiRes.addEventListener("click", function (e) {{
    var go = e.target.closest("[data-go3]");
    if (go) {{ closeFinder(); open(order.indexOf(go.dataset.go3)); return; }}
    var sh = e.target.closest("[data-show]");
    if (sh) {{
      var wrap = sh.closest("div").parentElement;
      var box = wrap.querySelector(".fi-pre");
      if (box) {{
        box.remove();
        var h = wrap.querySelector(".fi-hint"); if (h) h.remove();
        return;
      }}
      showPrompt(sh, buildPrompt(sh.dataset.show), null);
      return;
    }}
    var cp = e.target.closest("[data-copy]");
    if (!cp) return;
    var txt = buildPrompt(cp.dataset.copy);
    var done = function () {{
      var old = cp.dataset.label || cp.textContent;
      cp.dataset.label = old;
      cp.textContent = FT.copied; cp.classList.add("ok");
      setTimeout(function () {{ cp.textContent = old; cp.classList.remove("ok"); }}, 1800);
    }};
    /* Schlaegt das Kopieren fehl - im Artifact-Sandkasten und ohne Nutzergeste ist die
       Zwischenablage gesperrt -, darf nicht einfach nichts passieren. Dann wird der Text
       eingeblendet und markiert, sodass Strg/Cmd+C greift. */
    var manual = function () {{
      var box = showPrompt(cp, txt, FT.manual);
      if (box) {{
        var r = document.createRange(); r.selectNodeContents(box);
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
        box.scrollIntoView({{ block: "nearest" }});
      }}
    }};
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(txt).then(done, function () {{ legacy(txt, done, manual); }});
    }} else legacy(txt, done, manual);
  }});

  function legacy(txt, done, manual) {{
    var ta = document.createElement("textarea");
    ta.value = txt;
    ta.style.cssText = "position:fixed;top:-1000px;left:0;opacity:0";
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try {{ ok = document.execCommand("copy"); }} catch (e) {{}}
    ta.remove();
    if (ok) done(); else manual();
  }}

  function showPrompt(btn, txt, hint) {{
    var wrap = btn.closest("div").parentElement;
    var old = wrap.querySelector(".fi-pre");
    if (old) old.remove();
    var pre = document.createElement("pre");
    pre.className = "fi-pre";
    pre.textContent = txt;
    if (hint) {{
      var p = document.createElement("p");
      p.className = "fi-hint";
      p.textContent = hint;
      pre.setAttribute("data-hint", "1");
      wrap.appendChild(p);
    }}
    wrap.appendChild(pre);
    return pre;
  }}

  function fitFinder() {{
    fiRes.querySelectorAll(".fi-frame").forEach(function (fr) {{
      var host = fr.querySelector(".fi-host");
      if (!host || !fr.clientWidth) return;
      var k = fr.clientWidth / W;
      host.style.transform = "scale(" + k + ")";
      fr.style.height = Math.round(host.scrollHeight * k) + "px";
    }});
  }}
  window.addEventListener("resize", function () {{ if (!FI.hidden) setTimeout(fitFinder, 60); }});

  /* ---------- Öffnen und Schließen ---------- */
  function openFinder() {{
    if (!fiQuiz.children.length) renderQuiz();
    FI.hidden = false; document.body.style.overflow = "hidden"; FI.scrollTop = 0;
    document.getElementById("fi-close").focus();
  }}
  function closeFinder() {{
    FI.hidden = true; document.body.style.overflow = "";
    if (fiFocus) {{ try {{ fiFocus.focus(); }} catch (e) {{}} }}
  }}
  document.getElementById("fi-open").addEventListener("click", function (e) {{
    fiFocus = e.currentTarget; openFinder();
  }});
  document.getElementById("fi-close").addEventListener("click", closeFinder);
  fiAgain.addEventListener("click", function () {{
    fiRes.hidden = true; fiQuiz.hidden = false; fiAgain.hidden = true; FI.scrollTop = 0;
  }});
  fiQuiz.addEventListener("click", function (e) {{
    if (e.target.id === "fi-go") showResults();
  }});
  document.addEventListener("keydown", function (e) {{
    if (!FI.hidden && e.key === "Escape") {{ e.preventDefault(); closeFinder(); }}
  }});
  document.getElementById("fi-lede").textContent = FT.lede;

}})();
</script>
'''

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'"
           "%3E%3Crect width='32' height='32' rx='5' fill='%231E4A45'/%3E"
           "%3Crect x='7' y='7' width='18' height='4.6' fill='%23E9EBE6'/%3E"
           "%3Crect x='7' y='13.7' width='18' height='4.6' rx='2.3' fill='%23E9EBE6'/%3E"
           "%3Crect x='7' y='20.4' width='18' height='4.6' rx='1' fill='%23E9EBE6'/%3E%3C/svg%3E")

TOPBAR = {
 "de": '<div class="topbar"><div class="wrap topbar-in">\n'
       '  <a class="tb-brand" href="../">Designsprache</a>\n'
       '  <nav class="tb-lang" aria-label="Sprache / Language">\n'
       '    <a href="../de/" hreflang="de" lang="de" aria-current="page">Deutsch</a>\n'
       '    <a href="../en/" hreflang="en" lang="en">English</a>\n'
       '  </nav>\n'
       '  <a class="tb-repo" href="{repo}" rel="noopener">Quelltext auf GitHub</a>\n'
       '</div></div>',
 "en": '<div class="topbar"><div class="wrap topbar-in">\n'
       '  <a class="tb-brand" href="../">Designsprache</a>\n'
       '  <nav class="tb-lang" aria-label="Sprache / Language">\n'
       '    <a href="../de/" hreflang="de" lang="de">Deutsch</a>\n'
       '    <a href="../en/" hreflang="en" lang="en" aria-current="page">English</a>\n'
       '  </nav>\n'
       '  <a class="tb-repo" href="{repo}" rel="noopener">Source on GitHub</a>\n'
       '</div></div>',
}

_HEAD_TPL = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Sebastian Grundhoefer">
<link rel="canonical" href="{site}/{lang}/">
<link rel="alternate" hreflang="de" href="{site}/de/">
<link rel="alternate" hreflang="en" href="{site}/en/">
<link rel="alternate" hreflang="x-default" href="{site}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{site}/{lang}/">
<meta property="og:locale" content="{locale}">
<meta property="og:image" content="{site}/og.png">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="640">
<meta property="og:image:alt" content="{imgalt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{site}/og.png">
<link rel="icon" href="{icon}">
<style>
html {{ color-scheme: light dark; }}
body {{ margin: 0; font: 14px system-ui, sans-serif; }}
img {{ max-width: 100%; }}
[hidden] {{ display: none !important; }}
</style>
</head>
<body>
"""

HEAD = {
 "de": _HEAD_TPL.format(
   lang="de", locale="de_DE", site=SITE_URL, icon=FAVICON,
   imgalt="Dieselbe Projektliste in vier Stilen nebeneinander: Swiss, Bauhaus, Neo-Brutalismus, Dev-Noir.",
   title=f"Stil-Katalog — {N_ENTRIES} Wege, dieselbe Oberfläche zu bauen",
   desc=(f"{N_ENTRIES} UI-Stilrichtungen, jede als gerendertes Beispiel derselben Referenzoberfläche. "
         "Mit Faktenblatt, Kennzahlen und Entscheidungsraster. Von Swiss und Bauhaus über "
         "Skeuomorphismus und Glassmorphism bis Dev-Noir und Neo-Brutalismus.")),
 "en": _HEAD_TPL.format(
   lang="en", locale="en_US", site=SITE_URL, icon=FAVICON,
   imgalt="The same project list in four styles side by side: Swiss, Bauhaus, neo-brutalism, dev-noir.",
   title=f"Style Catalog — {N_ENTRIES} ways to build the same interface",
   desc=(f"{N_ENTRIES} UI style directions, each rendered as the very same reference interface. "
         "With fact sheets, scores and a decision grid. From Swiss and Bauhaus through "
         "skeuomorphism and glassmorphism to dev-noir and neo-brutalism.")),
}


def check_scoping(sheets, slugs, suffix):
    """Bricht ab, wenn ein Selektor nicht auf .style-SLUG beginnt.

    Alle Stylesheets teilen sich eine Seite. Ein einziger ungescopter Selektor -
    :root, body, ein nackter Element-Selektor - wuerde alle anderen Demos zerstoeren.
    Diese Pruefung laeuft bei jedem Build, damit ein Beitrag das nicht einschleppen kann.
    """
    problems = []
    for css, slug in zip(sheets, slugs):
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        stack, buf = [], ""
        for ch in css:
            if ch == "{":
                sel, buf = buf.strip(), ""
                if sel.startswith("@"):
                    name = sel.split()[0].lower()
                    if name == "@keyframes":
                        parts = sel.split(None, 1)
                        kf = parts[1].strip() if len(parts) > 1 else ""
                        if not kf.startswith(slug + "-"):
                            problems.append(f"{slug}: @keyframes ohne Praefix '{slug}-': {kf}")
                        stack.append("opaque")
                    elif name in ("@media", "@supports", "@layer", "@container"):
                        stack.append("group")
                    else:
                        stack.append("opaque")
                else:
                    if not (stack and stack[-1] == "opaque"):
                        for one in (x.strip() for x in sel.split(",")):
                            if one and not one.startswith(".style-" + slug):
                                problems.append(f"{slug}: ungescopter Selektor: {one[:80]}")
                    stack.append("rule")
            elif ch == "}":
                buf = ""
                if stack:
                    stack.pop()
            else:
                buf += ch
    if problems:
        for x in problems[:20]:
            print("  FEHLER  " + x, file=sys.stderr)
        sys.exit(f"{len(problems)} Scoping-Verstoesse in styles/*{suffix}.html")


def page_en():
    """Wendet die L10N-Tabelle auf das Seitengeruest an.

    Jedes Paar muss greifen. Schlaegt eines fehl, wurde die deutsche Vorlage geaendert,
    ohne die englische nachzuziehen - dann bricht der Build ab, statt eine halb deutsche
    englische Seite auszuliefern.
    """
    out, missed = PAGE, []
    for de, en in L10N:
        if de not in out:
            missed.append(de[:70])
        out = out.replace(de, en)
    if missed:
        for m in missed:
            print("  FEHLER  L10N-Paar greift nicht: " + m, file=sys.stderr)
        sys.exit(f"{len(missed)} von {len(L10N)} L10N-Paaren ohne Treffer")
    return out


def build_landing():
    """Zweisprachige Eingangsseite aus landing.html, mit eingesetzten URLs."""
    src = (ROOT / "landing.html").read_text(encoding="utf-8")
    out = DOCS / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        (src.replace("__SITE__", SITE_URL).replace("__REPO__", REPO_URL)
            .replace("__ICON__", FAVICON)
            .replace("__N__", str(N_ENTRIES)).replace("__NFAM__", str(N_FAMILIES))),
        encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    og = ROOT / "og.png"
    if og.exists():
        shutil.copyfile(og, DOCS / "og.png")
    else:
        print("  WARNUNG: og.png fehlt - Link-Vorschauen bleiben ohne Bild", file=sys.stderr)
    print(f"  {out.relative_to(ROOT)}  ({out.stat().st_size/1024:.0f} KB)")



# ---------------------------------------------------------------------------
# Social-Preview-Bild. Gebaut aus den echten Demos, nicht aus einer Attrappe:
# vier Fassungen derselben Oberflaeche nebeneinander erklaeren das Projekt
# ohne einen Satz Text.
#
#   python3 build.py --og      schreibt og.html (1280x640)
#   dann einmalig rendern und og.png einchecken:
#     "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
#       --headless --disable-gpu --hide-scrollbars --virtual-time-budget=8000 \
#       --screenshot=og.png --window-size=1280,640 file://$PWD/og.html
#
# og.png liegt im Repo, weil der CI-Runner keinen Browser hat; build.py
# kopiert es bei jedem Lauf nach docs/.
# ---------------------------------------------------------------------------

OG_STYLES = ["swiss", "bauhaus", "neo-brutalism", "dev-noir"]
OG_W, OG_H, OG_PAD, OG_GAP = 1280, 640, 40, 20
OG_TILE, OG_FRAME = 285, 196      # Kachelbreite und feste Rahmenhoehe des Demo-Streifens
OG_REF = 780                      # Bezugsbreite der Demos
OG_CARD = "dev-noir"              # aus diesem Faktenblatt stammt der gezeigte Prompt-Auszug


def build_og():
    sheets, demos, data = [], [], []
    for slug in OG_STYLES:
        raw = (SRC / f"{slug}.html").read_text(encoding="utf-8")
        m = re.search(r"<style>(.*?)</style>", raw, re.S)
        sheets.append(m.group(1).strip())
        demos.append(raw[m.end():].strip())
        data.append(json.loads((SRC / f"{slug}.json").read_text(encoding="utf-8")))

    fonts = set()
    for d in data:
        fonts.update(d.get("googleFonts") or [])
    specs = [x for x in FONT_SPECS
             if x.split(":")[0].replace("+", " ") in fonts] + CHROME_FONTS
    links = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             + "&".join("family=" + x for x in dict.fromkeys(specs)) + '&display=block">')

    # Der Prompt-Auszug stammt aus einem echten Faktenblatt, nicht aus einer Attrappe.
    card = json.loads((SRC / f"{OG_CARD}.json").read_text(encoding="utf-8"))
    cp = card["params"]
    zeilen = [("## " + card["name"], "h"), ("", "")]
    zeilen += [("- **" + k + ":** " + cp[v][:46] + ("…" if len(cp[v]) > 46 else ""), "")
               for k, v in (("Radius", "radius"), ("Kontrast", "contrast"),
                            ("Tiefe", "depth"), ("Farbe", "color"))]
    zeilen += [("", ""), ("## Regeln", "h")]
    zeilen += [("- " + m[:52] + ("…" if len(m) > 52 else ""), "")
               for m in card["markers"][:2]]
    pre = "".join('<div class="%s">%s</div>' % (c or "l", html.escape(t) or "&nbsp;")
                  for t, c in zeilen)

    k = OG_TILE / OG_REF
    tiles = "".join(
        f'<div class="tile"><div class="frame"><div class="host">{demo}</div></div>'
        f'<div class="lbl"><span class="n">{i + 1:02d}</span>{esc(d["name"].split(" / ")[0])}</div></div>'
        for i, (demo, d) in enumerate(zip(demos, data)))

    css = "\n".join(f"<style>\n{x}\n</style>" for x in sheets)

    (ROOT / "og.html").write_text(f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
{links}
<style>
  html, body {{ margin:0; padding:0; }}
  body {{ width:{OG_W}px; height:{OG_H}px; overflow:hidden;
    background:#141614; color:#E7EAE4; font-family:"Newsreader",Georgia,serif;
    display:flex; flex-direction:column; padding:{OG_PAD}px; box-sizing:border-box; }}
  .top {{ display:flex; gap:44px; align-items:flex-start; }}
  .left {{ flex:1 1 auto; min-width:0; }}
  .eyebrow {{ font-family:"IBM Plex Mono",monospace; font-size:13px; letter-spacing:.16em;
    text-transform:uppercase; color:#C7A55F; }}
  h1 {{ font-family:"IBM Plex Sans Condensed",Arial,sans-serif; font-weight:700;
    font-size:66px; line-height:.94; letter-spacing:-.025em; margin:10px 0 0; }}
  h1 em {{ font-family:"Newsreader",Georgia,serif; font-style:italic; font-weight:400;
    color:#99A099; letter-spacing:-.01em; font-size:.52em; display:block; margin-top:3px; }}
  .purpose {{ margin:14px 0 0; font-size:18px; line-height:1.4; color:#E7EAE4; max-width:34ch; }}
  .purpose span {{ display:block; color:#99A099; font-size:15px; margin-top:3px; }}
  .url {{ font-family:"IBM Plex Mono",monospace; font-size:14px; color:#77BFB1; margin-top:14px; }}
  .card {{ flex:0 0 452px; border:1px solid #333833; background:#1B1E1B; }}
  .card-h {{ display:flex; align-items:center; gap:8px; padding:9px 12px;
    border-bottom:1px solid #333833; font-family:"IBM Plex Mono",monospace; font-size:11px;
    letter-spacing:.1em; text-transform:uppercase; color:#6F766F; }}
  .card-h b {{ color:#C7A55F; font-weight:500; }}
  .card-b {{ padding:11px 13px; font-family:"IBM Plex Mono",monospace; font-size:11px;
    line-height:1.62; color:#99A099; }}
  .card-b .h {{ color:#E7EAE4; }}
  .card-f {{ padding:10px 13px 12px; border-top:1px solid #333833; }}
  .btn {{ display:inline-block; font-family:"IBM Plex Mono",monospace; font-size:12px;
    padding:6px 12px; background:#77BFB1; color:#101413; border-radius:2px; }}
  .btn + span {{ font-family:"IBM Plex Mono",monospace; font-size:11px; color:#6F766F;
    margin-left:10px; }}
  .row {{ display:flex; gap:{OG_GAP}px; margin-top:auto; align-items:flex-start; }}
  .tile {{ width:{OG_TILE}px; }}
  .frame {{ width:{OG_TILE}px; height:{OG_FRAME}px; overflow:hidden; border:1px solid #333833; }}
  .host {{ width:{OG_REF}px; transform:scale({k}); transform-origin:0 0; }}
  .lbl {{ padding-top:9px; font-family:"IBM Plex Sans Condensed",Arial,sans-serif;
    font-weight:600; font-size:16px; color:#E7EAE4; display:flex; gap:8px; align-items:baseline; }}
  .lbl .n {{ font-family:"IBM Plex Mono",monospace; font-size:11px; font-weight:600;
    color:#C7A55F; }}
</style>
{css}
</head><body>
  <div class="top">
    <div class="left">
      <span class="eyebrow">Referenzkatalog &middot; Reference catalog</span>
      <h1>Stil&#8209;Katalog<em>{N_ENTRIES} ways to build the same interface</em></h1>
      <p class="purpose">Dieselbe Oberfläche, {N_ENTRIES}&#8209;mal gestaltet — vergleichen,
        auswählen, als Anweisung für einen KI&#8209;Agenten kopieren.
        <span>The same interface, designed {N_ENTRIES} ways — compare, choose, copy it as an
        instruction for an AI agent.</span></p>
      <p class="url">{SITE_URL.replace("https://", "")}</p>
    </div>
    <div class="card">
      <div class="card-h">Als Prompt kopieren <b>&middot;</b> Copy as prompt</div>
      <div class="card-b">{pre}</div>
      <div class="card-f"><span class="btn">Kopiert &middot; Copied</span><span>4.000 Zeichen</span></div>
    </div>
  </div>
  <div class="row">{tiles}</div>
</body></html>
""", encoding="utf-8")
    print(f"  og.html  ({OG_W}x{OG_H}, {len(OG_STYLES)} Demos + Prompt-Karte)")

if __name__ == "__main__":
    print("Stil-Katalog")
    build_landing()
    for _lang in ("de", "en"):
        build(_lang, "site")
    if "--artifact" in sys.argv:
        build("de", "artifact")
    if "--og" in sys.argv:
        build_og()
    print("fertig.")

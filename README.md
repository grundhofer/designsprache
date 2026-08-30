# Stil-Katalog

**27 UI-Stilrichtungen — jede als gerendertes Beispiel derselben Oberfläche.**
27 UI style directions — each rendered as the very same interface.

→ **[grundhofer.github.io/designsprache](https://grundhofer.github.io/designsprache)**
&nbsp;·&nbsp; [Deutsch](https://grundhofer.github.io/designsprache/de/)
&nbsp;·&nbsp; [English](https://grundhofer.github.io/designsprache/en/)

---

## Deutsch

Über UI-Stile wird meist in Adjektiven geredet. „Clean", „modern", „verspielt" — Wörter, unter
denen sich jeder etwas anderes vorstellt. Dieser Katalog ersetzt sie durch Anschauung.

Jeder der 27 Einträge zeigt **exakt dieselbe Oberfläche**: eine Projektliste mit Kopfzeile, drei
Einträgen, einem Suchfeld und zwei Schaltflächen — dieselben dreizehn Textbausteine, überall.
Das Einzige, was sich ändert, ist die Gestaltung. Dadurch wird vergleichbar, was ein Stil
tatsächlich entscheidet, und was nur Geschmack ist.

Zu jedem Stil gehört ein Faktenblatt: Herkunft und Entstehungskontext, sechs bis neun harte
visuelle Merkmale mit konkreten Werten, echte Vertreter mit belegten Farbwerten und Radien,
Stärken, Risiken, Barrierefreiheits-Konsequenzen, Alterungsverhalten, Plattform-Eignung und
ein Praxistipp.

### Die sieben Parameter

Stilnamen sind austauschbar. Was einen Stil ausmacht, sind sieben Größen — und jede davon ist
eine Entscheidung, die man als Design-Token schreiben kann:

| Parameter | Spanne | Wirkung |
|---|---|---|
| **Radius** | 0 px → vollrund | Der am stärksten unterschätzte Markenträger |
| **Kontrast** | 1,5:1 → 18:1 | Ob eine Oberfläche ruhig oder laut wirkt |
| **Tiefe** | keine → Linie → Schatten → Unschärfe → z-Achse | Wie Hierarchie entsteht |
| **Dichte** | Faktor 5 zwischen den Extremen | Information pro Bildschirm |
| **Farbe** | monochrom+Akzent → Flächenfarbe → Verlauf | Wie viel Bedeutung Farbe trägt |
| **Typografie** | Grotesk / Serif / Mono / Display | Zweitstärkster Wiedererkennungsträger |
| **Motion** | 0 ms → 120 ms linear → 400 ms Spring | Die Persönlichkeit — meist vergessen |

Wer diese sieben kennt, kann Stile **mischen statt kopieren**. Kein starkes Produkt trägt einen
Reinstil: Linear ist Swiss-Raster plus Dark-Mode plus Terminal-Dichte, Notion ist Warm Editorial
plus Flat, Stripe ist Swiss plus Aurora.

### Die acht Familien

**Modernistische Schulen** — Swiss · Bauhaus · De Stijl
**Postmoderne & Rebellion** — Memphis · Swiss Punk · Web-Brutalismus
**Digitale Epochen** — Skeuomorphismus · Flat · Material 3 Expressive
**Weiche Materialität** — Neumorphismus · Glassmorphism · Claymorphism
**Produkt-Ästhetik heute** — Dev-Noir · Warm Editorial · Neo-Brutalismus · Terminal-Mono · Data-Dense · Spatial
**Nostalgie & Subkultur** — Y2K/Frutiger Aero · Vaporwave · Retro-Futurismus
**Ausdruck & Natur** — Organic/Blob · Maximalismus · Aurora-Mesh
**Weitere Pole** — Editorial-Print · Pixel/8-Bit · Playful-Chunky

---

## English

Talk about UI styles usually happens in adjectives. "Clean", "modern", "playful" — words that
mean something different to everyone. This catalog replaces them with evidence.

Each of the 27 entries shows **exactly the same interface**: a project list with a header, three
rows, a search field and two buttons — the same thirteen pieces of text throughout. The only
thing that changes is the design. That makes it comparable what a style actually decides, and
what is merely taste.

Every style comes with a fact sheet: origin and context, six to nine hard visual markers with
concrete values, real-world examples with sourced color values and radii, strengths, risks,
accessibility consequences, how it ages, platform fit, and one practical tip.

The seven parameters that constitute any style — radius, contrast, depth, density, color,
typography, motion — are each a decision you can write down as a design token. Know them, and
you can mix styles instead of copying them.

---

## Aufbau / How it works

Kein Framework, kein Build-Tool-Zoo. Ein Python-Skript ohne Abhängigkeiten baut aus den
Quelldateien drei statische Seiten.

No framework, no build-tool zoo. One dependency-free Python script turns the sources into three
static pages.

```
styles/
  swiss.html        Demo: ein <style>-Element + ein <div class="style-swiss">
  swiss.json        Faktenblatt / fact sheet
  swiss.en.html     englische Fassung, CSS zeichengleich / English, byte-identical CSS
  swiss.en.json
  … 27 Stile × 4 Dateien
landing.html        zweisprachige Eingangsseite / bilingual entry page
build.py            Generator
docs/               erzeugt / generated — nicht eingecheckt / not committed
```

```sh
python3 build.py              # docs/index.html, docs/de/, docs/en/
python3 build.py --artifact   # zusätzlich ein Fragment ohne <head>
```

### Die Scoping-Regel

27 Stylesheets teilen sich eine Seite. Damit sie sich nicht gegenseitig zerstören, gilt für
jede Demo: **jeder CSS-Selektor beginnt mit `.style-<slug>`**, `@keyframes`-Namen sind mit
`<slug>-` präfigiert, und es gibt kein `:root`, kein `body`, keinen nackten Element-Selektor.
`build.py` prüft das bei jedem Lauf und bricht bei Verstoß ab.

27 stylesheets share one page. So they cannot destroy each other, every demo obeys one rule:
**every CSS selector starts with `.style-<slug>`**, `@keyframes` names are prefixed with
`<slug>-`, and there is no `:root`, no `body`, no bare element selector. `build.py` verifies
this on every run and fails the build on violation.

Die Demos sind handgebautes HTML und CSS — keine Bilder, keine Skripte, keine Bibliotheken.
Grafik entsteht aus Gradients, `box-shadow`, Borders, Inline-SVG und CSS-Mustern. Schriften
kommen von Google Fonts.

---

## Mitmachen / Contributing

Ein 28. Stil ist willkommen — siehe **[CONTRIBUTING.md](CONTRIBUTING.md)**.
Korrekturen an Jahreszahlen, Urhebern, Farbwerten oder Einschätzungen ebenso: die
Faktenblätter sind recherchiert, aber nicht unfehlbar.

A 28th style is welcome — see **[CONTRIBUTING.md](CONTRIBUTING.md)**. Corrections to dates,
attributions, color values or judgements are equally welcome: the fact sheets are researched
but not infallible.

---

## Lizenz / License

- **Code** (`build.py`, `landing.html`, die Demos in `styles/*.html`) — [MIT](LICENSE).
  Nimm eine Demo, bau sie um, verwende sie kommerziell.
- **Texte** (die Faktenblätter in `styles/*.json`, die Prosa der Seite) —
  [CC BY 4.0](LICENSE-CONTENT.md). Weiterverwendung mit Namensnennung.

Die vier Kennzahlen je Stil (Haltbarkeit, Wiedererkennung, Aufwand, Dichte) sind fachliche
Einschätzungen, keine Messwerte. Genannte Produkt- und Markennamen gehören ihren jeweiligen
Inhabern; die Demos sind eigenständige Nachbauten im jeweiligen Stil, keine Kopien.

The four scores per style are professional judgements, not measurements. Product and brand
names belong to their respective owners; the demos are original recreations in the respective
style, not copies.

© Sebastian Grundhöfer

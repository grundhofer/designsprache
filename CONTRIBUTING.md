# Mitmachen / Contributing

*Deutsch unten, English below.*

---

## Deutsch

Zwei Arten von Beiträgen sind willkommen: **Korrekturen** an bestehenden Einträgen und ein
**neuer Stil**.

### Korrekturen

Die Faktenblätter sind recherchiert, aber nicht unfehlbar. Falsche Jahreszahlen, falsch
zugeschriebene Urheberschaft, nicht mehr stimmende Farbwerte, überholte Aussagen über aktuelle
Produkte — alles gern per Issue oder Pull Request. Bei strittigen Fakten hilft eine Quelle.

Die vier Kennzahlen (Haltbarkeit, Wiedererkennung, Aufwand, Dichte) sind Einschätzungen, keine
Messwerte. Über sie lässt sich streiten — dann bitte im Issue mit Begründung, nicht per
stillschweigender Änderung.

### Einen Stil ergänzen

Ein Stil besteht aus vier Dateien in `styles/`:

```
<slug>.html      Demo, deutsch
<slug>.json      Faktenblatt, deutsch
<slug>.en.html   Demo, englisch — CSS zeichengleich zur deutschen Fassung
<slug>.en.json   Faktenblatt, englisch
```

Danach den Stil in `build.py` in `ORDER_DE` und `ORDER_EN` in die passende Familie eintragen
und `python3 build.py` laufen lassen.

#### Die Referenz-UI

Der ganze Sinn des Katalogs ist Vergleichbarkeit: Jede Demo zeigt **denselben Inhalt**. Ändere
niemals Texte, Reihenfolge oder Bestandteile.

| Baustein | Inhalt |
|---|---|
| Kopfzeile | „Projekte" + Zähler „12" |
| Zeile 1 | Nexus · vor 2 Std. · Aktiv |
| Zeile 2 | Autowrite Studio · gestern · Aktiv |
| Zeile 3 | Balance Ally · vor 4 Tagen · Pausiert |
| Feld | Eingabefeld, `readonly`, Platzhalter „Suchen…" |
| Aktionen | Primärbutton „Neues Projekt", Sekundärbutton „Importieren" |

Wie du das anordnest, gewichtest und mit stiltypischen Zusatzelementen anreicherst — Raster,
Ornamente, Noise, Scanlines, Fensterrahmen —, ist deine gestalterische Freiheit. Genau dort
entsteht der Stil. Eine Demo, die nur „dieselbe Box mit anderem Radius" ist, verfehlt den Zweck.

#### Die Scoping-Regel

31 Stylesheets teilen sich eine Seite. Damit das funktioniert, gilt ohne Ausnahme:

1. Genau **ein** `<style>`-Element, danach genau **ein** `<div class="style-<slug>">`.
2. **Jeder** CSS-Selektor beginnt mit `.style-<slug>`. Kein `:root`, kein `html`, kein `body`,
   kein alleinstehendes `*`, kein nackter Element-Selektor. Auch innerhalb von `@media`.
3. CSS-Variablen nur auf `.style-<slug>` definieren, niemals auf `:root`.
4. `@keyframes`-Namen mit `<slug>-` präfigieren.
5. Klassennamen innerhalb der Demo sind frei — sie sind durch Regel 2 abgeschirmt.

`build.py` prüft das bei jedem Lauf und bricht bei Verstoß mit Zeilenangabe ab.

#### Weitere Regeln

- **Keine externen Ressourcen** außer Google Fonts. Kein `<script>`, kein `<link>`, kein
  `@import`, keine Bild-URLs. Grafik aus Gradients, `box-shadow`, Borders, Inline-SVG als
  `data:`-URI, Unicode-Zeichen und CSS-Mustern.
- **Schriften** nur aus Google Fonts oder System-Stacks, immer mit generischem Fallback.
  Die verwendeten Familien gehören ins JSON-Feld `googleFonts`; `build.py` lädt sie zentral.
- **Selbstgenügsam**: `.style-<slug>` setzt eigene `background`, `color`, `font-family`,
  `line-height`, `box-sizing`, `color-scheme` und `min-height: 460px`. Die Demo erbt nichts
  von außen und sieht in hellem wie dunklem Viewer-Theme identisch aus.
- **Breite** 780 px als Bezugsgröße; die Seite skaliert die Demo in ihren Rahmen.
- **Ehrlichkeit vor Schönheit**: Wenn ein Stil systematisch Kontrastprobleme erzeugt
  (Neumorphismus, Glassmorphism), setze das so um — und benenne es im Feld `a11y`.

#### Der finder-Block

Jedes Faktenblatt braucht am Ende einen `finder`-Block. Er speist den Stil-Finder und ist
**sprachneutral** — er steht in `.json` und `.en.json` wortgleich, nur `signature` wird übersetzt.

```json
"finder": {
  "mode": "light",
  "a11y": 4,
  "platform": { "web": 5, "mobile": 3, "desktop": 4 },
  "fits": ["content", "marketing"],
  "tone": ["calm", "warm"],
  "signature": "Ein Satz, höchstens 110 Zeichen: das eine Merkmal, an dem man ihn erkennt."
}
```

`fits` aus: `dev-tool` `data` `content` `consumer` `marketing` `creative` `civic` `internal`.
`tone` aus: `precise` `calm` `warm` `loud` `playful` `formal` `technical` `nostalgic`
`expressive` `austere`. Zwei bis vier je Feld — zwei treffende sind besser als vier ungefähre.
`mode` aus: `light` `dark` `both` — `both` nur, wenn der Stil in beiden Modi gleich überzeugend
ist.

Nutze die ganze Skala 1–5. Wenn alles bei 3 und 4 landet, ist die Zahl wertlos. Sieh dir zur
Orientierung `neumorphism.json` (a11y 1) und `civic-service.json` (a11y 5) an.

#### Das Faktenblatt

Struktur siehe jede bestehende `.json`. Was zählt:

- `markers` — neun bis elf **harte, überprüfbare** Merkmale mit Zahlen. Nicht „wirkt modern",
  sondern „Radius 0–2 px", „Trennung ausschließlich über 1 px-Linien", „Kontrast > 12:1".
- `examples` — mindestens vier **echte** Vertreter mit konkreter Beobachtung. Nicht „sieht gut
  aus", sondern welche Farbwerte, Radien, Schriften dort tatsächlich zu sehen sind.
- `verdict` — ehrlich. Ein klares Nein ist eine gute Antwort.
- `scores` — ganze Zahlen 1 bis 5. `effort` und `density` sind Eigenschaften, kein Urteil.

Die englische Fassung ist eine echte Übersetzung, keine maschinelle: idiomatische Fachbegriffe,
amerikanisches Englisch, gleiche Stimme. Die Felder `slug`, `palette`, `scores`, `googleFonts`
und `combinesWith` bleiben unverändert; `family` kommt aus der Liste in `build.py`.

Bei Zeichenraster-Layouts (Monospace, ASCII-Rahmen, aufgefüllte Spalten) haben englische Wörter
andere Längen — die Füllzeichen entsprechend nachzählen und anpassen, niemals das CSS ändern.

### Prüfen vor dem Pull Request

```sh
python3 build.py                    # muss ohne Fehler durchlaufen
python3 tools/palette-check.py      # muss ohne Befund durchlaufen
```

Dann `docs/de/index.html` und `docs/en/index.html` im Browser öffnen und den neuen Eintrag
ansehen — in hellem und dunklem Theme, breit und schmal.

---

## English

Two kinds of contributions are welcome: **corrections** to existing entries, and a **new
style**.

### Corrections

The fact sheets are researched but not infallible. Wrong dates, misattributed authorship,
outdated color values, claims about current products that no longer hold — issues and pull
requests are welcome. A source helps for contested facts.

The four scores (longevity, recognisability, effort, density) are judgements, not measurements.
They are arguable — please argue in an issue with reasoning rather than changing them silently.

### Adding a style

A style is four files in `styles/`: `<slug>.html`, `<slug>.json`, `<slug>.en.html`,
`<slug>.en.json`. Then add the slug to `ORDER_DE` and `ORDER_EN` in `build.py` under the right
family and run `python3 build.py`.

**The reference UI never changes.** Every demo shows the same content: header "Projekte" plus
counter "12"; three rows (Nexus · vor 2 Std. · Aktiv / Autowrite Studio · gestern · Aktiv /
Balance Ally · vor 4 Tagen · Pausiert); a readonly search field; a primary button "Neues
Projekt" and a secondary "Importieren". English versions use: "Projects", "2 hrs ago",
"yesterday", "4 days ago", "Active", "Paused", "Search…", "New project", "Import".

How you arrange, weight and enrich that with style-typical elements is your design freedom —
that is where the style lives. A demo that is merely "the same box with a different radius"
misses the point.

**The scoping rule.** 31 stylesheets share one page. Exactly one `<style>` element followed by
exactly one `<div class="style-<slug>">`; **every** CSS selector starts with `.style-<slug>`
(no `:root`, `html`, `body`, bare `*` or bare element selectors, not even inside `@media`);
CSS variables only on `.style-<slug>`; `@keyframes` names prefixed with `<slug>-`. `build.py`
enforces this and fails the build on violation.

**No external resources** except Google Fonts — no `<script>`, `<link>`, `@import` or image
URLs. Graphics come from gradients, `box-shadow`, borders, inline SVG as `data:` URIs, Unicode
characters and CSS patterns. The demo must be self-sufficient: set your own `background`,
`color`, `font-family`, `line-height`, `box-sizing`, `color-scheme` and `min-height: 460px`,
so it inherits nothing and looks identical in light and dark viewer themes. Design against a
width of 780 px; the page scales the demo into its frame.

**Honesty over prettiness**: if a style systematically causes contrast problems, build it that
way — and say so in the `a11y` field.

For the fact sheet, what matters: `markers` are nine to eleven hard, checkable properties with numbers,
not adjectives; `examples` are at least four real-world instances with concrete observations;
`verdict` is honest, and a clear no is a good answer; `scores` are integers 1–5, where `effort`
and `density` are properties rather than verdicts.

**Every fact sheet needs a `finder` block** at the end — it feeds the style finder and is
language-neutral: identical in `.json` and `.en.json`, only `signature` is translated. `mode` is
one of `light` `dark` `both`. See the German section above for the field list.

Run `python3 build.py` and `python3 tools/palette-check.py`, then open `docs/de/index.html` and
`docs/en/index.html` and look at your entry — in both themes, wide and narrow.

---

Beiträge stehen unter denselben Lizenzen wie das Projekt: [MIT](LICENSE) für Code,
[CC BY 4.0](LICENSE-CONTENT.md) für Texte.
Contributions are licensed under the same terms as the project: [MIT](LICENSE) for code,
[CC BY 4.0](LICENSE-CONTENT.md) for text.

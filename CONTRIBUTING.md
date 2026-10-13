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

Die Smartphone-Adaption gehört ebenfalls dazu: in `mobile/catalog.py` explizite Stilwerte
unter `THEMES` und einen deutschen sowie englischen Anpassungshinweis unter `NOTES` ergänzen.
Stilspezifische Layoutregeln stehen in `mobile/catalog.css`, alle Selektoren sind auf
`.m-app` bzw. `.m-app.m-<slug>` begrenzt. Der Build verweigert fehlende mobile Einträge.
Die Desktop-Faktenblattwerte bleiben Quellen für den Stil; mobile Abweichungen sind eigene,
offen benannte Entwurfsentscheidungen. Die gemeinsame mobile Referenz und ihr Verhalten
stehen in `mobile/catalog.js`; keine projektspezifischen Varianten der Referenztexte ergänzen.

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

37 Stylesheets teilen sich eine Seite. Damit das funktioniert, gilt ohne Ausnahme:

1. Genau **ein** `<style>`-Element, danach genau **ein** `<div class="style-<slug>">`.
2. **Jeder** CSS-Selektor beginnt mit `.style-<slug>`. Kein `:root`, kein `html`, kein `body`,
   kein alleinstehendes `*`, kein nackter Element-Selektor. Auch innerhalb von `@media`.
3. CSS-Variablen nur auf `.style-<slug>` definieren, niemals auf `:root`.
4. `@keyframes`-Namen mit `<slug>-` präfigieren.
5. Klassennamen innerhalb der Demo sind frei — sie sind durch Regel 2 abgeschirmt.

`build.py` prüft das bei jedem Lauf und bricht bei Verstoß mit einer Diagnose zum betroffenen Stil ab.

#### Weitere Regeln

- **Keine externen Ressourcen.** Kein `<script>`, kein `<link>`, kein
  `@import`, keine Bild-URLs. Grafik aus Gradients, `box-shadow`, Borders, Inline-SVG als
  `data:`-URI, Unicode-Zeichen und CSS-Mustern.
- **Schriften** nur aus der Bibliothek von Google Fonts oder System-Stacks, immer mit generischem
  Fallback. Die verwendeten Familien gehören ins JSON-Feld `googleFonts`; `build.py` liefert sie
  zentral aus `fonts/` aus. Eine neue Familie braucht dort ihre Dateien (siehe Schriften).
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
- `palette` — sechsstellige Hex-Werte (`#FF6600`, nicht `#f60`).
- `sources` — optional eine Liste aus `{"title": "Belegtes Thema", "url": "https://…"}`.
  Verlinke die konkrete Quelle und benenne im Titel, welche Aussage sie stützt. In beiden
  Sprachen bleiben die URLs gleich; die Titel werden übersetzt. Demo-Entscheidungen und
  redaktionelle Einschätzungen dürfen nicht als universelle Produktvorgaben erscheinen.

Die englische Fassung ist eine echte Übersetzung, keine maschinelle: idiomatische Fachbegriffe,
amerikanisches Englisch, gleiche Stimme. Die Felder `slug`, `palette`, `scores`, `googleFonts`
und `combinesWith` bleiben unverändert; `family` kommt aus der Liste in `build.py`.

Bei Zeichenraster-Layouts (Monospace, ASCII-Rahmen, aufgefüllte Spalten) haben englische Wörter
andere Längen — die Füllzeichen entsprechend nachzählen und anpassen, niemals das CSS ändern.

### Schriften

Die Seite liefert alle Schriften selbst aus; keine Seite lädt etwas von fremden Servern
(`tests/test_fonts.py` prüft das). `fonts/fonts.json` nennt für jede Familienangabe aus
`FONT_SPECS`, `CHROME_FONTS` und `HOME_FONTS` in `build.py` die Schnitte mit `unicode-range`,
für jede Datei Quelle und sha256, die Abrufdaten und für jede Familie den Lizenztext in
`fonts/licenses/` samt Begründung der Herkunft (`why`). `build.py` kopiert `fonts/` nach
`docs/fonts/`, schreibt daraus `docs/fonts/catalog.css` und `home.css` und bricht ab, wenn eine
Datei fehlt, ihre sha256 nicht stimmt, ein Lizenztext fehlt oder eine Release-Familie ein Zeichen
der früheren Google-Bereiche nicht abdeckt.

- `fonts/google/` enthält die Dateien, die Google Fonts für genau die früheren Anfragen
  ausgeliefert hat, unverändert (CSS2-API, Abruf mit aktuellem Chrome als User-Agent, alle
  `unicode-range`-Teilstücke). Pfade wie unter `fonts.gstatic.com/s/`.
- `fonts/release/` enthält unveränderte Release-Dateien für Familien, deren Lizenz einen Reserved
  Font Name trägt, der im Schriftnamen steckt (Plex, Lato, Orbitron, Istok, Cabin, Audiowide,
  Press Start 2P, Share). Die Teilstücke von Google sind geänderte Fassungen, und die OFL erlaubt
  den reservierten Namen ohne schriftliche Erlaubnis nur unveränderten Dateien; eine Absprache
  zwischen Google und den Urhebern gilt nicht für Dritte (OFL-FAQ 2.6 und 2.12). IBM Plex kommt
  aus den npm-Paketen von IBM, jeweils in der Fassung, die Googles Dateien gleicht (Plex Sans als
  variable Fassung, Plex Sans Condensed 1.3, Plex Mono 2.004); die übrigen kommen aus
  github.com/google/fonts (Lato 1.104 aus dem ersten Commit, weil Google Fonts weiter diese Fassung
  ausliefert). Was gegen Googles Dateien geprüft ist und wo eine Familie abweicht, steht in `why`.
- Unter `google` steht für jede Release-Familie je Schnitt die `unicode-range` der früheren
  Google-Antwort. Die Schnitte decken sie zusammen ab, auch Zeichen, die erst der Browser aus
  anderen Glyphen bildet (etwa den geschützten Bindestrich U+2011 aus U+2010). Fehlt ein Zeichen,
  holt der Browser es aus einer anderen Schrift.

Neue Familie: Hole die CSS2-Antwort für die neue Angabe mit einem aktuellen Browser als
User-Agent, lade alle darin genannten woff2-Dateien unverändert nach `fonts/google/`, trage
Angabe, Schnitte und Dateien mit sha256 in `fonts/fonts.json` ein und lege `OFL.txt` aus
github.com/google/fonts als `fonts/licenses/OFL-<Familie>.txt` ab. Nennt die Lizenz einen
Reserved Font Name, der im Schriftnamen vorkommt, nimm stattdessen unveränderte Release-Dateien
und trage die Bereiche der CSS2-Antwort unter `google` ein; `build.py` verweigert sonst den Bau.

### Impressum

Die Angaben (Name, Anschrift, E-Mail, Umsatzsteuer-ID) stehen nur in `legal/notice.json`.
`legal/page.py` baut daraus `de/impressum/` und `en/legal-notice/`; jede Seite verlinkt das
Impressum in der Fußzeile, zusammen mit den Schwesterprojekten Bildsprache und Farbsprache
(`SIBLINGS` in `build.py`).

### Prüfen vor dem Pull Request

```sh
python3 build.py                    # muss ohne Fehler durchlaufen
python3 tools/palette-check.py      # muss ohne Befund durchlaufen
python3 -m unittest discover -s tests -v
node --test tests/finder.test.cjs    # Node 22+, keine npm-Pakete nötig
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

Also add an explicit mobile theme to `THEMES` and German/English adaptation notes to `NOTES`
in `mobile/catalog.py`. Style-specific layout rules live in `mobile/catalog.css`, scoped to
`.m-app` or `.m-app.m-<slug>`. Missing mobile entries fail the build. Mobile deviations are
authored design choices, distinct from the desktop fact-sheet values. The shared mobile
reference and its behavior live in `mobile/catalog.js`; keep its reference copy consistent.

**The reference UI never changes.** Every demo shows the same content: header "Projekte" plus
counter "12"; three rows (Nexus · vor 2 Std. · Aktiv / Autowrite Studio · gestern · Aktiv /
Balance Ally · vor 4 Tagen · Pausiert); a readonly search field; a primary button "Neues
Projekt" and a secondary "Importieren". English versions use: "Projects", "2 hrs ago",
"yesterday", "4 days ago", "Active", "Paused", "Search…", "New project", "Import".

How you arrange, weight and enrich that with style-typical elements is your design freedom —
that is where the style lives. A demo that is merely "the same box with a different radius"
misses the point.

**The scoping rule.** 37 stylesheets share one page. Exactly one `<style>` element followed by
exactly one `<div class="style-<slug>">`; **every** CSS selector starts with `.style-<slug>`
(no `:root`, `html`, `body`, bare `*` or bare element selectors, not even inside `@media`);
CSS variables only on `.style-<slug>`; `@keyframes` names prefixed with `<slug>-`. `build.py`
enforces this and fails the build on violation.

**No external resources** — no `<script>`, `<link>`, `@import` or image
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

Use six-digit hex values in `palette`. Optional `sources` entries contain `title` and an
HTTPS `url`; name the specific claim the source supports, translate titles, and keep the
URLs identical between languages. Distinguish demo choices and editorial judgments from
product specifications. The build validates the file inventory, reference content, metadata,
references, and identical demo CSS across languages.

**Fonts** come from the Google Fonts library or system stacks. The site serves them itself from
`fonts/`; no page loads anything from another host. `fonts/fonts.json` lists the faces for every
family spec in `build.py`, the source and sha256 of every file, the retrieval dates, and the
license text in `fonts/licenses/` with the reason for each family's source (`why`).
`fonts/google/` holds the files Google Fonts served for the former requests, unchanged. Families
whose license reserves a name that is part of the font name (Plex, Lato, Orbitron, Istok, Cabin,
Audiowide, Press Start 2P, Share) use unmodified release files from `fonts/release/` instead,
because Google's subsets are modified versions and the OFL allows the reserved name only on
unmodified files unless the authors grant written permission. IBM Plex comes from IBM's npm
packages in the version that matches Google's files (Plex Sans as the variable version, Plex Sans
Condensed 1.3, Plex Mono 2.004); `why` records what was compared with Google's files and where a
family differs. For each release family, `google` holds the unicode-range of the former Google
response per style; the faces cover it together, including characters the browser builds from
other glyphs (such as the non-breaking hyphen U+2011 from U+2010), or the browser takes them from
another font. To add a family, fetch the CSS2 response with a current browser user agent, store
every woff2 file it lists unchanged in `fonts/google/`, add the spec, faces and files with sha256
to `fonts/fonts.json`, and copy its `OFL.txt` from github.com/google/fonts to `fonts/licenses/`.
The build fails on a missing file, a changed hash, a missing license, a reserved name on a Google
subset, or a release family that misses part of its former Google ranges.

The legal notice details live only in `legal/notice.json`; every page footer links the legal
notice and the sister projects Bildsprache and Farbsprache.

Also run `python3 -m unittest discover -s tests -v` and
`node --test tests/finder.test.cjs` after building. The JavaScript tests require Node 22+
but no npm packages. They check scoring and prompt output, not browser layout or native
dialog behavior; manual browser review remains necessary.

---

Beiträge stehen unter denselben Lizenzen wie das Projekt: [MIT](LICENSE) für Code,
[CC BY 4.0](LICENSE-CONTENT.md) für Texte.
Contributions are licensed under the same terms as the project: [MIT](LICENSE) for code,
[CC BY 4.0](LICENSE-CONTENT.md) for text.

## Prinzipien und Nutzungskontexte / Principles and contexts

`explorer/catalog.py` enthält die zweisprachigen Texte und Verweise, `explorer/catalog.css`
die Gestaltung und `explorer/catalog.js` die lokalen Zustandswechsel. Ein Kontext ist keine
zusätzliche Stilfamilie: Er beschreibt Aufgabe, Eingabe, Einschränkungen und passende Prinzipien.
Gerätebeispiele brauchen eigene Aufgaben und eine klare Beschreibung der Simulationsgrenzen.
Verweise auf Stile müssen vorhandene Einträge nennen; Quellen müssen Primärquellen sein.

Die interaktiven Beispiele speichern keine Daten dauerhaft. Navigation, Auswahl, Fehler und
Rückwege müssen mit der Tastatur funktionieren. Textwerte werden als Text ausgegeben bzw.
vor HTML-Ausgabe maskiert. Neue Zustandswechsel erhalten passende Regressionstests in
`tests/explorer.test.cjs`; die CI führt `node --test tests/*.test.cjs` aus.

Principles and contexts live in `explorer/` with bilingual copy and primary sources. Contexts
describe tasks, input and constraints rather than adding style families. Give device examples
appropriate tasks and explicit simulation limits. Keep state session-only, preserve keyboard
access and recovery, escape user text, and test meaningful state transitions.

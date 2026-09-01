# Stil-Katalog

**31 UI-Stilrichtungen — jede als gerendertes Beispiel derselben Oberfläche.**
31 UI style directions — each rendered as the very same interface.

→ **[grundhofer.github.io/designsprache](https://grundhofer.github.io/designsprache)**
&nbsp;·&nbsp; [Deutsch](https://grundhofer.github.io/designsprache/de/)
&nbsp;·&nbsp; [English](https://grundhofer.github.io/designsprache/en/)

![Stil-Katalog: dieselbe Projektliste in vier Stilen, daneben der Prompt-Export für KI-Agenten. — The same project list in four styles, alongside the prompt export for AI agents.](og.png)

---

## Wozu

Über UI-Stile wird in Adjektiven geredet — „clean", „modern", „verspielt". Wörter, unter denen
sich jeder etwas anderes vorstellt. Dieser Katalog ersetzt sie durch Anschauung: **31-mal
dieselbe Projektliste**, überall dieselben dreizehn Textbausteine, nur die Gestaltung ändert
sich. Dadurch wird vergleichbar, was ein Stil tatsächlich entscheidet — und was nur Geschmack
ist.

Zu jedem Eintrag gehört ein Faktenblatt mit harten Werten statt Stimmungen: Herkunft, neun bis
elf überprüfbare Merkmale, echte Vertreter mit belegten Farben und Radien, Risiken,
Barrierefreiheits-Konsequenzen, Alterungsverhalten und Plattform-Eignung.

Talk about UI styles happens in adjectives — words that mean something different to everyone.
This catalog replaces them with evidence: **the same project list 31 times**, the same thirteen
pieces of text throughout, only the design changes. Every entry comes with a fact sheet of hard,
checkable values rather than moods.

## Stil finden und als Prompt kopieren / Find a style, copy it as a prompt

Der Knopf **Stil finden** stellt neun Fragen — was du baust, wie es wirken soll, hell oder
dunkel, Dichte, Haltbarkeit, Auffälligkeit, Aufwand, Barrierefreiheit, Plattformen. Daraus
entsteht eine Empfehlung der fünf passendsten Einträge, und **jeder Treffer wird begründet**,
auch die negativen: „Haltbarkeit 5 von 5", „Ist hell, du wolltest dunkel".

Zu jeder Empfehlung gehört **Als Prompt kopieren**. Der Knopf legt eine vollständige
Stilanweisung für einen KI-Agenten in die Zwischenablage: Kernidee, die acht harten Parameter
mit konkreten Werten, Palette, Schriften, alle Regeln, die bekannten Fehlerquellen des Stils,
Barrierefreiheit und Praxistipp. Rund 4.000 Zeichen, direkt einsetzbar — genau das Material, das
einen Agenten davon abhält, wieder generisches Standard-UI zu bauen. Ist die Zwischenablage
gesperrt, wird der Text stattdessen eingeblendet und markiert.

**Find a style** asks nine questions and recommends the five closest entries, justifying every
match from the fact sheets' own attributes. **Copy as prompt** then puts a complete style
instruction for an AI agent on your clipboard — core idea, the eight hard parameters with
concrete values, palette, type, every rule, the known failure modes, accessibility and one
practical tip. About 4,000 characters, ready to paste.

---

## Aufbau / How it works

Kein Framework. Ein Python-Skript ohne Abhängigkeiten baut aus den Quelldateien drei statische
Seiten. No framework — one dependency-free Python script turns the sources into three static
pages.

```
styles/<slug>.html      Demo: ein <style>-Element + ein <div class="style-slug">
styles/<slug>.json      Faktenblatt / fact sheet
styles/<slug>.en.*      englische Fassung, CSS zeichengleich / English, byte-identical CSS
landing.html            zweisprachige Eingangsseite / bilingual entry page
build.py                Generator
tools/palette-check.py  Prüfwerkzeug / check tool
docs/                   erzeugt, nicht eingecheckt / generated, not committed
```

```sh
python3 build.py                 # docs/index.html, docs/de/, docs/en/
python3 tools/palette-check.py   # Palettendubletten / palette duplicates
```

**Die Scoping-Regel.** 31 Stylesheets teilen sich eine Seite. Deshalb beginnt in jeder Demo
jeder CSS-Selektor mit `.style-<slug>`, `@keyframes` sind slug-präfigiert, und es gibt kein
`:root`, kein `body`, keinen nackten Element-Selektor. `build.py` prüft das bei jedem Lauf und
bricht bei Verstoß ab — ebenso, wenn deutscher Text geändert wurde, ohne den englischen
nachzuziehen.

31 stylesheets share one page, so every CSS selector in a demo starts with `.style-<slug>`,
`@keyframes` names are slug-prefixed, and there is no `:root`, `body` or bare element selector.
`build.py` enforces this on every run.

`tools/palette-check.py` findet Stilpaare mit zwei oder mehr praktisch identischen bunten Farben
(OKLab-ΔE unter 2, Neutrale ausgenommen) und läuft in der CI. Es findet Stilpaare, die man sonst
für einen Stil hält. Runs in CI; finds pairs that would otherwise read as one style.

Die Demos sind handgebautes HTML und CSS — keine Bilder, keine Skripte, keine Bibliotheken.
The demos are hand-built HTML and CSS — no images, no scripts, no libraries.

---

## Warum „Designsprache" / Why "Designsprache"

Der Katalog beantwortet, **welche Sprachen es gibt und was jede entscheidet**. Die Antwort auf
*welche wird meine* kommt später in dasselbe Repository: Design-Tokens im DTCG-Format, aus einer
Quelle nach CSS, Tailwind, Compose und SwiftUI generiert. Bis dahin steht hier nur der Katalog —
kein Platzhalter, er funktioniert für sich.

The catalog answers **which languages exist and what each of them decides**. The answer to
*which one becomes mine* will land in this same repository later: design tokens in DTCG format,
generated from one source into CSS, Tailwind, Compose and SwiftUI.

---

## Mitmachen / Contributing

Ein 32. Stil und Korrekturen an Jahreszahlen, Urhebern oder Farbwerten sind willkommen — siehe
**[CONTRIBUTING.md](CONTRIBUTING.md)**. A 32nd style and corrections are welcome.

## Lizenz / License

**Code** (`build.py`, `tools/`, `landing.html`, die Demos) — [MIT](LICENSE).
**Texte** (die Faktenblätter, die Prosa der Seite) — [CC BY 4.0](LICENSE-CONTENT.md).

Die vier Kennzahlen je Stil sind fachliche Einschätzungen, keine Messwerte. Genannte Produkt-
und Markennamen gehören ihren Inhabern; die Demos sind eigenständige Nachbauten im jeweiligen
Stil, keine Kopien. The four scores are professional judgements, not measurements; the demos are
original recreations, not copies.

© Sebastian Grundhöfer

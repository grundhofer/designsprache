# Technology and content review — 2026-09-05

The static architecture suits this catalog: a Python generator, local HTML/CSS demos,
JSON fact sheets and a small browser script. No framework migration or package dependency
is needed. The initial build passed, but it did not catch several content, interaction and
validation defects. Those findings are corrected in the changes accompanying this report.

## Findings and changes

| Priority | Finding | Resolution |
| --- | --- | --- |
| High | Fact sheets incorrectly exempted readable metadata from contrast requirements; some confused decorative borders, font sizes or AA/AAA target sizes. | Corrected both languages and linked the specific W3C guidance. Deliberately weak demo styles remain identified as demonstrations rather than accessible product templates. |
| High | Finder and detail overlays lacked modal semantics and background keyboard isolation. Some entry points left focus behind the overlay. | Use labeled native dialogs, explicit initial focus and cancellation handling. Opening a fact sheet from recommendations preserves the underlying results and restores focus on return. The English finder and nested fact-sheet path were verified in Chrome on 2026-09-06. |
| Medium | “No preference” awarded partial points, lowering otherwise perfect matches. Results showed only six explanations, which could conceal mismatches. | Unspecified preferences contribute no weight; all scored explanations appear. Regression tests cover both languages. |
| Medium | Search advertised markers but indexed only the name, aliases, family and idea. | Index markers, all eight parameters and font names too. Test marker search, family filtering and empty results. |
| Medium | Table sorting was mouse-only; several containers overwrote shared horizontal padding; small secondary text had insufficient contrast. | Use buttons in sortable headers, preserve horizontal gutters, darken/lighten the viewer's secondary text tokens, and let the toolbar scroll normally on narrow screens. |
| Medium | Bilingual CSS and neutral metadata equality were documented but unenforced. Missing or invalid finder fields could silently fall back to invented defaults. | Validate the four-file inventory, required fields, reference content, inert inputs, score ranges, references, font names, source URLs and bilingual parity before generation. |
| Medium | The CSS check accepted lookalike scope prefixes and ignored global resource rules. | Reject wrong class boundaries, root sibling escapes, imports, external CSS URLs, unsupported global rules and unclosed blocks. Handle punctuation inside quoted strings. This remains a constrained source checker, not a general CSS sanitizer. |
| Medium | Palette matching counted several variants of one color as multiple shared colors and skipped shorthand hex. | Use maximum one-to-one matching, normalize shorthand, and store the portal's orange in six-digit form. |
| Low | The primer advertised seven parameters while fact sheets and exports contained eight. | Add texture as the eighth parameter in both languages. |
| Low | Cloned demo inputs repeated document IDs; prompt fallback could leave duplicate hints or lose focus. | Prefix cloned input IDs and associated labels; replace old hints and restore focus after legacy copying. |

## Content corrections and additions

Added a bilingual **From a style to a usable interface** guide covering semantic roles,
loading/empty/error states, narrow layouts, text resizing and accessibility checks.
Prompt exports now include corresponding implementation guidance.

Corrected Material's five core tonal palettes using [Google's color-system tutorial](https://codelabs.developers.google.com/customizing-material-color),
the backdrop-filter compatibility timeline using [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter),
and the distinction between the terminal's DEC graphics set and IBM PC code pages using
the [DEC terminal manual](https://vt100.net/docs/vt220-rm/chapter4.html).

Reframed the e-paper entry as a monochrome demo choice, with device-dependent capabilities,
using [E Ink's technology description](https://www.eink.com/tech/detail/Benefits),
[Kaleido specifications](https://www.eink.com/brand/detail/Kaleido) and
[TRMNL device profiles](https://trmnl.com/framework/docs/3.3/devices).
Removed the claim that a translucent tint guarantees background-independent contrast and
the unsupported reading-comfort promise attached to warm colors.

The accessibility corrections distinguish [text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html),
[essential non-text cues](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html),
[target sizes and exceptions](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html),
[resizable text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html), and
[contrast with text halos](https://www.w3.org/WAI/WCAG22/Techniques/general/G18).
The terminal cursor now stops after four cycles (4.24 seconds), alongside its existing
reduced-motion behavior.

## Validation

- Site, artifact and social-preview HTML build successfully: 31 entries, 9 families, both languages.
- 11 Python regression tests pass for source contracts, bilingual drift, CSS isolation and palette matching.
- 12 Node regression tests pass for generated JavaScript, search/filter behavior, finder scoring,
  complete explanations and all 62 language-specific prompts. No npm packages are required.
- Palette check passes across 465 pairs, retaining the existing documented exception.
- The GitHub Pages sanity checks and `git diff --check` pass. Regression tests now run in CI.

## Remaining review limits

### Browser follow-up — 2026-09-06

Rebuilt the site and reran all 11 Python tests, 12 Node tests, the palette check and both
staged and unstaged whitespace checks successfully. Used native Chrome controls to inspect
the generated English page locally on macOS, including its dark desktop rendering.

- Opening the finder moves focus to its close button and removes the background catalog
  from the accessibility tree. Tab moves to the first answer; Return selects it.
- Showing recommendations moves focus to the results heading and renders five matches.
- Opening the first recommended fact sheet moves focus to its heading. Escape closes only
  that sheet, retains the finder results and restores focus to the originating entry button.
- Show text exposes the exported prompt. Closing the finder restores catalog navigation;
  Shift-Tab then reaches the sort selector preceding the finder button.
- Activating the table's longevity header by mouse and then Return reverses its ordering.
  The ascending result starts with the two entries scoring 1, with a visible focus outline
  on the header button.

The browser session changed to another tab during navigation to the German page, so this
pass stopped without completing that language's interactive checks. Clipboard permissions,
full Tab/Shift-Tab wraparound, other entry points and browsers, narrow layouts, enlarged text
and light-theme rendering remain unverified. The Node tests exercise generated logic with
small fixtures; they do not render a page or verify browser accessibility behavior.

Sources now support selected claims; this is not a citation-complete historical audit of every
example, product snapshot, date or quoted measurement. Transparent-background contrast figures
and display-specific effects need rendered measurement before making a conformance claim.
Editorial scores remain judgments rather than measured guarantees.

The catalog intentionally loads all demos and many external Google Fonts. Its generated
language pages are roughly 0.9 MB each before compression; actual font transfer, loading speed
and layout stability have not been profiled. Further performance changes should follow measurement.
Since 2026-10-12 the site serves these fonts itself; see the section of that date below.

This report records validation before publication. Deployment status is tracked separately
in the repository's GitHub Actions workflow.

## Mobile reference extension — 2026-09-08

Added explicit mobile adaptations for all 31 existing styles, in both languages. A shared
Desktop/Smartphone switch controls gallery previews, the fact-sheet demo and finder results.
The mobile screen selector compares the same list, project detail or creation form across
styles. Mobile layouts reflow up to 390 px without the desktop scaling transform.

The fact-sheet prototype supports navigation, search, creation and importing project names.
It uses session-only state that resets on close, style/view change or reset. Gallery and
finder previews remain inert. Mobile prompts append the style's adaptation note, base values
and platform implementation guidance; the fact-sheet palette stays explicitly labeled as
such. Platform references distinguish Material, Apple / Liquid Glass and Samsung One UI;
the latter two are future catalog additions, not new entries in this release.

Validation: 12 Python and 20 Node tests cover source inventory, bilingual data, generated
scripts, all 186 mobile style/language/screen combinations, safe text rendering, creation,
import, search, state isolation, view-control synchronization, language links, finder
preview switching and mobile prompt exports. Build, palette and Pages sanity checks pass.
The new mobile layouts have not received a rendered browser or real-device accessibility
pass. Tests use lightweight DOM fixtures and do not establish visual or native-platform
conformance. Mobile theme values are authored adaptations rather than vendor specifications.

## Platform-language entries — 2026-09-08

Added Apple / Liquid Glass and Samsung / One UI as the Platform Languages family: 33 entries
in 10 families. Both have bilingual fact sheets, desktop demos, three mobile screens,
finder scores and mobile prompt guidance. The mobile introduction now derives its entry
count from the catalog, and family sections have stable anchors for direct links.

Apple's entry distinguishes a functional material layer from generic glassmorphism.
Its web demo has opaque content and optional toolbar blur, with opaque fallbacks for
unsupported blur and matching transparency/contrast preferences. It does not claim native
refraction or morphing. One UI's mobile list has an upper viewing area; detail and form
screens reduce that area. Its broad desktop layout is explicitly an authored adaptation.

Sources are Apple and Samsung's own announcements and design documentation. Numeric markers,
palettes and demo font choices are explicitly authored values, not measured vendor tokens.
The mobile platform scores describe the relevant ecosystem (iOS or Galaxy-like Android),
with the limitation stated in each fact sheet. Existing scores remain editorial judgments.

Validation: 12 Python and 22 Node tests, the bilingual build, Pages sanity checks and the
palette comparison across 528 pairs pass. Existing mobile tests now cover 198 combinations
of style, language and screen. New checks verify platform-sensitive finder scores, mobile
exports, family anchors and the derived count. Rendered browser and device testing of these
new entries remains outstanding; the earlier browser results do not cover them.

## Erweiterung: drei Ebenen, Prinzipien und Nutzungskontexte (2026-09-08)

- Der Katalog trennt Stile/Designsprachen, Bedienprinzipien und Geräte/Nutzungskontexte in
  drei direkt verlinkbare Ansichten. URL-Parameter, Sprachwechsel und Browser-Verlauf werden
  synchronisiert. Die statischen Beschreibungen bleiben ohne JavaScript zugänglich.
- Vier neue zweisprachige Einträge: Microsoft/Fluent, GNOME/Adwaita, KDE/Breeze und IBM/Carbon.
  Insgesamt 37 Einträge in zehn Familien, jeweils mit Desktop- und Smartphone-Adaption,
  Faktenblatt, Quellen und bestehendem Finder-/Prompt-Export.
- Sechs interaktive Prinzipien: Hierarchie/Gruppierung, schrittweise Offenlegung,
  Speichern/Fehler/erneuter Versuch/Rückgängig, Navigation, adaptive Bediengröße und
  inklusive Darstellung (200% Text, Kontrast, lange Texte, reduzierte Bewegung).
- Acht Kontexte: Web, Desktop, Smartphone, Tablet/Foldable, Smartwatch, TV, Auto und XR.
  Kontextbezogene Aufgaben, Quellen und Verknüpfungen zu Stilen/Prinzipien sind enthalten.
  Zustände bleiben lokal im Arbeitsspeicher. Uhr, Auto und XR werden ausdrücklich als
  schematische Beispiele mit beschriebenen Grenzen dargestellt.
- Validierung: Python-Build für beide Sprachen; 16 Python- und 40 Node-Tests bestanden.
  Zustandsmaschinen, Event-Anbindung mit DOM-Testobjekten, Rückwege, Routing, Sprachlinks,
  Maskierung von Texteingaben, vollständige Referenzen, gültige HTML-Verschachtelung,
  eindeutige IDs, ein Hauptbereich/eine Hauptüberschrift und No-JS-Inhalte geprüft.
  CI-Sanity für beide Sprachen bestanden. 666 Palettenpaare ohne neue Dublette.
- Grenzen: keine visuelle Browserprüfung und keine Tests mit Screenreader oder realer
  Smartwatch, Fernbedienung, Fahrzeug- oder XR-Hardware. Die automatisierten DOM-Tests
  ersetzen keine Layout- oder Hilfsmittelprüfung. Es wird keine native Implementierung,
  vollständige WCAG-Konformität oder Freigabe für den Fahrzeugeinsatz behauptet.

## Startseitensprache, README und Ebenenwechsel (2026-09-09)

- Fehlerursache der leeren Seite: Der globale Selektor `[data-level]` erfasste nach der
  Initialisierung auch das HTML-Wurzelelement. Beim Wechsel der Ebene wurde dadurch das
  gesamte Dokument ausgeblendet. Die Auswahl ist jetzt auf direkte Ebenen im Hauptbereich
  beschränkt; der Zustandsmarker am Dokument hat zusätzlich einen eigenen Namen.
- Der verbesserte Regressionstest berücksichtigt das dynamische Wurzelattribut: Er schlägt
  mit dem alten Code in beiden Sprachen fehl und besteht mit der Korrektur auch bei
  wiederholten Wechseln zwischen allen drei Ebenen.
- Die Startseite bestimmt ihre Sprache vor dem Rendern aus `?lang=de|en`, einer gespeicherten
  manuellen Wahl oder der ersten unterstützten Browsersprache; Standard ist Englisch.
  Der sichtbare Deutsch-/English-Schalter aktualisiert Texte, Dokumentensprache und Metadaten.
  Gesperrter Browserspeicher verhindert das Umschalten nicht. Ohne JavaScript bleiben beide
  Kataloglinks und Sprachfassungen zugänglich.
- README.md ist eine gekürzte englische Einführung mit deutschem README-Link in der ersten
  Zeile. README.de.md enthält die entsprechende deutsche Fassung und den Rückverweis.
- Build, 16 Python-Tests, 47 Node-Tests und Palettenprüfung bestanden. Die neuen Prüfungen
  decken Spracherkennung, Prioritäten, Umschalten, Speicherung und deren Ausfall ab.
  Keine zusätzliche visuelle Browser- oder Hardwareprüfung durchgeführt.

## System / Hell / Dunkel (2026-09-09)

- Gemeinsamer Darstellungsschalter neben der Sprachwahl auf Startseite und beiden Katalogseiten.
  Standard ist System; CSS reagiert dabei unmittelbar auf Änderungen der Systemeinstellung.
  Hell und Dunkel setzen eine manuelle Vorgabe. Die Auswahl wird vor dem ersten Rendern
  eingelesen und bleibt über Seiten- und Sprachwechsel erhalten.
- Offene Tabs und aus dem Browser-Verlauf wiederhergestellte Seiten synchronisieren die
  Einstellung. Gesperrter Browserspeicher verhindert den Wechsel nicht. Ohne JavaScript
  bleibt die automatische Anpassung per CSS erhalten.
- Die gemeinsamen Farben und Bedienelemente liegen in `viewer/`. Der dunkle Seitenrahmen
  hat hellere Oberflächen, deutlichere Trennlinien und stärkere Sekundärtexte. Die kleinen
  goldfarbenen Überschriften im hellen Rahmen wurden für ausreichenden Kontrast abgedunkelt.
  Die 37 Stilpaletten und ihre mobilen Adaptionen wurden nicht geändert.
- Build, 17 Python-Tests, 52 Node-Tests und Palettenprüfung bestanden. Der neue Kontrasttest
  prüft fünf Textrollen gegen drei Hintergrundrollen je Modus sowie die ausgewählte Aktion
  auf mindestens 4,5:1. Tests decken Voreinstellungen, Sprach-/Seitenwechsel, gesperrten
  Speicher, Tab-Synchronisierung und Browser-Cache-Wiederherstellung ab.
- Keine zusätzliche visuelle Browser- oder Hilfsmittelprüfung. Die Prüfung der Farbpaare
  ist kein Nachweis vollständiger WCAG-Konformität der Seite oder ihrer Referenzdemos.

## Schriften lokal, Impressum, Schwesterprojekte (2026-10-12)

- Keine Seite lädt mehr etwas von fonts.googleapis.com oder fonts.gstatic.com. Die Schriften
  liegen in `fonts/` (457 Dateien, 15.520.441 Bytes: 346 woff2 von Google, 71 Release-Dateien,
  39 OFL-Texte, `fonts.json`) und werden nach `docs/fonts/` kopiert; `docs/fonts/catalog.css`
  und `home.css` enthalten die Schnitte und Achsenbereiche der früheren Anfragen, mit
  `font-display:swap` wie bisher. Herkunft, Abrufdatum und sha256 jeder Datei stehen in
  `fonts/fonts.json`; der Build prüft sie.
- 29 Familien nutzen unverändert die Dateien, die Google Fonts ausgeliefert hat, mit denselben
  `unicode-range`-Teilstücken. Zehn Familien, deren Lizenz einen Reserved Font Name im
  Schriftnamen trägt, kommen als unveränderte Release-Dateien: IBM Plex aus den npm-Paketen von
  IBM (`@ibm/plex-sans-variable` 0.2.0, `@ibm/plex-sans-condensed` 1.1.0, `@ibm/plex-mono` 1.1.0),
  Lato 1.104, Orbitron, Istok Web, Cabin Sketch, Audiowide, Press Start 2P und Share Tech Mono als
  TTF aus github.com/google/fonts.
- Abgleich mit Googles Dateien (fontTools und HarfBuzz, je angefragtem Gewicht, alle Zeichen der
  Google-Dateien, Paarabstände über ASCII, Umlaute und gängige Satzzeichen): Umrisse, Laufweiten
  und Paarabstände sind gleich, mit diesen Ausnahmen. Plex Mono 2.004 (Google: 2.3) weicht beim
  weichen Trennzeichen U+00AD ab (Laufweite 0 statt 600; in Chrome ist es in beiden Fällen
  0 breit) und in den Umrissen von Ѳ ѳ Ҫ ҫ Ө ө. Die TTF-Dateien enthalten Hinting-Tabellen
  (TrueType), Googles woff2 nicht. Eine erste Fassung nutzte IBMs statische Plex Sans 1.1.0, deren
  Laufweiten bei 500 und 600 abwichen, sowie Plex Mono 2.5.0 (anderes Sternchen) und Plex Sans
  Condensed 2.0.0 (Gravis nach Buchstaben als Kombinationszeichen); diese Fassungen sind ersetzt.
- `unicode-range` der Release-Familien: Die Schnitte decken je Stil zusammen die Bereiche der
  früheren Google-Antwort ab (in `fonts.json` unter `google`, vom Build geprüft). Eine erste
  Fassung nannte nur die Zeichen in Googles Dateien; dadurch kam der geschützte Bindestrich
  U+2011 (etwa in „Stil‑Katalog“), den Chrome vorher aus dem Bindestrich der Plex-Datei bildete,
  aus einer Systemschrift. In Chrome kommen die Glyphen dieser Stellen wieder aus denselben
  Schriften wie vor der Umstellung (`CSS.getPlatformFontsForNode`, gleiche Glyphenzahlen je
  Schrift). Zeichen, die in Googles Bereich lagen, aber in Googles Datei fehlten, und die die
  Release-Datei enthält (etwa ‡ und ‰, bei Istok Web auch Sonderleerzeichen und U+2010 bis
  U+2012), zeigt die Seite jetzt aus der Familie statt aus einer Ersatzschrift. Auf den Seiten
  kommt keines davon in diesen Schriften vor.
- Neue Seiten `de/impressum/` und `en/legal-notice/`; Angaben nur in `legal/notice.json`, die
  Tests lesen sie von dort. Jede ausgelieferte Seite verlinkt das Impressum und die
  Schwesterprojekte Bildsprache und Farbsprache in der Seitensprache, die Startseite und die neue
  zweisprachige `404.html` in beiden Sprachen. Die 404 nutzt absolute Pfade ab `/designsprache/`,
  weil GitHub Pages sie unter jedem fehlenden Pfad ausliefert.
- Build, 34 Python-Tests, 52 Node-Tests, Palettenprüfung und die Sanity-Schritte der CI bestanden
  (Python 3.12, Node 22). Headless Chrome 154, je Startseite (de/en), Katalog (de/en, Ebenen
  Prinzipien und Kontexte), Impressum (de/en) und 404 unter einem tiefen und einem flachen
  fehlenden Pfad bei 390 und 1280 px, hell und dunkel: keine Anfrage an fremde Hosts, keine
  fehlgeschlagene Anfrage, keine Konsolenfehler außer dem 404-Status der Fehlerseite selbst, kein
  seitliches Scrollen, keine Schrift im Status `error`; auf den Katalogseiten sind alle 39
  Familien geladen. Die Fußzeilenlinks führen zum Impressum der jeweiligen Sprache, auch von der
  404 aus.
- Bildvergleich gegen den unveränderten Stand mit Google Fonts (37 Demos je Katalogseite in DE
  1280 px hell und EN 390 px dunkel, dazu sieben Bereiche des Seitenrahmens und die Startseite,
  mit Vergleichsaufnahme des alten Stands gegen Rauschen): IBM Plex, auch die Demo IBM Carbon,
  und alle übrigen Schriften sind pixelgleich oder weichen um höchstens 64 von 255 je Kanal ab,
  fast nur in Verläufen und Schatten, die auch zwischen zwei Aufnahmen des alten Stands
  schwanken. Sichtbar anders ist Press Start 2P in der Demo Pixel 8-Bit: Mit Googles Datei
  fehlten in Chrome auf macOS einzelne Pixelreihen (in „NEUES PROJEKT“ und „IMPORTIEREN“ die
  oberste, dazu Reihen im Titel), die TTF zeigt die Glyphen vollständig (154 bzw. 137 deutlich
  abweichende Pixel; Umrisse und Laufweiten beider Dateien sind gleich). Das ist eine bewusste
  Änderung; wer das alte Bild will, müsste Googles geänderte Datei ausliefern, was der Reserved
  Font Name „Press Start 2P“ ohne Erlaubnis nicht zulässt. Erwartete Unterschiede: das geänderte
  Kolophon und die neuen Fußzeilen.
- Grenzen: Die TTF-Dateien (15 im Repo, zehn davon lädt der Katalog, 1.480.915 Bytes) sind
  größer als Googles Teilstücke. Lokal gemessen (Chrome, Cache aus, Server ohne Kompression)
  überträgt der Katalog 61 Schriftdateien mit 3.110.957 Bytes statt 60 mit 1.840.784 Bytes, dazu
  `catalog.css` mit 240.718 Bytes (gzip -9: 38.576) statt 40.585 Bytes CSS von Google; die
  Startseite 355.442 statt 328.158 Bytes Schriften plus `home.css` mit 15.836 Bytes. `docs/`
  wächst von 2,3 auf 17,8 MB, davon 5,47 MB für alle 124 Teilstücke von Noto Sans JP, von denen
  der Katalog sechs lädt. Ob GitHub Pages TTF und CSS komprimiert, ist nicht geprüft. Offen zur
  Entscheidung: die TTF verlustfrei als WOFF2 verpacken (laut OFL-FAQ ohne Umbenennung zulässig,
  aber eine eigene Verarbeitung) oder den Mehrverbrauch so hinnehmen. Geprüft ist nur Chrome auf
  macOS; unter Windows kann das Hinting der TTF anders aussehen als Googles Dateien.

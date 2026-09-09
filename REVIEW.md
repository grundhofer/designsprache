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

[Read in English → README.md](README.md)

# Designsprache

**37 Designsprachen · 6 interaktive Prinzipien · 8 Nutzungskontexte.**

Ein visueller Referenzkatalog für Softwaregestaltung. Vergleiche dieselbe Projektliste in
unterschiedlichen Stilen, probiere Bedienprinzipien aus und entdecke die Unterschiede von
Desktop bis Smartwatch.

**[Katalog öffnen](https://grundhofer.github.io/designsprache/)** ·
[Deutsch](https://grundhofer.github.io/designsprache/de/) ·
[English](https://grundhofer.github.io/designsprache/en/)

![Dieselbe Projektliste in vier Stilen, daneben der Prompt-Export für KI-Agenten.](og.png)

## Drei Ebenen entdecken

- **[Stile & Designsprachen](https://grundhofer.github.io/designsprache/de/?level=styles):**
  Desktop- und Smartphone-Vergleiche, belegte Faktenblätter, Paletten, Typografie und Abwägungen.
  Mit Swiss, Bauhaus, Material, Apple Liquid Glass, One UI, Fluent, Adwaita, Breeze und Carbon.
- **[Gestaltungs- & Bedienprinzipien](https://grundhofer.github.io/designsprache/de/?level=principles):**
  sechs bedienbare Beispiele für Gruppierung, schrittweise Offenlegung, Rückmeldung und
  Fehlerbehebung, Navigation, adaptive Bedienelemente und inklusive Darstellung.
- **[Geräte & Nutzungskontexte](https://grundhofer.github.io/designsprache/de/?level=contexts):**
  passende Aufgaben für Web, Desktop, Smartphone, Tablet/Foldable, Smartwatch, TV, Auto und XR.

**Stil finden** empfiehlt fünf passende Einträge und begründet die Auswahl. **Als Prompt kopieren**
exportiert konkrete Gestaltungsanweisungen für einen KI-Coding-Agenten. Öffne ein Faktenblatt,
um seinen mobilen Ablauf auszuprobieren.

Die Startseite erkennt deine bevorzugte Browsersprache und merkt sich manuelle Sprachwechsel.
**System / Hell / Dunkel** folgt der Geräteeinstellung oder speichert deine Auswahl für alle Seiten;
die Referenzdemos behalten ihre eigenen Farben.
Demo-Daten bleiben im Arbeitsspeicher. Gerätebeispiele sind schematische Web-Prototypen;
Kennzahlen sind redaktionelle Einschätzungen, keine Barrierefreiheitsnachweise oder Plattformfreigaben.

## Lokal starten

Benötigt Python 3.10+; Node.js 22+ nur für die JavaScript-Tests. Keine Paketinstallation nötig.

```sh
python3 build.py
python3 -m http.server 8000 --directory docs
```

Öffne [localhost:8000](http://localhost:8000). Prüfungen nach dem Build:

```sh
python3 -m unittest discover -s tests -v
node --test tests/*.test.cjs
python3 tools/palette-check.py
```

## Projektaufbau

| Pfad | Inhalt |
| --- | --- |
| `styles/` | Zweisprachige Faktenblätter und isolierte HTML/CSS-Demos |
| `mobile/`, `viewer/` | Mobile Interaktionen und gemeinsame Seitenthemes |
| `explorer/` | Prinzipien, Nutzungskontexte und Navigation zwischen den Ebenen |
| `landing.html`, `build.py` | Startseite und statischer Generator ohne Abhängigkeiten |
| `tools/`, `tests/` | Quellen-, Paletten- und Funktionsprüfungen |
| `docs/` | Erzeugte Website; nicht eingecheckt |

GitHub Actions prüft die Änderungen und veröffentlicht `main` auf GitHub Pages.
[CONTRIBUTING.md](CONTRIBUTING.md) beschreibt die Inhalts- und CSS-Regeln;
[REVIEW.md](REVIEW.md) dokumentiert Umfang und Grenzen der Prüfungen.

## Lizenz

Code: [MIT](LICENSE). Texte: [CC BY 4.0](LICENSE-CONTENT.md).
Produktnamen gehören ihren Inhabern. Die Demos sind eigenständige Interpretationen.

© Sebastian Grundhöfer

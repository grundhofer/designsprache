[Deutsch lesen → README.de.md](README.de.md)

# Designsprache

**37 design languages · 6 interactive principles · 8 device contexts.**

A visual reference for designing software. Compare the same project list across styles,
try interaction patterns, and explore how interfaces change from desktop to smartwatch.

**[Open the catalog](https://grundhofer.github.io/designsprache/)** ·
[English](https://grundhofer.github.io/designsprache/en/) ·
[Deutsch](https://grundhofer.github.io/designsprache/de/)

![The same project list in four styles, with an AI prompt export.](og.png)

## Explore three levels

- **[Styles & design languages](https://grundhofer.github.io/designsprache/en/?level=styles):**
  desktop and smartphone comparisons, sourced fact sheets, palettes, typography and tradeoffs.
  Includes Swiss, Bauhaus, Material, Apple Liquid Glass, One UI, Fluent, Adwaita, Breeze and Carbon.
- **[Design & interaction principles](https://grundhofer.github.io/designsprache/en/?level=principles):**
  six hands-on examples covering grouping, progressive disclosure, feedback and recovery,
  navigation, adaptive controls and inclusive presentation.
- **[Devices & contexts](https://grundhofer.github.io/designsprache/en/?level=contexts):**
  task-specific examples for web, desktop, smartphone, tablet/foldable, smartwatch, TV, car and XR.

**Find a style** recommends five matches and explains its choices. **Copy as prompt** exports
concrete design instructions for an AI coding agent. Open a fact sheet to try its mobile flow.

The home page detects your preferred browser language and remembers manual language changes.
**System / Light / Dark** follows your device setting or saves your choice across the site;
reference demos retain their own colors.
Demo data stays in memory. Device examples are schematic web prototypes; scores are editorial
judgments, not accessibility certifications or platform approvals.

## Build locally

Requires Python 3.10+; Node.js 22+ is needed only for JavaScript tests. No package installation.

```sh
python3 build.py
python3 -m http.server 8000 --directory docs
```

Open [localhost:8000](http://localhost:8000). To run checks after building:

```sh
python3 -m unittest discover -s tests -v
node --test tests/*.test.cjs
python3 tools/palette-check.py
```

## Project structure

| Path | Contents |
| --- | --- |
| `styles/` | Bilingual fact sheets and scoped HTML/CSS demos |
| `mobile/`, `viewer/` | Mobile interactions and shared viewer themes |
| `explorer/` | Principles, device contexts and three-level navigation |
| `landing.html`, `build.py` | Home page and dependency-free static generator |
| `tools/`, `tests/` | Source, palette and behavior checks |
| `docs/` | Generated site; not committed |

GitHub Actions runs the checks and deploys `main` to GitHub Pages.
See [CONTRIBUTING.md](CONTRIBUTING.md) for content and CSS rules, and [REVIEW.md](REVIEW.md)
for validation scope and limitations.

## License

Code: [MIT](LICENSE). Written content: [CC BY 4.0](LICENSE-CONTENT.md).
Product names belong to their respective owners. Demos are independent interpretations.

© Sebastian Grundhöfer

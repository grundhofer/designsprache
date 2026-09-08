"""Mobile adaptations: authored design choices, not vendor specifications."""
import json
from pathlib import Path

ROOT = Path(__file__).parent

# ground, surface, ink, accent, accent ink, rule, radius, font, layout
THEMES = {
    'apple-liquid-glass': ('#EEF3FA', '#FFFFFF', '#172434', '#0069DB', '#FFFFFF', '#B5C3D4', '22px', 'system-ui', 'cards'),
    'one-ui': ('#F3F3F5', '#FFFFFF', '#17171B', '#2158C9', '#FFFFFF', '#D0D0D6', '24px', 'Roboto', 'cards'),
    'swiss': ('#FFFFFF', '#FFFFFF', '#0B0B0B', '#E30613', '#FFFFFF', '#D4D4D4', '0', 'Inter', 'ruled'),
    'bauhaus': ('#F4F1E8', '#F5C518', '#111111', '#0B4EA2', '#FFFFFF', '#111111', '0', 'Jost', 'blocks'),
    'de-stijl': ('#F5F3EE', '#FFFFFF', '#14110F', '#1F3D99', '#FFFFFF', '#14110F', '0', 'Archivo', 'blocks'),
    'memphis': ('#F9BA65', '#B392E1', '#17130E', '#17130E', '#FFFFFF', '#17130E', '0', 'Poppins', 'cards'),
    'swiss-punk': ('#E9E5DC', '#E9E5DC', '#100E0C', '#E4271B', '#FFFFFF', '#100E0C', '0', 'Archivo', 'ruled'),
    'web-brutalism': ('#FFFFFF', '#EFEFEF', '#000000', '#0000EE', '#FFFFFF', '#808080', '0', 'Times New Roman', 'ruled'),
    'skeuomorph': ('#6B4728', '#D9D4C6', '#251B13', '#245C99', '#FFFFFF', '#867D6A', '8px', 'Lato', 'cards'),
    'flat': ('#FFFFFF', '#EDF8FC', '#10252D', '#006F9E', '#FFFFFF', '#C4DDE8', '4px', 'Work Sans', 'blocks'),
    'material-expressive': ('#FEF7FF', '#ECE6F0', '#21005D', '#6750A4', '#FFFFFF', '#79747E', '24px', 'Roboto Flex', 'cards'),
    'neumorphism': ('#E0E5EC', '#E0E5EC', '#37465D', '#4C5C73', '#FFFFFF', '#8494AB', '24px', 'Nunito', 'cards'),
    'glassmorphism': ('#0A0D26', '#293257', '#FFFFFF', '#00C8FF', '#0A0D26', '#829AC0', '24px', 'Inter', 'cards'),
    'claymorphism': ('#EFE9FF', '#B9A6FF', '#40316F', '#5B34CF', '#FFFFFF', '#766199', '30px', 'Nunito', 'cards'),
    'dev-noir': ('#08080B', '#14151A', '#EDEDEF', '#5E6AD2', '#FFFFFF', '#52525E', '8px', 'Inter', 'cards'),
    'warm-editorial': ('#FAF7F2', '#F3EEE4', '#2B2622', '#A8432A', '#FFFFFF', '#C8BDAA', '10px', 'Newsreader', 'ruled'),
    'neo-brutalism': ('#F4F4F0', '#FF90E8', '#000000', '#FFDE00', '#000000', '#000000', '2px', 'Space Grotesk', 'cards'),
    'terminal-mono': ('#0C0C0C', '#101010', '#D9D9D4', '#00C08B', '#0C0C0C', '#7C7C74', '0', 'Geist Mono', 'console'),
    'data-dense': ('#0D1116', '#1B222B', '#C9D2DC', '#2BD97C', '#0D1116', '#647587', '0', 'IBM Plex Sans Condensed', 'console'),
    'spatial-depth': ('#0A0C12', '#1C2231', '#F3F6FA', '#86E7B8', '#0A0C12', '#798698', '28px', 'Inter', 'cards'),
    'civic-service': ('#FFFFFF', '#FFFFFF', '#0B0C0C', '#00703C', '#FFFFFF', '#505A5F', '0', 'Public Sans', 'ruled'),
    'e-paper': ('#E4E2DD', '#D8D6D1', '#2B2B2B', '#2B2B2B', '#E4E2DD', '#5C5C5A', '0', 'Inter', 'ruled'),
    'y2k-aero': ('#07456F', '#D9F3FE', '#073855', '#0E6CB0', '#FFFFFF', '#73A7C6', '20px', 'Istok Web', 'cards'),
    'vaporwave': ('#0B0121', '#21103E', '#F9EFFF', '#01CDFE', '#0B0121', '#B967FF', '0', 'Chakra Petch', 'cards'),
    'retro-futurism': ('#0E0C08', '#14120C', '#FFB000', '#FFB000', '#0E0C08', '#6B5A34', '2px', 'Share Tech Mono', 'console'),
    'organic-blob': ('#FAF6EF', '#D9E5D5', '#2C3A31', '#4F7355', '#FFFFFF', '#92AA8D', '30px 12px 28px 16px', 'Nunito', 'cards'),
    'maximalism': ('#D3CBB7', '#F15060', '#1B1714', '#1B1714', '#FFFFFF', '#1B1714', '0', 'Bricolage Grotesque', 'cards'),
    'aurora-mesh': ('#07080C', '#19152F', '#F7F8FA', '#B09AFF', '#07080C', '#70648E', '12px', 'Inter', 'cards'),
    'hand-drawn': ('#FBFAF6', '#F2EEE3', '#1E1B18', '#B83A22', '#FFFFFF', '#6B645B', '5px 15px 7px 12px', 'Neucha', 'cards'),
    'editorial-print': ('#FBF8F1', '#F4EFE3', '#17140F', '#8C2F1F', '#FFFFFF', '#A79B85', '0', 'Newsreader', 'ruled'),
    'pixel-8bit': ('#0B0A12', '#2A2C46', '#EDEBF2', '#3BE081', '#0B0A12', '#A2A1B5', '0', 'Silkscreen', 'console'),
    'playful-chunky': ('#FFFFFF', '#F1F8FC', '#3B3B47', '#4CC93F', '#13330F', '#6C7781', '18px', 'Nunito', 'cards'),
    'portal-density': ('#F5F5F5', '#FFFFFF', '#333333', '#0867BF', '#FFFFFF', '#949494', '2px', 'Noto Sans JP', 'blocks'),
}

NOTES = {
    'apple-liquid-glass': ('Deckende Projektzeilen liegen unter einer abgesetzten, glasartigen Navigation. Die untere Leiste bleibt beschriftet. Blur ist eine optionale CSS-Annäherung; Lichtbrechung, Morphing und native Systemanpassungen werden nicht nachgebildet. Ohne Blur oder bei erhöhtem Kontrast sind die Bedienflächen deckend.', 'Opaque project rows sit beneath a distinct glass-like navigation layer. The bottom bar keeps text labels. Blur is an optional CSS approximation; refraction, morphing and native system adaptations are not reproduced. Without blur or with increased contrast, controls are opaque.'),
    'one-ui': ('Der Listentitel erhält oben einen ruhigen Betrachtungsbereich; Suche, Projektzeilen und Hauptaktion folgen darunter. Detail und Formular verkürzen den Kopf zugunsten von Inhalt und Bildschirmtastatur. Weiße Fokusblöcke bleiben deckend. Roboto dient hier als Ersatzschrift, nicht als Nachbildung von SamsungOne.', 'The list title gets a quiet upper viewing area, followed by search, project rows and the primary action. Detail and form screens shorten the header to leave room for content and the on-screen keyboard. White focus blocks stay opaque. Roboto is a substitute here, not a reproduction of SamsungOne.'),
    'swiss': ('Das Raster wird einspaltig; Zeit und Status stehen unter dem Namen. Die rote Zählung und die harten Linien bleiben.', 'The grid becomes one column; time and status move below the name. The red count and hard rules remain.'),
    'bauhaus': ('Primärfarben und geometrische Flächen tragen die Hierarchie. Rechteckige Zeilen erhalten eine große Touchfläche.', 'Primary colors and geometric fields carry hierarchy. Rectangular rows receive generous touch targets.'),
    'de-stijl': ('Schwarze Stege und ungleiche Farbflächen bleiben erhalten; die Projekte folgen einer eindeutigen vertikalen Lesereihenfolge.', 'Black dividers and unequal color fields remain; projects follow a clear vertical reading order.'),
    'memphis': ('Muster und wechselnde Kartenformen bleiben außerhalb der Schrift. Die Bedienflächen werden nicht gedreht.', 'Patterns and varied card shapes stay clear of text. Interactive surfaces are not rotated.'),
    'swiss-punk': ('Der typografische Bruch sitzt im Titel. Projektnamen und Formularbeschriftungen bleiben unverdreht und vollständig lesbar.', 'Typographic disruption lives in the heading. Project names and form labels remain upright and fully readable.'),
    'web-brutalism': ('Serifenschrift und sichtbare Links bleiben; Bedienelemente erhalten mehr Höhe und Formulare eine lineare Reihenfolge.', 'Serif type and visible links remain; controls gain height and forms follow a linear order.'),
    'skeuomorph': ('Materialrahmen und plastische Tasten bleiben. Die mobile Liste verzichtet auf zusätzliche Werkzeugleisten.', 'Material framing and dimensional buttons remain. The mobile list omits extra toolbars.'),
    'flat': ('Flache Farbblöcke trennen die Projekte. Text ergänzt den Status; eine klare Hauptaktion steht unter der Liste.', 'Flat color blocks separate projects. Text identifies status; a clear primary action sits below the list.'),
    'material-expressive': ('Tonale Karten, kontrastierende Rundungen und eine breite Hauptaktion übertragen den Stil auf Touch. Diese Web-Demo ist kein nativer Android-Screen.', 'Tonal cards, contrasting shapes and a wide primary action adapt the style for touch. This web demo is not a native Android screen.'),
    'neumorphism': ('Weiches Relief bleibt als Oberfläche. Text wird abgedunkelt; Linien und Fokusmarkierungen ergänzen die schwer erkennbaren Konturen.', 'Soft relief remains a surface treatment. Darker text, borders and focus outlines supplement the indistinct contours.'),
    'glassmorphism': ('Glas liegt über einem festgelegten Hintergrund. Deckende Leseflächen sichern die Texte; native Systemmaterialien werden nicht simuliert.', 'Glass sits over a defined background. Opaque reading surfaces support text; this does not reproduce native system materials.'),
    'claymorphism': ('Voluminöse Karten und Innenlichter bleiben. Weniger Fläche pro Zeile und breite Tasten schaffen Platz für die Bedienung.', 'Voluminous cards and inner highlights remain. Compact rows and wide buttons leave room for interaction.'),
    'dev-noir': ('Die dunkle Ebenenfolge bleibt. Tastaturkürzel entfallen zugunsten beschrifteter Touchaktionen; Metadaten erhalten mehr Kontrast.', 'The dark layer hierarchy remains. Labeled touch actions replace shortcuts; metadata gains contrast.'),
    'warm-editorial': ('Die Papierfläche wird zur einspaltigen Leseliste. Serifentitel und feine Trennlinien bleiben, Formulare erhalten deutliche Feldgrenzen.', 'The paper surface becomes a single-column reading list. Serif headings and fine rules remain; form fields get explicit boundaries.'),
    'neo-brutalism': ('Harte Schatten und schwarze Konturen bleiben. Zwischen den Karten ist Platz für Schatten und Fokus; nichts überdeckt die Nachbarzeile.', 'Hard shadows and black outlines remain. Cards leave room for shadows and focus; nothing overlaps an adjacent row.'),
    'terminal-mono': ('Das Zeichenraster wird schmaler. Befehlsartige Beschriftungen bleiben, aber alle Aktionen sind per Touch und Tastatur erreichbar.', 'The character grid narrows. Command-like labels remain, but every action supports touch and keyboard.'),
    'data-dense': ('Zeit und Status stehen unter dem Projektnamen. Haarlinien und tabellarische Ziffern bleiben; Touchflächen werden trotz hoher Informationsdichte größer.', 'Time and status move below each project name. Hairlines and tabular figures remain; touch targets grow despite the dense presentation.'),
    'spatial-depth': ('Gestapelte, gerundete Flächen werden in eine flache Touch-Navigation übersetzt. Die Demo zeigt keine räumliche Blick- oder Handinteraktion.', 'Stacked rounded surfaces become flat touch navigation. The demo does not represent spatial gaze or hand interaction.'),
    'civic-service': ('Große Beschriftungen, Vollsockel und gelber Tastaturfokus bleiben. Touch und eine externe Tastatur sind gleichwertige Zugänge.', 'Large labels, solid button bases and yellow keyboard focus remain. Touch and an external keyboard are equally supported.'),
    'e-paper': ('Monochrome Flächen und harte Regeln bleiben. Ansichten wechseln ohne Animation; die Darstellung ist eine Web-Adaption, keine Display-Simulation.', 'Monochrome surfaces and hard rules remain. Views switch without animation; this is a web adaptation, not a display simulation.'),
    'y2k-aero': ('Glanz bleibt auf Kopf- und Aktionsflächen. Projektzeilen bekommen einen ruhigen, hellen Grund und deutliche Schrift.', 'Gloss stays on the header and action surfaces. Project rows get a quiet light background and clear type.'),
    'vaporwave': ('Neonrahmen und Raster bleiben dekorativ. Über dem Text liegen weder Scanlines noch Farbverschiebungen.', 'Neon frames and grids remain decorative. Text has no scanline overlays or color aberration.'),
    'retro-futurism': ('Beschriftete Maschinenfelder und bernsteinfarbene Anzeigen bleiben. Schalter werden zu breiten Touchaktionen mit Text.', 'Labeled machine panels and amber readouts remain. Switches become wide, text-labeled touch actions.'),
    'organic-blob': ('Organische Kartenkonturen bleiben, aber Text und Touchflächen liegen auf einem stabilen, rechteckigen Innenraster.', 'Organic card outlines remain, while text and touch targets use a stable rectangular inner grid.'),
    'maximalism': ('Collage entsteht durch Papierlagen, Kontraste und wechselnde Flächen. Bedienflächen bleiben in Lesereihenfolge und überlappen sich nicht.', 'Collage comes from paper layers, contrast and varied surfaces. Controls follow reading order without overlapping.'),
    'aurora-mesh': ('Lichtfelder bleiben im Hintergrund. Deckende Karten tragen die Texte; Bewegung ist für die Bedienung nicht nötig.', 'Light fields stay in the background. Opaque cards carry text; interaction requires no animation.'),
    'hand-drawn': ('Unregelmäßige Konturen bleiben, Feldgrößen und Lesereihenfolge werden stabil. Die Handschrift ist Text, keine Bildgrafik.', 'Irregular outlines remain; field sizes and reading order are stable. Handwriting uses real text, not images.'),
    'editorial-print': ('Spalten werden zu einer Lesespalte mit Nummern, Serifentiteln und starken Linien. Details öffnen auf einer eigenen Ansicht.', 'Columns become one reading column with numbers, serif headings and strong rules. Details open in a separate view.'),
    'pixel-8bit': ('Stufenkanten und begrenzte Palette bleiben. Pixeltext darf umbrechen; ganze Screens werden nicht auf Telefonbreite verkleinert.', 'Stepped edges and a limited palette remain. Pixel type can wrap; whole screens are not shrunk to phone width.'),
    'playful-chunky': ('Dicke Tastensockel und runde Karten bleiben. Breite beschriftete Aktionen ersetzen kleine Symbolschalter.', 'Thick button bases and rounded cards remain. Wide labeled actions replace small icon controls.'),
    'portal-density': ('Kategorie-Farbbalken bleiben an den Zeilen. Mehrspaltige Portalbereiche werden gestapelt und die Trefferflächen vergrößert.', 'Category color bars remain on rows. Multi-column portal sections stack, and touch targets grow.'),
}


def assets(slugs, lang):
    if set(slugs) != set(THEMES) or set(slugs) != set(NOTES):
        raise ValueError('Every catalog entry needs an explicit mobile theme and bilingual adaptation note')
    keys = ('ground', 'surface', 'ink', 'accent', 'on-accent', 'rule', 'radius', 'font', 'layout')
    css = (ROOT / 'catalog.css').read_text()
    for slug, values in THEMES.items():
        tokens = dict(zip(keys, values))
        font = tokens.pop('font')
        tokens.pop('layout')
        css += '\n.m-app.m-' + slug + '{' + ''.join('--m-' + k + ':' + v + ';' for k, v in tokens.items())
        css += '--m-font:' + ('system-ui' if font == 'system-ui' else '"' + font + '"') + ',' + ('serif' if font in ('Newsreader', 'Times New Roman') else 'sans-serif') + ';}'
        light_ink = sum(int(values[2][i:i+2], 16) for i in (1, 3, 5)) > 510
        css += '\n.m-app.m-' + slug + '{color-scheme:' + ('dark' if light_ink else 'light') + ';}'
    payload = {s: {'layout': THEMES[s][-1], 'note': NOTES[s][lang == 'en'],
                   'tokens': dict(zip(keys[:-1], THEMES[s][:-1]))} for s in slugs}
    script = 'var MOBILE_DATA = ' + json.dumps(payload, ensure_ascii=False).replace('</', '<\\/') + ';\n'
    script += (ROOT / 'catalog.js').read_text()
    return css, script


def controls(lang, sheet=False):
    en = lang == 'en'
    prefix = 'sheet' if sheet else 'catalog'
    return f'''<div class="view-controls" data-view-controls hidden>
  <div class="view-switch" role="group" aria-label="{'Reference layout' if en else 'Referenzlayout'}">
    <button type="button" data-view="desktop" aria-pressed="true">Desktop</button>
    <button type="button" data-view="mobile" aria-pressed="false">Smartphone</button>
  </div>
  <div class="mobile-states" hidden><label for="{prefix}-screen">{'Screen' if en else 'Ansicht'}</label>
    <select id="{prefix}-screen" data-mobile-screen>
      <option value="list">{'Project list' if en else 'Projektliste'}</option>
      <option value="detail">{'Project details' if en else 'Projektdetail'}</option>
      <option value="new">{'New project' if en else 'Neues Projekt'}</option>
    </select>
  </div>
</div>'''


def intro(lang, count=None):
    count = len(THEMES) if count is None else count
    if lang == 'en':
        return f'''<aside class="mobile-intro wrap" hidden>
  <span class="eyebrow">Same projects · different space</span>
  <h2>{count} styles for a small screen</h2>
  <p>Compare the list, detail and new-project screens. Open an entry to try its mobile flow.
    These are authored touch adaptations of the existing styles, not native platform screenshots.</p>
  <details><summary>Style and platform are two decisions</summary>
    <p><a href="https://m3.material.io/">Material 3 Expressive</a> contributes tonal surfaces and distinctive shapes.
    <a href="https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass">Apple’s Liquid Glass</a>
    defines materials for controls and navigation across Apple platforms.
    <a href="https://developer.samsung.com/one-ui/layout/basic.html">Samsung One UI</a> separates an upper viewing area
    from a more reachable interaction area. A visual style still needs the navigation and input conventions of its target platform.</p>
    <p>Find Apple / Liquid Glass and Samsung One UI in the Platform Languages family, with their own fact sheets and demos.
    Material remains in Digital Eras so the catalog also preserves its historical context.</p>
  </details>
</aside>'''
    return f'''<aside class="mobile-intro wrap" hidden>
  <span class="eyebrow">Dieselben Projekte · anderer Raum</span>
  <h2>{count} Stile auf kleinem Bildschirm</h2>
  <p>Vergleiche Liste, Detail und das Anlegen eines Projekts. Öffne einen Eintrag, um den mobilen Ablauf auszuprobieren.
    Die Demos sind eigene Touch-Adaptionen der bestehenden Stile, keine nativen Plattform-Screenshots.</p>
  <details><summary>Stil und Plattform sind zwei Entscheidungen</summary>
    <p><a href="https://m3.material.io/">Material 3 Expressive</a> steuert tonale Flächen und prägnante Formen bei.
    <a href="https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass">Apples Liquid Glass</a>
    definiert Materialien für Bedienelemente und Navigation auf Apple-Plattformen.
    <a href="https://developer.samsung.com/one-ui/layout/basic.html">Samsung One UI</a> trennt einen oberen Betrachtungsbereich
    von einem besser erreichbaren Interaktionsbereich. Ein visueller Stil braucht zusätzlich die Navigations- und Eingabekonventionen seiner Zielplattform.</p>
    <p>Apple / Liquid Glass und Samsung One UI stehen mit eigenen Faktenblättern und Demos in der Familie Plattformsprachen.
    Material bleibt in Digitale Epochen, damit auch seine historische Einordnung sichtbar bleibt.</p>
  </details>
</aside>'''

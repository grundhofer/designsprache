"""Three editorial levels, bilingual principle labs and device-context references."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).parent

def esc(value):
    return html.escape(str(value), quote=True)

# Contexts are task/input references, deliberately independent of style rankings.
CONTEXTS = [
    dict(id='web', name=['Web','Web'], tagline=['Links, Verlauf, wechselnde Fenster','Links, history, changing windows'],
         task=['Ein Projekt per Link öffnen und zur Übersicht zurückkehren.','Open a project by link and return to its overview.'],
         rules=[['Adresse und Zurück-Verhalten gehören zur Orientierung.','URLs and back navigation establish orientation.'],['Layouts fließen mit der verfügbaren Breite.','Layouts reflow with available width.'],['Tastatur und Touch bleiben gleichwertig nutzbar.','Keyboard and touch remain usable alternatives.']],
         limit=['Die Demo zeigt lokale Navigation; sie lädt keine Projektdaten.','The demo shows local navigation; it does not load project data.'],
         source=['MDN: History API','https://developer.mozilla.org/en-US/docs/Web/API/History_API'],styles=['swiss','fluent','ibm-carbon'],principle='navigation'),
    dict(id='desktop',name=['Desktop','Desktop'],tagline=['Präzision, Tastatur, mehrere Bereiche','Precision, keyboard, multiple panes'],
         task=['Ein Projekt auswählen und seine Details neben der Liste prüfen.','Select a project and inspect its details beside the list.'],
         rules=[['Häufige Aktionen sind sichtbar und per Tastatur erreichbar.','Frequent actions are visible and keyboard accessible.'],['Auswahl und Fokus sind unterschiedliche Zustände.','Selection and focus are different states.'],['Fenster und Bereiche bleiben in ihrer Größe veränderbar.','Windows and panes remain resizable.']],
         limit=['Hier wird eine geteilte Ansicht gezeigt, keine native Fensterverwaltung.','This demonstrates a split view, not native window management.'],
         source=['KDE: Simple by default','https://develop.kde.org/hig/simple_by_default/'],styles=['fluent','gnome-adwaita','kde-breeze'],principle='navigation'),
    dict(id='smartphone',name=['Smartphone','Smartphone'],tagline=['Touch, wenig Platz, Unterbrechungen','Touch, limited space, interruptions'],
         task=['Den Projektstatus prüfen und mit einer klaren Zurück-Aktion weitergehen.','Check a project’s status and continue with a clear back action.'],
         rules=[['Eine Hauptaufgabe pro Ansicht erleichtert kurze Sitzungen.','One main task per view supports short sessions.'],['Wichtige Aktionen bleiben beschriftet und gut erreichbar.','Important actions stay labeled and reachable.'],['Tastatur, große Schrift und Querformat brauchen Raum.','On-screen keyboards, large text and landscape need space.']],
         limit=['Die ausführlichen mobilen Abläufe aller Stile stehen auf Ebene 1.','The full mobile flows for every style are available on level 1.'],
         source=['Samsung: Layout','https://developer.samsung.com/one-ui/layout/basic.html'],styles=['one-ui','apple-liquid-glass','material-expressive'],principle='adaptive'),
    dict(id='tablet',name=['Tablet & Foldable','Tablet & foldable'],tagline=['Touch trifft auf mehrere Bereiche','Touch meets multiple panes'],
         task=['Zwischen einer schmalen Ansicht und Liste plus Detail wechseln.','Switch between a narrow view and list plus detail.'],
         rules=[['Verfügbare Fensterbreite bestimmt die Zahl der Bereiche.','Available window width determines the number of panes.'],['Auswahl bleibt beim Layoutwechsel erhalten.','Selection survives a layout change.'],['Faltkanten, Stift und externe Tastatur separat prüfen.','Check folds, pen input and external keyboards separately.']],
         limit=['Die Breitenumschaltung ist schematisch; sie simuliert weder Faltkante noch Stiftdruck.','The width toggle is schematic; it does not simulate a hinge or pen pressure.'],
         source=['Android: List-detail layouts','https://developer.android.com/develop/ui/compose/layouts/adaptive/list-detail'],styles=['material-expressive','one-ui','gnome-adwaita'],principle='adaptive'),
    dict(id='watch',name=['Smartwatch','Smartwatch'],tagline=['Ein Blick, eine kurze Handlung','One glance, one brief action'],
         task=['Einen Fokusblock starten, unterbrechen und fortsetzen.','Start, pause and resume a focus session.'],
         rules=[['Zeige zuerst eine wesentliche Information.','Show one essential piece of information first.'],['Kurze Aktionen ersetzen umfangreiche Formulare.','Brief actions replace lengthy forms.'],['Krone, Sprache und Haptik ergänzen Touch gerätespezifisch.','Crown, voice and haptics complement touch on supported devices.']],
         limit=['Start und Pause sind bedienbar; Zeitablauf, Krone und Haptik werden nicht simuliert.','Start and pause work; elapsed time, crown input and haptics are not simulated.'],
         source=['Apple: Designing for watchOS','https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos/'],styles=['apple-liquid-glass','material-expressive'],principle='feedback'),
    dict(id='tv',name=['TV & Fernbedienung','TV & remote'],tagline=['Abstand und sichtbarer Fokus','Distance and visible focus'],
         task=['Mit Pfeiltasten oder den Richtungstasten eine Sendung wählen und öffnen.','Use arrow keys or the direction buttons to select and open a programme.'],
         rules=[['Fokus muss aus der Entfernung eindeutig sein.','Focus must be clear from a distance.'],['Richtungsnavigation folgt einer vorhersehbaren Ordnung.','Directional navigation follows a predictable order.'],['Eine sichtbare Zurück-Aktion führt aus den Details.','A visible back action exits details.']],
         limit=['Die Demo bildet eine Richtungstasten-Steuerung ab; echte Lesbarkeit aus Sitzentfernung muss am TV geprüft werden.','The demo models directional input; actual viewing-distance legibility needs testing on a TV.'],
         source=['Android TV: Navigation','https://developer.android.com/design/ui/tv/guides/foundations/navigation-on-tv'],styles=['flat','spatial-depth'],principle='navigation'),
    dict(id='car',name=['Auto','Car'],tagline=['Kurze Blicke, unterbrechbare Aufgaben','Brief glances, interruptible tasks'],
         task=['Zwischen Fahrt und Parken umschalten und einen Audiofavoriten wählen.','Switch between driving and parked states and choose an audio favourite.'],
         rules=[['Die Fahraufgabe bestimmt die verfügbare Aufmerksamkeit.','Driving determines the available attention.'],['Interaktionen müssen unterbrechbar bleiben.','Interactions must remain interruptible.'],['Zugelassene Plattformvorlagen bestimmen den Produktumfang.','Approved platform templates determine product scope.']],
         limit=['Schematische Web-Demo ohne Fahrzeuganbindung. Die vereinfachte Parksperre ist kein Nachweis einer Freigabe für den Fahrzeugeinsatz.','Schematic web demo without a vehicle connection. Its simplified parked-state restriction does not demonstrate approval for in-car use.'],
         source=['Google: Driving interaction principles','https://developers.google.com/cars/design/design-foundations/interaction-principles'],styles=['flat','material-expressive'],principle='disclosure'),
    dict(id='spatial',name=['Räumliche Anwendungen / XR','Spatial applications / XR'],tagline=['Raum, Komfort, Blick und Hände','Space, comfort, gaze and hands'],
         task=['Ein Inhaltsfenster und seine Bedienebene in zwei Anordnungen vergleichen.','Compare a content window and its control layer in two arrangements.'],
         rules=[['Komfort und reale Umgebung bestimmen die Platzierung.','Comfort and the real environment guide placement.'],['Inhalt und Bedienung haben erkennbare Ebenen.','Content and controls occupy recognizable layers.'],['Blick, Hände und alternative Eingaben brauchen eigene Tests.','Gaze, hands and alternative inputs need dedicated tests.']],
         limit=['Zweidimensionale Ebenenskizze; keine Simulation von Blicksteuerung, Tiefenwahrnehmung oder räumlichem Komfort.','Two-dimensional layer sketch; no simulation of gaze input, depth perception or spatial comfort.'],
         source=['Apple: Design great visionOS apps','https://developer.apple.com/videos/play/wwdc2024/10086/'],styles=['spatial-depth','apple-liquid-glass'],principle='hierarchy'),
]

PRINCIPLES = [
 ('hierarchy',['Hierarchie & Gruppierung','Hierarchy & grouping'],['Dieselben Inhalte: Abstände und Gewichtung verändern, was zuerst gelesen wird.','The same content: spacing and weight change what gets read first.'],'https://carbondesignsystem.com/elements/typography/style-strategies/','Carbon · Typography'),
 ('disclosure',['Schrittweise Offenlegung','Progressive disclosure'],['Häufige Eingaben bleiben sichtbar. Weitere Einstellungen erscheinen bei Bedarf und behalten ihre Werte.','Frequent inputs stay visible. Further settings appear on demand and retain their values.'],'https://develop.kde.org/hig/simple_by_default/','KDE · Simple by default'),
 ('feedback',['Rückmeldung & Fehlerbehebung','Feedback & recovery'],['Einen Speicherversuch mit Ladezustand, Fehler, erneutem Versuch und Rückgängig durchspielen.','Try saving through loading, failure, retry and undo.'],'https://www.nngroup.com/articles/ten-usability-heuristics/','Nielsen · Usability heuristics'),
 ('navigation',['Orientierung & Navigation','Orientation & navigation'],['Eine Auswahl in zwei Navigationsmustern verfolgen: eigene Detailseite oder Liste und Detail nebeneinander.','Follow one selection across two navigation patterns: a separate detail view or list and detail side by side.'],'https://developer.android.com/develop/ui/compose/layouts/adaptive/list-detail','Android · List-detail'),
 ('adaptive',['Anpassung & Eingabe','Adaptation & input'],['Layoutbreite und Bediengröße unabhängig ändern. Die Aufgabe und die Auswahl bleiben erhalten.','Change layout width and control size independently. The task and selection remain intact.'],'https://developer.gnome.org/hig/guidelines/pointer-touch.html','GNOME · Pointer & touch'),
 ('inclusive',['Inklusive Darstellung','Inclusive presentation'],['Schrift vergrößern, Kontrast erhöhen und lange Texte einschalten. Beobachte, wie die Inhalte neu umbrechen.','Enlarge text, increase contrast and enable long labels. Watch content reflow.'],'https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html','W3C · Resize text'),
]


def header(lang, count):
    en=lang=='en'
    def t(de,en_text):return en_text if en else de
    levels=[('styles','01',t('Stile & Designsprachen','Styles & design languages'),t(f'{count} visuelle Referenzen · Welche Form passt?',f'{count} visual references · Which form fits?')),
            ('principles','02',t('Gestaltungs- & Bedienprinzipien','Design & interaction principles'),t('6 interaktive Beispiele · Wie funktioniert es?','6 interactive examples · How does it work?')),
            ('contexts','03',t('Geräte & Nutzungskontexte','Devices & contexts'),t('8 Kontexte · Wo und womit wird es benutzt?','8 contexts · Where and how is it used?'))]
    nav=''.join(f'<a href="?level={key}#{key}" data-level-link="{key}"><span>{num}</span><strong>{name}</strong><small>{desc}</small></a>' for key,num,name,desc in levels)
    return f'''<header class="ex-intro wrap"><span class="eyebrow">{t('Drei Ebenen einer Oberfläche','Three levels of an interface')}</span>
<h1>{t('Aussehen. Bedienung. Kontext.','Appearance. Interaction. Context.')}</h1>
<p>{t('Wähle eine Designsprache, prüfe ihre Bedienung und passe sie an die Nutzung an. Drei getrennte Entscheidungen, die zusammen eine brauchbare Oberfläche ergeben.','Choose a design language, examine its interaction and adapt it to its context. Three separate decisions that together make a usable interface.')}</p></header>
<nav class="ex-levels wrap" aria-label="{t('Die drei Ebenen','The three levels')}">{nav}</nav>'''


def principles(lang):
    en=lang=='en'; i=int(en)
    def t(de,eng):return eng if en else de
    def btn(action,label,extra=''):return f'<button type="button" data-lab-action="{action}" {extra}>{label}</button>'
    def check(key,label):return f'<label class="ex-check"><input type="checkbox" data-lab-option="{key}"> {label}</label>'
    def select(key,label,opts):return f'<label>{label}<select data-lab-option="{key}">'+''.join(f'<option value="{v}">{n}</option>' for v,n in opts)+'</select></label>'
    labs={
      'hierarchy':f'''<div class="ex-controls">{select('grouping',t('Anordnung','Arrangement'),[('grouped',t('Gruppiert','Grouped')),('flat',t('Gleich gewichtet','Equal weight'))])}</div>
<div class="ex-demo ex-grouping" data-grouping="grouped"><h4>{t('Projektübersicht','Project overview')}</h4><div class="ex-group"><strong>Nexus</strong><span>{t('Aktiv','Active')}</span><small>{t('Zuletzt geändert: heute','Last updated: today')}</small></div><div class="ex-group"><strong>Balance Ally</strong><span>{t('Pausiert','Paused')}</span><small>{t('Zuletzt geändert: gestern','Last updated: yesterday')}</small></div></div>''',
      'disclosure':f'''<form class="ex-demo ex-disclosure" data-lab-form="disclosure"><label>{t('Projektname','Project name')}<input name="project" value="Nexus" required maxlength="100"></label>
<details><summary>{t('Erweiterte Einstellungen','Advanced settings')}</summary><label>{t('Verantwortlich','Owner')}<input name="owner" value="Alex" maxlength="100"></label><label>{t('Erinnerung','Reminder')}<select name="reminder"><option value="weekly">{t('Wöchentlich','Weekly')}</option><option value="never">{t('Keine','None')}</option></select></label></details>
<button type="submit">{t('Einstellungen übernehmen','Apply settings')}</button><p class="ex-status" role="status" data-disclosure-status>{t('Änderungen gelten nur für dieses Beispiel.','Changes apply only to this example.')}</p></form>''',
      'feedback':f'''<div class="ex-controls">{check('fail',t('Nächsten Versuch scheitern lassen','Fail the next attempt'))}</div><div class="ex-demo"><p><strong>Nexus</strong> · <span data-feedback-value>{t('Entwurf','Draft')}</span></p><p class="ex-status" role="status" data-feedback-status>{t('Bereit zum Speichern.','Ready to save.')}</p><div class="ex-controls">{btn('save',t('Speichern','Save'))}{btn('retry',t('Erneut versuchen','Retry'),'hidden')}{btn('undo',t('Rückgängig','Undo'),'hidden')}{btn('reset-feedback',t('Zurücksetzen','Reset'))}</div></div>''',
      'navigation':f'''<div class="ex-controls">{select('navigation',t('Muster','Pattern'),[('split',t('Liste + Detail','List + detail')),('pages',t('Eigene Detailansicht','Separate detail view'))])}</div><div class="ex-demo" data-navigation-demo></div>''',
      'adaptive':f'''<div class="ex-controls">{select('width',t('Platz','Space'),[('wide',t('Breit / zwei Bereiche','Wide / two panes')),('narrow',t('Schmal / eine Ansicht','Narrow / one view'))])}{select('input',t('Bediengröße','Control size'),[('touch',t('Touch · großzügig','Touch · generous')),('pointer',t('Maus / Tastatur · kompakt','Mouse / keyboard · compact'))])}</div><div class="ex-demo ex-adaptive" data-width="wide" data-input="touch" data-adaptive-demo></div><p class="ex-note">{t('Alle Varianten unterstützen Tastatur und Touch. Die Umschaltung ändert die Gestaltung, nicht die verfügbare Eingabe.','Every variant supports keyboard and touch. The toggle changes presentation, not available input.')}</p>''',
      'inclusive':f'''<div class="ex-controls">{check('large',t('Schrift 200%','Text 200%'))}{check('contrast',t('Hoher Kontrast','High contrast'))}{check('long',t('Lange Texte','Long labels'))}{check('motion',t('Bewegung reduzieren','Reduce motion'))}</div><div class="ex-demo ex-inclusive" data-inclusive-demo><div class="ex-pulse" aria-hidden="true"></div><h4 data-inclusive-title>Nexus</h4><p data-inclusive-copy>{t('Ein gemeinsamer Ort für Projekte.','A shared home for projects.')}</p><button type="button" data-lab-action="inclusive-confirm">{t('Auswahl bestätigen','Confirm selection')}</button><p role="status" data-inclusive-status></p></div><p class="ex-note">{t('Systemseitig reduzierte Bewegung hat Vorrang. Diese Schalter veranschaulichen einzelne Anforderungen und ersetzen keine vollständige Barrierefreiheitsprüfung.','The system’s reduced-motion preference takes priority. These controls illustrate individual requirements and do not replace a full accessibility audit.')}</p>'''
    }
    cards=''
    for num,(key,name,desc,url,source) in enumerate(PRINCIPLES,1):
        cards+=f'''<article class="ex-lab" id="principle-{key}" data-principle="{key}"><header><span class="eyebrow">{num:02d} / 06</span><h3>{name[i]}</h3><p>{desc[i]}</p></header>{labs[key]}<p class="ex-source"><a href="{url}">{source}</a></p></article>'''
    return f'''<section class="ex-panel wrap" id="principles" data-level="principles" aria-labelledby="principles-title"><div class="ex-section-head"><span class="eyebrow">02 · {t('Bedienung','Interaction')}</span><h2 id="principles-title" tabindex="-1">{t('Prinzipien zum Ausprobieren','Principles to try')}</h2><p>{t('Sechs kleine Versuche machen die Wirkung einer Entscheidung sichtbar. Alle Änderungen bleiben in dieser Sitzung und lassen sich durch Neuladen zurücksetzen.','Six small experiments make the effect of a decision visible. All changes stay in this session and reset when you reload.')}</p><noscript>{t('Für die interaktiven Versuche bitte JavaScript aktivieren. Beschreibungen und Quellen bleiben lesbar.','Enable JavaScript for the interactive experiments. Descriptions and sources remain readable.')}</noscript></div><div class="ex-labs">{cards}</div></section>'''


def contexts(lang, styles):
    en=lang=='en';i=int(en)
    def t(de,eng):return eng if en else de
    cards=''
    family_anchors={}
    for slug,style in styles.items():
        family_anchors.setdefault(style['family'], 'family-'+slug)
    for num,c in enumerate(CONTEXTS,1):
        links=' · '.join(f'<a href="?level=styles#{family_anchors[styles[s]["family"]]}" data-style-link="{s}">{esc(styles[s]["name"])}</a>' for s in c['styles'])
        rules=''.join(f'<li>{esc(r[i])}</li>' for r in c['rules'])
        cards+=f'''<article class="ex-context" id="context-{c['id']}" data-context="{c['id']}"><header><span class="eyebrow">{num:02d} / 08 · {esc(c['tagline'][i])}</span><h3>{esc(c['name'][i])}</h3><p>{esc(c['task'][i])}</p></header><div class="ex-context-demo" data-context-demo="{c['id']}"></div><ul>{rules}</ul><p class="ex-note">{esc(c['limit'][i])}</p><details><summary>{t('Verbindungen zu den anderen Ebenen','Connections to the other levels')}</summary><p>{t('Mögliche visuelle Referenzen, keine Plattformfreigabe:','Possible visual references, not platform approval:')} {links}.</p><p><a href="?level=principles#principle-{c['principle']}">{t('Passendes Bedienprinzip ausprobieren','Try the related interaction principle')}</a></p></details><p class="ex-source"><a href="{c['source'][1]}">{esc(c['source'][0])}</a></p></article>'''
    return f'''<section class="ex-panel wrap" id="contexts" data-level="contexts" aria-labelledby="contexts-title"><div class="ex-section-head"><span class="eyebrow">03 · {t('Nutzung','Use')}</span><h2 id="contexts-title" tabindex="-1">{t('Ein Kontext verändert die Aufgabe','Context changes the task')}</h2><p>{t('Geräteform, Aufmerksamkeit und Eingabe bestimmen, wie viel eine Oberfläche auf einmal leisten soll. Die Beispiele zeigen jeweils eine passende Aufgabe in einer neutralen Gestaltung.','Device form, attention and input determine how much an interface should do at once. Each example shows a suitable task in a neutral visual language.')}</p><nav class="ex-context-index" aria-label="{t('Kontexte','Contexts')}">'''+''.join(f'<a href="#context-{c["id"]}">{esc(c["name"][i])}</a>' for c in CONTEXTS)+f'''</nav><noscript>{t('JavaScript aktiviert die schematischen Bedienbeispiele.','JavaScript enables the schematic interaction examples.')}</noscript></div><div class="ex-contexts">{cards}</div></section>'''


def assets(lang):
    return (ROOT/'catalog.css').read_text(), (ROOT/'catalog.js').read_text()

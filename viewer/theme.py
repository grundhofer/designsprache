"""Shared viewer theme; reference demos keep their own scoped palettes."""
from pathlib import Path

PALETTES = {
    'light': {
        'ground':'#E9EBE6', 'surface':'#F5F7F2', 'surface-2':'#FCFDFA',
        'ink':'#171A17', 'ink-2':'#565D58', 'ink-3':'#5C645D',
        'rule':'#C6CBC2', 'rule-soft':'#DCE0D8',
        'accent':'#1E4A45', 'accent-ink':'#FCFDFA', 'accent-soft':'#D9E5E1', 'brass':'#806128',
    },
    'dark': {
        'ground':'#1C211E', 'surface':'#29312C', 'surface-2':'#343E37',
        'ink':'#EEF1EB', 'ink-2':'#BDC7BD', 'ink-3':'#AAB8AD',
        'rule':'#64736A', 'rule-soft':'#46544B',
        'accent':'#8AD0BE', 'accent-ink':'#14251F', 'accent-soft':'#30483D', 'brass':'#D6BB80',
    },
}


def css():
    def values(mode):
        shadow = ('0 1px 2px rgba(23,26,23,.05), 0 8px 24px -12px rgba(23,26,23,.18)'
                  if mode == 'light' else '0 1px 2px rgba(0,0,0,.25), 0 10px 30px -14px rgba(0,0,0,.45)')
        return ''.join('--'+key+':'+value+';' for key,value in PALETTES[mode].items())+'--shadow:'+shadow+';color-scheme:'+mode+';'
    return (':root {'+values('light')+'}\n'
            '@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {'+values('dark')+'} }\n'
            ':root[data-theme="dark"] {'+values('dark')+'}\n'+'''
.theme-switch { display:flex; flex-wrap:wrap; border:1px solid var(--ink-3); background:var(--surface); }
.theme-switch button { min-height:44px; padding:10px 13px; border:0; background:transparent;
  color:var(--ink); font:500 13px var(--f-mono); cursor:pointer; }
.theme-switch button[aria-pressed="true"] { background:var(--accent); color:var(--accent-ink); }
.theme-switch button:focus-visible { outline:3px solid var(--accent); outline-offset:3px; position:relative; z-index:1; }
@media (forced-colors:active) {
  .theme-switch { border-color:ButtonText; }
  .theme-switch button[aria-pressed="true"] { color:HighlightText; background:Highlight; forced-color-adjust:none; }
}
''')


def script():
    return '<script id="theme-controller">\n'+(Path(__file__).parent/'theme.js').read_text()+'\n</script>\n'


def controls(lang=None):
    labels={'de':('System','Hell','Dunkel'),'en':('System','Light','Dark')}
    title={'de':'Darstellung','en':'Appearance'}.get(lang,'Darstellung / Appearance')
    buttons=[]
    for index,mode in enumerate(('system','light','dark')):
        text=labels[lang][index] if lang else ''.join(
            f'<span lang="{locale}" data-language-content="{locale}">{labels[locale][index]}</span>'
            for locale in ('de','en'))
        buttons.append(f'<button type="button" data-theme-choice="{mode}" aria-pressed="false">{text}</button>')
    return f'<div class="theme-switch" data-theme-controls role="group" aria-label="{title}" hidden>'+''.join(buttons)+'</div>'

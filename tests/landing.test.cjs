const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

const page=fs.readFileSync(path.join(__dirname,'..','docs','index.html'),'utf8');
const script=page.match(/<script>([\s\S]*?)<\/script>/)[1];
function mount({languages=['de-DE'], language='de-DE', saved=null, query='', blocked=false}={}) {
  const buttons=['de','en'].map(lang=>({dataset:{languageSwitch:lang},attrs:{},listeners:{},
    setAttribute(key,value){this.attrs[key]=value;},addEventListener(key,fn){this.listeners[key]=fn;}}));
  const links=['de','en'].map(hreflang=>({hreflang,listeners:{},addEventListener(key,fn){this.listeners[key]=fn;}}));
  const root={dataset:{},lang:'de'}, group={hidden:true}, metas=new Map();
  let ready, stored=saved, writes=0;
  const document={documentElement:root,addEventListener(key,fn){ready=fn;},
    querySelectorAll:selector=>selector==='[data-language-switch]'?buttons:links,
    querySelector:selector=>{if(selector==='.language-switch')return group;if(!metas.has(selector))metas.set(selector,{});return metas.get(selector);}};
  const window={location:new URL('https://example.com/designsprache/'+query),
    localStorage:{getItem(){if(blocked)throw Error('blocked');return stored;},setItem(key,value){if(blocked)throw Error('blocked');stored=value;writes++;}},
    history:{replaceState(a,b,url){window.location=new URL(url);}}};
  vm.runInNewContext(script,{document,window,navigator:{languages,language},URL,URLSearchParams});
  const beforeReady=root.lang;
  ready();
  return {root,buttons,links,group,metas,document,window,beforeReady,get saved(){return stored;},get writes(){return writes;}};
}

test('home: detect regional browser preferences before rendering; default to English',()=>{
  for(const [languages,expected] of [[['de-AT'],'de'],[['en-GB','de'],'en'],[['fr-FR','de-CH'],'de'],[['ja-JP'],'en'],[['DE-de'],'de']]) {
    const m=mount({languages});assert.equal(m.beforeReady,expected);assert.equal(m.root.dataset.language,expected);
    assert.equal(m.buttons.find(b=>b.dataset.languageSwitch===expected).attrs['aria-pressed'],'true');
    assert.equal(m.writes,0,'automatic detection must not overwrite a later browser preference');
  }
  assert.equal(mount({languages:[],language:'en-US'}).root.lang,'en');
});
test('home: explicit URL overrides saved choice, which overrides browser preference',()=>{
  assert.equal(mount({saved:'en'}).root.lang,'en');
  assert.equal(mount({saved:'en',query:'?lang=de'}).root.lang,'de');
  assert.equal(mount({saved:'invalid',query:'?lang=xx',languages:['fr']}).root.lang,'en');
});
test('home: manual switch updates content language, metadata, selection, URL and preference',()=>{
  const m=mount({query:'?from=readme#intro'});
  assert.equal(m.group.hidden,false);
  m.buttons[1].listeners.click();
  assert.equal(m.root.lang,'en');assert.equal(m.saved,'en');
  assert.equal(m.buttons[0].attrs['aria-pressed'],'false');assert.equal(m.buttons[1].attrs['aria-pressed'],'true');
  assert.equal(m.window.location.search,'?from=readme&lang=en');assert.equal(m.window.location.hash,'#intro');
  assert.match(m.document.title,/Styles, principles, contexts/);
  assert.match(m.metas.get('meta[name="description"]').content,/37 styles/);
  m.buttons[0].listeners.click();assert.equal(m.saved,'de');assert.match(m.document.title,/Stile, Prinzipien/);
});
test('home: unavailable storage does not prevent detection or manual switching',()=>{
  const m=mount({blocked:true});assert.equal(m.root.lang,'de');
  assert.doesNotThrow(()=>m.buttons[1].listeners.click());assert.equal(m.root.lang,'en');
});
test('home: catalog links remember the explicitly chosen language and work without JavaScript',()=>{
  const m=mount();m.links[1].listeners.click();assert.equal(m.saved,'en');
  assert.ok(page.includes('href="de/" hreflang="de"'));assert.ok(page.includes('href="en/" hreflang="en"'));
  assert.ok(!/<a[^>]*class="door"[^>]*\bhidden\b/.test(page));
  assert.ok(page.includes(':root[data-language="de"] [data-language-content="en"]'));
  assert.ok(page.includes(':root[data-language="en"] [data-language-content="de"]'));
});

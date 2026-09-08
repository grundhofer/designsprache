// Test the shipped state machines, markup and event wiring without browser automation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

for (const lang of ['de', 'en']) {
  const page = fs.readFileSync(path.join(__dirname, '..', 'docs', lang, 'index.html'), 'utf8');
  const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
  const start = script.indexOf('  /* ---------- Explorer: pure state');
  const dom = script.indexOf('  /* ---------- Explorer: DOM wiring');
  const end = script.indexOf('\n})();', dom);
  const model = script.slice(start, dom);
  function context() {
    const ctx = vm.createContext({ LANG:lang,
      esc: value => String(value).replace(/[&<>"]/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' })[c]),
    });
    vm.runInContext(model, ctx);
    return ctx;
  }
  test(`${lang}: save failure preserves draft, retry succeeds and undo restores it`, () => {
    const c=context(); const initial=c.newFeedbackState();
    let state=c.feedbackTransition(initial,'save');
    assert.equal(state.phase,'saving'); assert.equal(initial.phase,'idle');
    state=c.feedbackTransition(state,'failure');
    assert.equal(state.saved,false); assert.equal(state.phase,'error');
    state=c.feedbackTransition(state,'retry');
    state=c.feedbackTransition(state,'success');
    assert.equal(state.saved,true); assert.equal(state.phase,'saved');
    state=c.feedbackTransition(state,'undo');
    assert.equal(state.saved,false); assert.equal(state.phase,'undone');
    state=c.feedbackTransition(c.feedbackTransition(state,'save'),'reset');
    assert.equal(c.feedbackTransition(state,'success').saved,false,'late completion cannot save after reset');
  });
  test(`${lang}: selection survives back navigation and a change of pane count`, () => {
    const c=context(); let state=c.exNavState('pages');
    assert.ok(!c.exNavigationMarkup(state).includes('ex-project-detail'));
    state=c.exNavTransition(state,'open',2);
    assert.ok(c.exNavigationMarkup(state).includes(lang==='de'?'Pausiert':'Paused'));
    state=c.exNavTransition(state,'mode','split');
    assert.equal(state.selected,2); assert.ok(c.exNavigationMarkup(state).includes('ex-split'));
    state=c.exNavTransition(state,'back');
    state=c.exNavTransition(state,'mode','pages');
    assert.equal(state.selected,2); assert.ok(!state.detail);
    assert.equal(c.exNavTransition(state,'open',99).selected,2);
    assert.equal(c.exNavTransition(state,'open',NaN).selected,2);
  });
  test(`${lang}: watch pause/resume and reset are isolated from other contexts`, () => {
    const c=context(); let watch=c.newContextState('watch'), tv=c.newContextState('tv');
    watch=c.exContextTransition(watch,'watch-toggle'); assert.equal(watch.watch,'running');
    watch=c.exContextTransition(watch,'watch-toggle'); assert.equal(watch.watch,'paused');
    watch=c.exContextTransition(watch,'watch-toggle'); assert.equal(watch.watch,'running');
    watch=c.exContextTransition(watch,'watch-reset'); assert.equal(watch.watch,'idle');
    assert.equal(tv.watch,'idle');
  });
  test(`${lang}: TV navigation stays in bounds and preserves selection after details`, () => {
    const c=context(); let state=c.newContextState('tv');
    state=c.exContextTransition(state,'tv-move',-1); assert.equal(state.selected,0);
    state=c.exContextTransition(state,'tv-move',3); assert.equal(state.selected,2);
    const markup=c.exContextMarkup(state);
    assert.equal((markup.match(/tabindex="0"/g)||[]).length,1);
    state=c.exContextTransition(state,'tv-open',2);
    assert.equal(c.exContextTransition(state,'tv-move',-1).selected,2);
    assert.ok(!c.exContextMarkup(state).includes('data-tv-index'));
    state=c.exContextTransition(state,'tv-back'); assert.equal(state.selected,2);
    assert.ok(c.exContextMarkup(state).includes('data-tv-index="2"'));
  });
  test(`${lang}: car input requires parking and user text is escaped`, () => {
    const c=context(); let state=c.newContextState('car');
    assert.equal(c.exContextTransition(state,'custom','Example').custom,'');
    assert.ok(!c.exContextMarkup(state).includes('<form'));
    state=c.exContextTransition(state,'park');
    state=c.exContextTransition(state,'custom',' <img src=x onerror="bad()"> ');
    const markup=c.exContextMarkup(state);
    assert.ok(markup.includes('&lt;img')); assert.ok(!markup.includes('<img'));
    assert.ok(markup.includes('&quot;bad()&quot;'));
    state=c.exContextTransition(state,'park');
    assert.ok(!c.exContextMarkup(state).includes('<form'));
    state=c.exContextTransition(state,'audio',2); assert.equal(state.selected,2);
  });
  test(`${lang}: all eight contexts render meaningful tasks and all six labs exist`, () => {
    const c=context();
    for (const id of ['web','desktop','smartphone','tablet','watch','tv','car','spatial']) {
      const markup=c.exContextMarkup(c.newContextState(id));
      assert.ok(markup.includes('<button'),id); assert.ok(!markup.includes('undefined'),id);
      if(lang==='en')assert.ok(!/\b(und|nicht|Oberfläche|Einträge|Haltbarkeit)\b/.test(markup),id);
      assert.ok(page.includes(`id="context-${id}"`),id);
      assert.ok(!markup.includes('onClick='));
    }
    for (const id of ['hierarchy','disclosure','feedback','navigation','adaptive','inclusive']) {
      assert.ok(page.includes(`id="principle-${id}"`));
    }
    assert.equal(c.exLevel('unknown'),'styles');
    assert.equal(c.exLevel('principles'),'principles');
    assert.equal(c.exLevel('<script>'),'styles');
  });

  function mount() {
    const c=context();
    class Node {
      constructor(dataset={}) { this.dataset=dataset; this.attributes={}; this.children=new Map(); this.listeners={}; this.hidden=false; this.checked=false; this.value=''; this.innerHTML=''; this.textContent=''; this.classList={toggle(){},add(){},remove(){}}; }
      addEventListener(event,callback) { this.listeners[event]=callback; }
      setAttribute(key,value) { this.attributes[key]=value; }
      removeAttribute(key) { delete this.attributes[key]; }
      querySelector(selector) { if(!this.children.has(selector))this.children.set(selector,new Node());return this.children.get(selector); }
      focus() { this.focused=true; }
      scrollIntoView() { this.scrolled=true; }
      closest() { return null; }
    }
    const panels=['styles','principles','contexts'].map(level=>new Node({level}));
    const nav=panels.map(panel=>new Node({levelLink:panel.dataset.level}));
    const links=['de','en'].map(locale=>({href:`https://example.com/${locale}/`}));
    const ids=new Map(),selectors=new Map();
    const byId=id=>{if(!ids.has(id))ids.set(id,new Node());return ids.get(id);};
    const query=selector=>{if(!selectors.has(selector))selectors.set(selector,new Node());return selectors.get(selector);};
    const demos=['web','desktop','smartphone','tablet','watch','tv','car','spatial'].map(id=>{const n=query(`[data-context-demo="${id}"]`);n.dataset.contextDemo=id;return n;});
    c.document={documentElement:{dataset:{}},getElementById:byId,querySelector:query,querySelectorAll:selector=>({
      '[data-level]':panels,'[data-level-link]':nav,'.tb-lang a':links,'[data-context-demo]':demos,'[data-style-link]':[],
    })[selector]||[]};
    const location=new URL('https://example.com/de/?level=principles&view=mobile&screen=detail#principle-feedback');
    c.window={location,addEventListener(){},history:{pushState(a,b,url){c.window.location=new URL(url);}}};
    c.URL=URL;c.URLSearchParams=URLSearchParams;c.schedule=()=>{};c.setCatalogView=()=>{};
    c.sheet={hidden:true};c.FI={hidden:true};c.close=()=>{c.sheet.hidden=true;};c.closeFinder=()=>{c.FI.hidden=true;};
    const timers=new Map();let timerId=0;
    c.setTimeout=callback=>{timers.set(++timerId,callback);return timerId;};c.clearTimeout=id=>timers.delete(id);
    vm.runInContext(script.slice(dom,end),c);
    return {c,Node,panels,nav,links,ids,selectors,query,byId,timers};
  }
  test(`${lang}: mounted explorer routes preserve language, view and screen; back closes overlays`, () => {
    const m=mount();
    assert.deepEqual(m.panels.map(p=>p.hidden),[true,false,true]);
    assert.ok(m.links.every(link=>link.href.includes('level=principles') && link.href.includes('screen=detail')));
    m.nav[2].listeners.click({button:0,preventDefault(){}});
    assert.deepEqual(m.panels.map(p=>p.hidden),[true,true,false]);
    assert.ok(m.c.window.location.href.includes('view=mobile'));
    assert.equal(m.byId('contexts-title').focused,true);
    m.c.sheet.hidden=false;m.c.FI.hidden=false;
    m.c.window.location=new URL('https://example.com/de/?level=principles');m.c.exRestoreRoute();
    assert.equal(m.c.sheet.hidden,true);assert.equal(m.c.FI.hidden,true);
    assert.deepEqual(m.panels.map(p=>p.hidden),[true,false,true]);
  });
  test(`${lang}: mounted feedback cancels pending save when reset and consumes failure once`, () => {
    const m=mount(), lab=m.query('[data-principle="feedback"]');lab.dataset.principle='feedback';
    const fail=lab.querySelector('[data-lab-option="fail"]');fail.checked=true;
    function click(action) {
      const button=new m.Node({labAction:action});
      m.byId('principles').listeners.click({target:{closest:selector=>selector==='[data-principle]'?lab:selector==='[data-lab-action]'?button:null}});
    }
    click('save'); assert.equal(m.c.exFeedback.phase,'saving');
    click('reset-feedback'); assert.equal(m.c.exFeedback.phase,'idle');assert.equal(fail.checked,false);
    // Only the unrelated initial-anchor timer may remain.
    for(const callback of m.timers.values())callback();
    assert.equal(m.c.exFeedback.saved,false);
    m.timers.clear();fail.checked=true;click('save');
    for(const callback of m.timers.values())callback();m.timers.clear();
    assert.equal(m.c.exFeedback.phase,'error');assert.equal(fail.checked,false);
    click('retry');for(const callback of m.timers.values())callback();m.timers.clear();
    assert.equal(m.c.exFeedback.phase,'saved');click('undo');
    assert.equal(m.c.exFeedback.saved,false);
    assert.equal(lab.querySelector('[data-lab-action="save"]').focused,true);
  });
  test(`${lang}: mounted disclosure applies current hidden advanced values as text`, () => {
    const m=mount(); const form=m.query('[data-lab-form="disclosure"]');
    form.elements={project:{value:'<img src=x>'},owner:{value:'Alex'},reminder:{selectedOptions:[{textContent:lang==='de'?'Wöchentlich':'Weekly'}]}};
    form.listeners.submit({preventDefault(){},currentTarget:form});
    assert.ok(form.querySelector('[data-disclosure-status]').textContent.includes('<img src=x>'));
    assert.equal(form.querySelector('[data-disclosure-status]').innerHTML,'');
  });
}

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');
const routes=['index.html','de/index.html','en/index.html'];
const pages=routes.map(route=>fs.readFileSync(path.join(__dirname,'..','docs',route),'utf8'));
const scripts=pages.map(page=>page.match(/<script id="theme-controller">([\s\S]*?)<\/script>/)[1]);
const KEY='designsprache.theme';
function mount({storage=new Map(),blocked=false,script=scripts[0]}={}) {
  let ready;
  const events={};
  const root={hidden:false,dataset:{explorerLevel:'principles',language:'de'}};
  const group={hidden:true};
  const buttons=['system','light','dark'].map(themeChoice=>({dataset:{themeChoice},attrs:{},listeners:{},
    setAttribute(key,value){this.attrs[key]=value;},addEventListener(key,fn){this.listeners[key]=fn;}}));
  const document={documentElement:root,addEventListener(key,fn){ready=fn;},querySelectorAll:selector=>({
    '[data-theme-choice]':buttons,'[data-theme-controls]':[group],
  })[selector]||[]};
  const window={localStorage:{
    getItem(key){if(blocked)throw Error('blocked');return storage.get(key)||null;},
    setItem(key,value){if(blocked)throw Error('blocked');storage.set(key,value);},
  },addEventListener(key,fn){events[key]=fn;}};
  vm.runInNewContext(script,{document,window});
  const initial=root.dataset.theme;
  ready();
  return {root,group,buttons,storage,events,window,initial};
}

test('theme: every page loads the same controller in the head and has three accessible choices',()=>{
  for(let i=0;i<pages.length;i++) {
    assert.equal(scripts[i],scripts[0]);
    assert.ok(pages[i].indexOf('id="theme-controller"')<pages[i].indexOf('</head>'));
    for(const choice of ['system','light','dark']) assert.equal((pages[i].match(new RegExp(`data-theme-choice="${choice}"`,'g'))||[]).length,1);
    assert.ok(pages[i].includes('data-theme-controls role="group"'));
    assert.ok(pages[i].includes('@media (prefers-color-scheme: dark) { :root:not([data-theme="light"])'));
    assert.ok(pages[i].includes(':root[data-theme="dark"]'));
  }
});
test('theme: default and invalid stored values use the live CSS system preference',()=>{
  for(const saved of [null,'system','invalid','<script>']) {
    const m=mount({storage:new Map(saved?[[KEY,saved]]:[])});
    assert.equal(m.initial,'system');assert.equal(m.buttons[0].attrs['aria-pressed'],'true');
    assert.equal(m.group.hidden,false);
  }
});
test('theme: manual choices survive page and language changes, and System restores automatic behavior',()=>{
  const storage=new Map([['designsprache.language','de']]);
  const home=mount({storage});home.buttons[2].listeners.click();assert.equal(home.root.dataset.theme,'dark');
  const catalog=mount({storage,script:scripts[2]});assert.equal(catalog.initial,'dark');
  catalog.buttons[1].listeners.click();assert.equal(catalog.root.dataset.theme,'light');
  assert.equal(catalog.buttons[2].attrs['aria-pressed'],'false');
  const de=mount({storage,script:scripts[1]});assert.equal(de.initial,'light');
  de.buttons[0].listeners.click();assert.equal(storage.get(KEY),'system');
  assert.equal(de.root.dataset.theme,'system');assert.equal(storage.get('designsprache.language'),'de');
  assert.equal(de.root.dataset.explorerLevel,'principles');assert.equal(de.root.hidden,false);
});
test('theme: switching stays usable when local storage is blocked',()=>{
  const m=mount({blocked:true});assert.equal(m.initial,'system');
  for(const [index,mode] of ['system','light','dark'].entries()) {
    assert.doesNotThrow(()=>m.buttons[index].listeners.click());assert.equal(m.root.dataset.theme,mode);
  }
  m.events.pageshow({persisted:true});assert.equal(m.root.dataset.theme,'dark');
});
test('theme: open tabs and back-forward cached pages synchronize without rewriting preferences',()=>{
  const m=mount();
  m.events.storage({key:KEY,newValue:'light',storageArea:m.window.localStorage});assert.equal(m.root.dataset.theme,'light');
  assert.equal(m.storage.has(KEY),false);
  m.events.storage({key:'designsprache.language',newValue:'en'});assert.equal(m.root.dataset.theme,'light');
  m.events.storage({key:KEY,newValue:'dark',storageArea:{}});assert.equal(m.root.dataset.theme,'light');
  m.events.storage({key:null,newValue:null});assert.equal(m.root.dataset.theme,'system');
  m.storage.set(KEY,'dark');m.events.pageshow({persisted:true});assert.equal(m.root.dataset.theme,'dark');
});

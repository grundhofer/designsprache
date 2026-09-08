// Exercise the actual generated finder functions without a browser or npm dependencies.
// Run `python3 build.py` first, then `node --test tests/finder.test.cjs`.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

for (const lang of ['de', 'en']) {
  const page = fs.readFileSync(path.join(__dirname, '..', 'docs', lang, 'index.html'), 'utf8');
  const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];
  const data = JSON.parse(page.match(/<script type="application\/json" id="payload">([\s\S]*?)<\/script>/)[1]);
  function section(start, end) {
    const from = script.indexOf(start);
    const to = script.indexOf(end, from);
    assert.ok(from >= 0 && to > from, `Missing script section: ${start}`);
    return script.slice(from, to);
  }
  function finder(answers, order = Object.keys(data)) {
    const context = vm.createContext({
      DATA: data, LANG: lang, SITE: 'https://grundhofer.github.io/designsprache', ANS: answers, order,
      fiRes: { querySelectorAll: () => [] }, fiQuiz: {}, fiAgain: {}, FI: {},
      document: { getElementById: () => ({ focus() {} }) }, fitFinder() {}, setTimeout() {},
      mountMobileResults() {},
    });
    vm.runInContext([
      section('  var FT = ', '  var ANS = '),
      section('  var f1 = ', '  /* ---------- Bewertung'),
      section('  function esc(s)', '  function open(i)'),
      section('  function rate(slug)', '  /* ---------- Fragebogen'),
      section('  function showResults()', '  fiRes.addEventListener'),
      section('var MOBILE_DATA = ', '  /* ---------- Mobile reference: catalog integration'),
    ].join('\n'), context);
    return context;
  }

  test(`${lang}: complete generated JavaScript parses`, () => {
    assert.doesNotThrow(() => new vm.Script(script));
  });

  test(`${lang}: no preference behaves exactly like an unanswered preference`, () => {
    const base = finder({ use: 'dev-tool' });
    const any = finder({ use: 'dev-tool', mode: 'any', density: 'any', longevity: 'any', recognition: 'any' });
    for (const slug of Object.keys(data)) {
      assert.equal(any.rate(slug).pct, base.rate(slug).pct, slug);
      assert.equal(JSON.stringify(any.rate(slug).why), JSON.stringify(base.rate(slug).why), slug);
    }
  });

  test(`${lang}: matches beat explicit mismatches and stay within percentage bounds`, () => {
    const context = finder({ use: 'civic', mode: 'light', a11y: '5', effort: '1' });
    assert.ok(context.rate('civic-service').pct > context.rate('vaporwave').pct);
    for (const slug of Object.keys(data)) {
      assert.ok(context.rate(slug).pct >= 0 && context.rate(slug).pct <= 100);
    }
    assert.equal(finder({}).rate('swiss').pct, 0);
  });

  test(`${lang}: marker search, family filtering and empty results use generated search data`, () => {
    const decode = text => text.replace(/&(?:amp|quot|lt|gt|#x27);/g, entity => ({
      '&amp;': '&', '&quot;': '"', '&lt;': '<', '&gt;': '>', '&#x27;': "'",
    })[entity]);
    const plates = [...page.matchAll(/<article class="k-plate"([\s\S]*?)>/g)].map(match => ({
      dataset: Object.fromEntries([...match[1].matchAll(/data-(slug|family|search)="([^"]*)"/g)]
        .map(attribute => [attribute[1], decode(attribute[2])])),
    }));
    const families = [...new Set(plates.map(p => p.dataset.family))].map(family => ({
      querySelectorAll: () => plates.filter(p => p.dataset.family === family),
    }));
    const context = vm.createContext({
      q: { value: 'steps(1,end)' }, fam: '*', tally: {}, empty: {}, schedule() {},
      document: { querySelectorAll: () => families },
    });
    vm.runInContext(section('  function apply()', '  chips.forEach'), context);
    context.apply();
    assert.equal(plates.find(p => p.dataset.slug === 'terminal-mono').hidden, false);
    context.q.value = 'this-marker-does-not-exist';
    context.apply();
    assert.ok(plates.every(p => p.hidden));
    assert.equal(context.empty.hidden, false);
    context.q.value = '';
    context.fam = data['e-paper'].family;
    context.apply();
    assert.equal(plates.filter(p => !p.hidden).length, 2);
    assert.equal(context.empty.hidden, true);
  });

  test(`${lang}: all reasons, including late mismatches, reach the result card`, () => {
    const d = data.swiss;
    const context = finder({
      use: d.finder.fits[0], tone: [d.finder.tone[0]],
      mode: d.finder.mode === 'light' ? 'dark' : 'light',
      density: String(d.scores.density), longevity: String(d.scores.longevity),
      recognition: String(d.scores.recognition), effort: '5', a11y: '5', platform: ['web'],
    }, ['swiss']);
    const reasons = context.rate('swiss').why;
    assert.ok(reasons.length > 6);
    assert.ok(reasons.some(reason => !reason.ok));
    context.showResults();
    for (const reason of reasons) assert.ok(context.fiRes.innerHTML.includes(context.esc(reason.t)), reason.t);
  });

  test(`${lang}: every prompt contains eight parameters, palette, risks and product checks`, () => {
    const context = finder({});
    for (const [slug, d] of Object.entries(data)) {
      const prompt = context.buildPrompt(slug);
      for (const value of Object.values(d.params)) assert.ok(prompt.includes(value), `${slug}: ${value}`);
      for (const color of d.palette) assert.ok(prompt.includes(color), `${slug}: ${color}`);
      for (const risk of d.risks) assert.ok(prompt.includes(risk), `${slug}: missing risk`);
      assert.ok(prompt.includes(lang === 'de' ? 'Prüfung im Produkt' : 'Product checks'));
      assert.ok(prompt.includes(`/designsprache/${lang}/`));
      assert.ok(!prompt.includes('undefined'));
    }
  });

  test(`${lang}: every style renders three mobile screens with intact reference data`, () => {
    const context = finder({});
    for (const slug of Object.keys(data)) {
      for (const screen of ['list', 'detail', 'new']) {
        const markup = context.mobileMarkup(slug, context.newMobileState(screen));
        assert.ok(markup.includes(`m-${slug}`));
        assert.ok(!markup.includes('undefined'));
        assert.ok(!markup.includes('scale('));
        if (screen === 'list') {
          for (const name of ['Nexus', 'Autowrite Studio', 'Balance Ally']) assert.ok(markup.includes(name));
          assert.ok(markup.includes('m-count">12'));
        }
        if (screen === 'new') assert.ok(markup.includes('name="name" required'));
      }
    }
  });

  test(`${lang}: mobile creation, import, search and reset preserve isolated demo state`, () => {
    const context = finder({});
    const state = context.newMobileState('new');
    assert.equal(context.mobileAdd(state, ['   '], 'active', ''), false);
    assert.equal(state.projects.length, 3);
    assert.equal(context.mobileAdd(state, [' <img src=x onerror=alert(1)> '], 'paused', '<script>bad</script>'), true);
    assert.equal(state.screen, 'detail');
    assert.equal(state.projects[state.selected].status, 'paused');
    const detail = context.mobileMarkup('swiss', state);
    assert.ok(detail.includes('&lt;img'));
    assert.ok(!detail.includes('<script>'));
    assert.equal(context.mobileAdd(state, ['Atlas', '', 'Studio'], 'unexpected', ''), true);
    assert.equal(state.screen, 'list');
    assert.equal(state.projects.length, 6);
    state.query = 'atlas';
    assert.equal(context.mobileRows(state).count, 1);
    state.query = 'no-such-project';
    assert.equal(context.mobileRows(state).count, 0);
    assert.equal(context.newMobileState().projects.length, 3);
  });

  test(`${lang}: mobile prompt adds the actual style adaptation only in mobile view`, () => {
    const context = finder({});
    for (const slug of Object.keys(data)) {
      context.mobileMode = false;
      assert.ok(!context.buildPrompt(slug).includes(context.MT.promptText));
      context.mobileMode = true;
      const prompt = context.buildPrompt(slug);
      assert.ok(prompt.includes(context.MT.promptText));
      assert.ok(prompt.includes(context.MOBILE_DATA[slug].note));
    }
  });

  test(`${lang}: mobile view wiring synchronizes controls, finder, exports and language links`, () => {
    const context = finder({});
    const element = (dataset = {}) => ({
      dataset, hidden: false, style: {}, children: [], attributes: {}, listeners: {},
      setAttribute(key, value) { this.attributes[key] = value; },
      addEventListener(type, callback) { this.listeners[type] = callback; },
      appendChild(child) { this.children.push(child); }, focus() { this.focused = true; },
    });
    const previews = Object.keys(data).map(slug => element({ mobileSlug: slug }));
    const views = ['desktop', 'mobile', 'desktop', 'mobile'].map(view => element({ view }));
    const selects = [element(), element()], states = [element(), element()], intro = element();
    const links = ['de', 'en'].map(locale => ({ href: `https://example.com/${locale}/` }));
    const ids = Object.fromEntries(['mobile-sheet', 'mobile-help', 'mobile-note', 'mobile-reset', 'mobile-palette-label', 'mobile-values'].map(id => [id, element()]));
    const resultHost = element(), resultFrame = element({ demo: 'swiss' });
    resultFrame.querySelector = () => resultHost;
    let removedPrompt = false;
    const source = { firstElementChild: { cloneNode: () => ({ querySelectorAll: () => [] }) } };
    context.document = {
      getElementById: id => ids[id], documentElement: { dataset: {} },
      querySelector: () => source,
      querySelectorAll: selector => ({
        '.mobile-preview': previews, '[data-view]': views, '[data-mobile-screen]': selects,
        '.mobile-states, .mobile-intro': [...states, intro], '[data-view-controls]': [element()], '.tb-lang a': links,
      })[selector] || [],
    };
    context.fiRes = { querySelectorAll: selector => selector === '.fi-frame' ? [resultFrame]
      : [{ remove() { removedPrompt = true; } }] };
    context.sHost = { parentElement: element() }; context.sCap = element(); context.cur = -1;
    context.schedule = () => {};
    context.URL = URL; context.URLSearchParams = URLSearchParams;
    context.window = { location: { href: 'https://example.com/de/?view=mobile&screen=detail', search: '?view=mobile&screen=detail' },
      history: { replaceState(a, b, href) { context.window.location.href = href; } } };
    vm.runInContext(section('  /* ---------- Mobile reference: catalog integration', '\n})();'), context);
    assert.equal(context.mobileMode, true);
    assert.equal(context.mobileScreen, 'detail');
    assert.equal(intro.hidden, false);
    assert.ok(previews.every(p => p.innerHTML.startsWith('<div inert>') && p.innerHTML.includes('Nexus')));
    assert.equal(resultHost.style.transform, 'none');
    assert.ok(resultHost.innerHTML.includes('m-swiss'));
    assert.ok(links.every(link => link.href.includes('view=mobile')));
    assert.equal(removedPrompt, true);
    views[0].listeners.click();
    assert.equal(context.mobileMode, false);
    assert.equal(intro.hidden, true);
    assert.equal(resultHost.style.width, '');
    assert.equal(resultHost.children.length, 1);
    assert.ok(links.every(link => !link.href.includes('view=')));
    assert.equal(views[2].attributes['aria-pressed'], 'true');
    selects[0].value = 'new'; selects[0].listeners.change();
    assert.equal(context.mobileMode, true);
    assert.equal(selects[1].value, 'new');
    assert.ok(context.window.location.href.includes('screen=new'));
    context.setCatalogView('mobile', '<script>', false);
    assert.equal(context.mobileScreen, 'list');
  });
}

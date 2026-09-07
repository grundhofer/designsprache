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
    });
    vm.runInContext([
      section('  var FT = ', '  var ANS = '),
      section('  var f1 = ', '  /* ---------- Bewertung'),
      section('  function esc(s)', '  function open(i)'),
      section('  function rate(slug)', '  /* ---------- Fragebogen'),
      section('  function showResults()', '  fiRes.addEventListener'),
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
}

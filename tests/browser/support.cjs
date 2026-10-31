// Shared fixtures for the rendered browser checks.
//
// Every test gets a page that
// - aborts and records any request to a host other than the local test server,
// - records console errors, uncaught page errors, failed requests and HTTP errors,
// and fails in teardown if any of these occurred.
const { test: base, expect } = require('@playwright/test');
const { AxeBuilder } = require('@axe-core/playwright');

const LANGS = ['de', 'en'];
const WIDTHS = [390, 1280];
const SCHEMES = ['light', 'dark'];

// Rendered text the checks rely on, per language.
const T = {
  de: { finder: 'Stil finden', copied: 'Kopiert', intro: 'Verwende die folgende Designsprache' },
  en: { finder: 'Find a style', copied: 'Copied', intro: 'Use the following design language' },
};

// Every axe finding fails the run, whatever its impact, unless it is listed
// here with a reason and recorded in REVIEW.md. Keep this list empty unless a
// finding is an intended property of the catalog.
const DOCUMENTED_AXE = [
  // { rule: 'color-contrast', target: /\.style-neumorphism/, reason: '...' },
];

const test = base.extend({
  guard: [async ({ page, baseURL }, use) => {
    const own = new URL(baseURL).host;
    const problems = { foreign: [], console: [], pageerror: [], failed: [], http: [] };
    await page.route('**/*', (route) => {
      const url = new URL(route.request().url());
      if (url.host !== own) {
        problems.foreign.push(url.href);
        return route.abort('blockedbyclient');
      }
      return route.continue();
    });
    page.on('console', (msg) => { if (msg.type() === 'error') problems.console.push(msg.text()); });
    page.on('pageerror', (err) => problems.pageerror.push(String(err)));
    page.on('requestfailed', (req) => {
      if (new URL(req.url()).host === own) problems.failed.push(`${req.url()} ${req.failure()?.errorText}`);
    });
    page.on('response', (res) => { if (res.status() >= 400) problems.http.push(`${res.status()} ${res.url()}`); });
    await use(problems);
    expect(problems.foreign, 'requests to foreign hosts').toEqual([]);
    expect(problems.console, 'console errors').toEqual([]);
    expect(problems.pageerror, 'uncaught page errors').toEqual([]);
    expect(problems.failed, 'failed requests').toEqual([]);
    expect(problems.http, 'HTTP error responses').toEqual([]);
  }, { auto: true }],
});

// Navigate and wait until the page, its scripts and its web fonts are settled.
async function load(page, path) {
  await page.goto(path, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready.then(() => undefined));
}

async function expectNoHorizontalScroll(page, label = '') {
  const m = await page.evaluate(() => ({
    scroll: document.documentElement.scrollWidth,
    client: document.documentElement.clientWidth,
    body: document.body.scrollWidth,
  }));
  expect(m.scroll, `page scrolls sideways ${label}`).toBeLessThanOrEqual(m.client);
  expect(m.body, `body wider than viewport ${label}`).toBeLessThanOrEqual(m.client);
}

// Dialogs are their own scroll containers; they must not scroll sideways either.
async function expectNoSidewaysIn(page, selector) {
  const m = await page.locator(selector).evaluate((el) => ({ scroll: el.scrollWidth, client: el.clientWidth }));
  expect(m.scroll, `${selector} scrolls sideways`).toBeLessThanOrEqual(m.client);
}

// Runs axe with the WCAG 2.x A/AA rule sets plus best practices. Undocumented
// findings of any impact fail; documented ones are attached as annotations.
async function axe(page, label, { include } = {}) {
  let builder = new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice']);
  if (include) builder = builder.include(include);
  const result = await builder.analyze();
  const undocumented = [];
  const documented = [];
  for (const v of result.violations) {
    for (const node of v.nodes) {
      const target = node.target.join(' ');
      const entry = `${v.impact} ${v.id} ${target}`;
      const known = DOCUMENTED_AXE.some((d) => d.rule === v.id && d.target.test(target));
      (known ? documented : undocumented).push(entry);
    }
  }
  expect(undocumented, `axe findings (${label})`).toEqual([]);
  if (documented.length) {
    test.info().annotations.push({ type: 'axe (documented)', description: `${label}: ${documented.join('; ')}` });
  }
  return documented;
}

async function activeInfo(page) {
  return page.evaluate(() => {
    const a = document.activeElement;
    return {
      id: a ? a.id : '',
      tag: a ? a.tagName : '',
      text: a ? (a.textContent || '').trim().slice(0, 60) : '',
      dialog: a && a.closest('dialog') ? a.closest('dialog').id : null,
      body: a === document.body || a === document.documentElement || a === null,
    };
  });
}

module.exports = { test, expect, LANGS, WIDTHS, SCHEMES, T, load, expectNoHorizontalScroll, expectNoSidewaysIn, axe, activeInfo };

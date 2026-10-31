// Enlarged text: browser zoom (200 % and 400 %), the browser's default font
// size setting, and the WCAG 1.4.12 text-spacing overrides.
const { test, expect, LANGS, load, expectNoHorizontalScroll, expectNoSidewaysIn } = require('./support.cjs');

const ZOOMS = [
  // A 1280 x 900 window at 200 % zoom lays out like 640 x 450 CSS pixels at 2x.
  { name: 'zoom 200%', viewport: { width: 640, height: 450 }, deviceScaleFactor: 2 },
  // 400 % of 1280 px is the 320 px reflow width of WCAG 1.4.10.
  { name: 'zoom 400%', viewport: { width: 320, height: 256 }, deviceScaleFactor: 4 },
];

for (const lang of LANGS) {
  for (const z of ZOOMS) {
    test.describe(`${lang} ${z.name}`, () => {
      test.use({ viewport: z.viewport, deviceScaleFactor: z.deviceScaleFactor });
      for (const path of ['/?lang=' + lang, `/${lang}/`, `/${lang}/?level=principles`, `/${lang}/?level=contexts`]) {
        test(`no sideways scrolling ${path}`, async ({ page }) => {
          await load(page, path);
          await expectNoHorizontalScroll(page, path);
        });
      }
      test('finder and fact sheet reflow', async ({ page }) => {
        await load(page, `/${lang}/`);
        await page.locator('#fi-open').click();
        await page.locator('.fi-opt').first().click();
        await page.locator('#fi-go').click();
        await expect(page.locator('#fi-results .fi-card')).toHaveCount(5);
        await expectNoHorizontalScroll(page, 'finder');
        await expectNoSidewaysIn(page, '#finder');
        await page.locator('#fi-results [data-go3]').first().click();
        await expect(page.locator('#s-name')).toBeFocused();
        await expectNoSidewaysIn(page, '#sheet');
      });
    });
  }
}

for (const lang of LANGS) {
  test(`${lang}: text spacing overrides (WCAG 1.4.12) cause no sideways scrolling`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 900 });
    await load(page, `/${lang}/`);
    await page.addStyleTag({ content: `
      *:not(.demo-host *):not(.sheet-host *):not(.fi-host *) {
        line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important;
      }
      p:not(.demo-host *) { margin-bottom: 2em !important; }` });
    await expectNoHorizontalScroll(page, 'text spacing');
  });

  // Chromium's "font size" setting (Settings > Appearance). The catalog sizes
  // its text in px, so this setting does not enlarge it; browser zoom does.
  // The check records the measured sizes and guards against overflow; the
  // finding is listed in REVIEW.md.
  test(`${lang}: default font size setting at 32 px`, async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    const cdp = await page.context().newCDPSession(page);
    await cdp.send('Page.enable');
    await cdp.send('Page.setFontSizes', { fontSizes: { standard: 32, fixed: 26 } });
    for (const path of ['/?lang=' + lang, `/${lang}/`]) {
      await load(page, path);
      const sizes = await page.evaluate(() => {
        const px = (sel) => {
          const el = document.querySelector(sel);
          return el ? parseFloat(getComputedStyle(el).fontSize) : null;
        };
        return { root: px('html'), body: px('body'), p: px('main p') };
      });
      test.info().annotations.push({ type: 'font-size', description: `${path} ${JSON.stringify(sizes)}` });
      expect(sizes.root, 'Page.setFontSizes did not apply').toBe(32);
      await expectNoHorizontalScroll(page, `${path} font size 32`);
    }
  });
}

// Every shipped page in both languages, at 390 and 1280 px, light and dark:
// no sideways scrolling, no foreign requests, no console errors (guard
// fixture) and no serious axe findings.
const { test, expect, LANGS, WIDTHS, SCHEMES, load, expectNoHorizontalScroll, axe } = require('./support.cjs');

const PAGES = {
  de: ['/?lang=de', '/de/', '/de/?level=principles', '/de/?level=contexts', '/de/impressum/'],
  en: ['/?lang=en', '/en/', '/en/?level=principles', '/en/?level=contexts', '/en/legal-notice/'],
};

for (const lang of LANGS) {
  for (const width of WIDTHS) {
    for (const scheme of SCHEMES) {
      test.describe(`${lang} ${width}px ${scheme}`, () => {
        test.use({ viewport: { width, height: 900 }, colorScheme: scheme });
        for (const path of PAGES[lang]) {
          test(`page ${path}`, async ({ page }) => {
            await load(page, path);
            await expect(page.locator('html')).toHaveAttribute('lang', lang);
            // System theme: the stored preference is absent, CSS follows the emulated scheme.
            await expect(page.locator('html')).toHaveAttribute('data-theme', 'system');
            const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
            const [r, g, b] = bg.match(/\d+/g).map(Number);
            const luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
            if (scheme === 'dark') expect(luminance, `dark body background ${bg}`).toBeLessThan(0.35);
            else expect(luminance, `light body background ${bg}`).toBeGreaterThan(0.65);
            await expectNoHorizontalScroll(page, path);
            // Web fonts: none may have failed to load.
            const failedFonts = await page.evaluate(() =>
              [...document.fonts].filter((f) => f.status === 'error').map((f) => f.family));
            expect(failedFonts).toEqual([]);
            await axe(page, `${path} ${width}px ${scheme}`);
          });
        }
      });
    }
  }
}

// The explicit Light/Dark choice overrides the system setting and survives a
// reload and a change of language.
for (const lang of LANGS) {
  test(`${lang}: manual theme choice overrides the system and persists`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await load(page, `/${lang}/`);
    const html = page.locator('html');
    await page.locator('.topbar [data-theme-choice="dark"]').click();
    await expect(html).toHaveAttribute('data-theme', 'dark');
    await expect(page.locator('.topbar [data-theme-choice="dark"]')).toHaveAttribute('aria-pressed', 'true');
    const darkBg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    await page.reload();
    await expect(html).toHaveAttribute('data-theme', 'dark');
    const other = lang === 'de' ? 'en' : 'de';
    await page.locator(`.tb-lang a[hreflang="${other}"]`).click();
    await expect(html).toHaveAttribute('lang', other);
    await expect(html).toHaveAttribute('data-theme', 'dark');
    expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).toBe(darkBg);
    await page.locator('.topbar [data-theme-choice="system"]').click();
    await expect(html).toHaveAttribute('data-theme', 'system');
    expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).not.toBe(darkBg);
  });
}

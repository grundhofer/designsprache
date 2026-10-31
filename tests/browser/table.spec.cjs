// Sortable table headers by keyboard and the other fact-sheet entry points.
const { test, expect, LANGS, WIDTHS, load, expectNoHorizontalScroll, expectNoSidewaysIn, axe } = require('./support.cjs');

async function column(page, col) {
  return page.evaluate((c) =>
    [...document.querySelectorAll('#tbody tr')].map((r) => Number(r.cells[c].dataset.v)), col);
}

for (const lang of LANGS) {
  for (const width of WIDTHS) {
    test.describe(`${lang} ${width}px`, () => {
      test.use({ viewport: { width, height: 900 } });

      test('sortable headers respond to Enter and Space with a visible focus', async ({ page }) => {
        await load(page, `/${lang}/`);
        const heads = page.locator('th.sortable');
        await expect(heads).toHaveCount(3);
        for (let i = 0; i < 3; i++) {
          const th = heads.nth(i);
          const col = Number(await th.getAttribute('data-col'));
          const btn = th.locator('button');
          // Reach the header button with the keyboard from the control before it.
          await btn.evaluate((el) => {
            const all = [...document.querySelectorAll('button, a[href], select, input, [tabindex="0"]')]
              .filter((x) => !x.disabled && x.offsetParent !== null);
            all[all.indexOf(el) - 1].focus();
          });
          await page.keyboard.press('Tab');
          await expect(btn).toBeFocused();
          const outline = await btn.evaluate((el) => {
            const s = getComputedStyle(el);
            return { visible: el.matches(':focus-visible'), style: s.outlineStyle, width: parseFloat(s.outlineWidth) };
          });
          expect(outline.visible).toBe(true);
          expect(outline.style).not.toBe('none');
          expect(outline.width).toBeGreaterThan(0);

          await page.keyboard.press('Enter');
          await expect(th).toHaveAttribute('aria-sort', 'descending');
          let v = await column(page, col);
          expect(v).toEqual([...v].sort((a, b) => b - a));
          await expect(btn).toBeFocused();

          await page.keyboard.press('Space');
          await expect(th).toHaveAttribute('aria-sort', 'ascending');
          v = await column(page, col);
          expect(v).toEqual([...v].sort((a, b) => a - b));
          // Only one column is sorted at a time.
          await expect(page.locator('th.sortable[aria-sort="none"]')).toHaveCount(2);
        }
        await expectNoHorizontalScroll(page, 'table');
      });

      test('fact sheet from table row and gallery: focus, arrows, Escape, focus return', async ({ page }) => {
        await load(page, `/${lang}/`);
        const row = page.locator('#tbody .row-open').nth(2);
        await row.focus();
        await page.keyboard.press('Enter');
        const sheet = page.locator('#sheet');
        await expect(sheet).toHaveJSProperty('open', true);
        await expect(page.locator('#s-name')).toBeFocused();
        await expect(page.locator('#s-name')).toHaveText((await row.textContent()).trim());
        await axe(page, `fact sheet ${lang} ${width}px`, { include: '#sheet' });
        await expectNoHorizontalScroll(page, 'fact sheet');
        await expectNoSidewaysIn(page, '#sheet');
        const before = await page.locator('#s-name').textContent();
        await page.keyboard.press('ArrowRight');
        await expect(page.locator('#s-name')).not.toHaveText(before);
        await page.keyboard.press('ArrowLeft');
        await expect(page.locator('#s-name')).toHaveText(before);
        await page.keyboard.press('Escape');
        await expect(sheet).toHaveJSProperty('open', false);
        await expect(row).toBeFocused();
        expect(await page.evaluate(() => document.body.style.overflow)).toBe('');

        const plate = page.locator('.plate-open').first();
        await plate.focus();
        await page.keyboard.press('Enter');
        await expect(page.locator('#s-name')).toBeFocused();
        await page.locator('#s-close').click();
        await expect(sheet).toHaveJSProperty('open', false);
        await expect(plate).toBeFocused();
      });
    });
  }
}

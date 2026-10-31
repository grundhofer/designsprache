// Finder dialog and the fact sheet opened from its results, by keyboard.
const { test, expect, LANGS, WIDTHS, T, load, expectNoHorizontalScroll, expectNoSidewaysIn, axe, activeInfo } = require('./support.cjs');

for (const lang of LANGS) {
  for (const width of WIDTHS) {
    test.describe(`${lang} ${width}px`, () => {
      test.use({ viewport: { width, height: 900 } });

      test('finder: first focus, inert background, Tab/Shift-Tab wrap, Escape, focus return', async ({ page }) => {
        await load(page, `/${lang}/`);
        const opener = page.locator('#fi-open');
        await expect(opener).toHaveText(T[lang].finder);
        await opener.focus();
        await page.keyboard.press('Enter');
        const finder = page.locator('#finder');
        await expect(finder).toHaveJSProperty('open', true);
        expect((await activeInfo(page)).id, 'first focus').toBe('fi-close');
        // The background is inert while the modal dialog is open.
        // Background controls cannot take focus, even programmatically.
        expect(await page.locator('.plate-open').first().evaluate((el) => {
          el.focus();
          return document.activeElement === el;
        }), 'background control took focus').toBe(false);
        // The background is outside the accessibility tree (inert).
        const cdp = await page.context().newCDPSession(page);
        const { nodes } = await cdp.send('Accessibility.getFullAXTree');
        const exposed = nodes.filter((n) => !n.ignored).map((n) => n.name && n.name.value).filter(Boolean);
        expect(exposed).toContain(await page.locator('#fi-title').textContent());
        expect(exposed).not.toContain((await page.locator('.plate-open').first().textContent()).trim());
        expect(exposed).not.toContain((await page.locator('#tbody .row-open').first().textContent()).trim());
        expect((await activeInfo(page)).id).toBe('fi-close');

        // Count the reachable controls, then Tab once around the whole dialog.
        const stops = await page.evaluate(() =>
          [...document.querySelectorAll('#finder button, #finder [tabindex="0"]')]
            .filter((el) => !el.disabled && el.offsetParent !== null).length);
        expect(stops).toBeGreaterThan(10);
        const forward = [];
        for (let i = 0; i < stops + 3; i++) {
          await page.keyboard.press('Tab');
          forward.push(await activeInfo(page));
        }
        // Focus never lands on background content. Chromium passes through the
        // document (the browser UI in a headed window) and the scrollable
        // dialog itself before wrapping; both are native modal behavior.
        for (const step of forward) {
          expect(step.dialog === 'finder' || step.body, `Tab reached background: ${JSON.stringify(step)}`).toBe(true);
        }
        const firstAgain = forward.findIndex((s, i) => i > 0 && s.id === 'fi-close');
        expect(firstAgain, `Tab did not wrap to the close button: ${JSON.stringify(forward.slice(-5))}`).toBeGreaterThan(stops - 2);

        // Shift-Tab from the first control wraps to the last one.
        await page.locator('#fi-close').focus();
        const backward = [];
        for (let i = 0; i < 4; i++) {
          await page.keyboard.press('Shift+Tab');
          backward.push(await activeInfo(page));
        }
        for (const step of backward) {
          expect(step.dialog === 'finder' || step.body, `Shift-Tab reached background: ${JSON.stringify(step)}`).toBe(true);
        }
        const lastText = await page.evaluate(() => {
          const all = [...document.querySelectorAll('#finder button')].filter((el) => !el.disabled && el.offsetParent !== null);
          return all[all.length - 1].textContent.trim();
        });
        expect(backward.map((s) => s.text), 'Shift-Tab wrap').toContain(lastText);

        await page.keyboard.press('Escape');
        await expect(finder).toHaveJSProperty('open', false);
        await expect(finder).toBeHidden();
        await expect(opener).toBeFocused();
        expect(await page.evaluate(() => document.body.style.overflow)).toBe('');
      });

      test('finder: results, fact sheet from results, Escape order, clipboard', async ({ page, context, baseURL }) => {
        await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: baseURL });
        await load(page, `/${lang}/`);
        await page.locator('#fi-open').click();
        await expect(page.locator('#fi-close')).toBeFocused();
        // Answer the first question by keyboard: Tab to it, Enter selects.
        await page.keyboard.press('Tab');
        const first = page.locator('.fi-opt').first();
        await expect(first).toBeFocused();
        await page.keyboard.press('Enter');
        await expect(first).toHaveAttribute('aria-pressed', 'true');
        const go = page.locator('#fi-go');
        await expect(go).toBeEnabled();
        await go.focus();
        await page.keyboard.press('Enter');

        await expect(page.locator('#fi-result-title')).toBeFocused();
        const cards = page.locator('#fi-results .fi-card');
        await expect(cards).toHaveCount(5);
        await expect(page.locator('#fi-again')).toBeVisible();
        await expectNoHorizontalScroll(page, 'finder results');
        await expectNoSidewaysIn(page, '#finder');
        await axe(page, `finder results ${lang} ${width}px`, { include: '#finder' });

        // Open the first recommended fact sheet from the results.
        const name = (await cards.first().locator('h3').textContent()).trim();
        const openBtn = cards.first().locator('[data-go3]');
        await openBtn.focus();
        await page.keyboard.press('Enter');
        const sheet = page.locator('#sheet');
        await expect(sheet).toHaveJSProperty('open', true);
        await expect(page.locator('#s-name')).toBeFocused();
        await expect(page.locator('#s-name')).toHaveText(name);
        await expectNoHorizontalScroll(page, 'fact sheet');
        await expectNoSidewaysIn(page, '#sheet');
        await axe(page, `fact sheet over finder ${lang} ${width}px`, { include: '#sheet' });

        // Escape closes only the sheet; results stay; focus returns to the button.
        await page.keyboard.press('Escape');
        await expect(sheet).toHaveJSProperty('open', false);
        await expect(page.locator('#finder')).toHaveJSProperty('open', true);
        await expect(cards).toHaveCount(5);
        await expect(openBtn).toBeFocused();

        // Copy as prompt: with clipboard permission the prompt lands in the clipboard.
        const copy = cards.first().locator('[data-copy]');
        await copy.click();
        await expect(copy).toHaveText(T[lang].copied);
        const clip = await page.evaluate(() => navigator.clipboard.readText());
        expect(clip.startsWith(T[lang].intro), clip.slice(0, 80)).toBe(true);
        expect(clip).toContain(name);
        await expect(page.locator('#fi-results .fi-hint')).toHaveCount(0);

        // Show text toggles the same prompt inline.
        const show = cards.first().locator('[data-show]');
        await show.click();
        await expect(cards.first().locator('.fi-pre')).toHaveText(clip);
        await show.click();
        await expect(cards.first().locator('.fi-pre')).toHaveCount(0);

        // Escape now closes the finder and returns focus to its opener.
        await page.locator('#fi-result-title').focus();
        await page.keyboard.press('Escape');
        await expect(page.locator('#finder')).toHaveJSProperty('open', false);
        await expect(page.locator('#fi-open')).toBeFocused();
      });
    });
  }
}

// Clipboard blocked: the prompt is shown and selected for manual copying.
for (const lang of LANGS) {
  test(`${lang}: blocked clipboard falls back to a selected text box`, async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'clipboard', {
        configurable: true,
        value: { writeText: () => Promise.reject(new DOMException('blocked', 'NotAllowedError')) },
      });
      document.execCommand = () => false;
    });
    await load(page, `/${lang}/`);
    await page.locator('#fi-open').click();
    await page.locator('.fi-opt').first().click();
    await page.locator('#fi-go').click();
    const card = page.locator('#fi-results .fi-card').first();
    await card.locator('[data-copy]').click();
    const box = card.locator('.fi-pre[data-hint]');
    await expect(box).toBeVisible();
    await expect(card.locator('.fi-hint')).toBeVisible();
    const selected = await page.evaluate(() => String(window.getSelection()));
    expect(selected.startsWith(T[lang].intro)).toBe(true);
    expect(selected).toBe(await box.textContent());
  });
}

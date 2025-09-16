const { test, expect } = require('@playwright/test');

test('get a joke button works', async ({ page }) => {
  await page.goto('https://jokes-app-ew5b.onrender.com/');
  // Check the button is visible
  await expect(page.locator('#joke-btn')).toBeVisible();
  // Click the button
  await page.click('#joke-btn');
  // Wait for joke paragraph to have non-empty text
  const jokeEl = page.locator('#joke');
  await expect(jokeEl).not.toHaveText('');
  // Check that some text was actually returned
  const jokeText = await jokeEl.innerText();
  expect(jokeText.trim()).not.toBe('');
});
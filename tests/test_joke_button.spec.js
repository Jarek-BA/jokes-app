const { test, expect } = require('@playwright/test');

test('get a joke button works', async ({ page }) => {
  // Go to your deployed app

const baseURL = process.env.BASE_URL || 'http://127.0.0.1:8000';
await page.goto(baseURL, { timeout: 15000, waitUntil: 'domcontentloaded' });

  // Wait explicitly for the button to appear
  const jokeButton = page.locator('#joke-btn');
  await expect(jokeButton).toBeVisible({ timeout: 15000 });

  // Click the button
  await jokeButton.click();

  // Wait for joke paragraph to have non-empty text
  const jokeEl = page.locator('#joke');
  await expect(jokeEl).not.toHaveText('', { timeout: 15000 });

  // Check that some text was actually returned
  const jokeText = await jokeEl.innerText();
  expect(jokeText.trim()).not.toBe('');
});

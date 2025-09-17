const { test, expect } = require('@playwright/test');

test('get a joke button works', async ({ page }) => {
  // Go to your deployed app

  await page.goto('https://jokes-app-ew5b.onrender.com/', { timeout: 15000, waitUntil: 'domcontentloaded' });
  // await page.goto('http://127.0.0.1:8000/', { timeout: 15000, waitUntil: 'domcontentloaded' }); // to run locally

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

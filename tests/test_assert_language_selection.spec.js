import { test, expect } from '@playwright/test';

// Map dropdown labels to franc language codes
const languageMap = {
  English: 'eng',
  Czech: 'ces',
  German: 'deu',
  Spanish: 'spa',
  French: 'fra',
  Portuguese: 'por'
};

for (const [langLabel, langCode] of Object.entries(languageMap)) {
  test(`Joke is displayed in ${langLabel}`, async ({ page }) => {
    // ✅ dynamic import so it works in CommonJS tests
    const { franc } = await import('franc');

    // Go to the app
    await page.goto('https://jokes-app-ew5b.onrender.com/', {
      timeout: 15000,
      waitUntil: 'domcontentloaded'
    });
    // For local runs:
    // await page.goto('http://127.0.0.1:8000/', { timeout: 15000, waitUntil: 'domcontentloaded' });

    // Select the language in dropdown
    const dropdown = page.locator('#language-selection');
    await expect(dropdown).toBeVisible();
    await dropdown.selectOption(langLabel);

    // Click "Get Joke"
    const jokeButton = page.locator('#joke-btn');
    await expect(jokeButton).toBeVisible();
    await jokeButton.click();

    // Wait for the joke display
    const jokeDisplay = page.locator('#joke');
    await expect(jokeDisplay).toBeVisible({ timeout: 15000 });

    // Extract joke text
    const jokeText = await jokeDisplay.textContent();
    expect(jokeText).not.toBeNull();
    expect(jokeText?.trim().length).toBeGreaterThan(0);

    // Detect language
    const detectedLang = franc(jokeText || '');

    // Debug log
    console.log(
      `Selected: ${langLabel}, Expected: ${langCode}, Detected: ${detectedLang}, Joke: ${jokeText}`
    );

    // Assert match
    expect(detectedLang).toBe(langCode);
  });
}

const { test, expect } = require('@playwright/test');

test('Language selection dropdown shows supported languages', async ({ page }) => {

const baseURL = process.env.BASE_URL || 'http://127.0.0.1:8000';
await page.goto(baseURL, { timeout: 15000, waitUntil: 'domcontentloaded' });

  // Locate the dropdown
  const dropdown = page.locator('#language-selection'); // ✅ match actual ID in HTML

  // Ensure dropdown is visible
  await expect(dropdown).toBeVisible();

  // Get all option values
  const options = dropdown.locator('option');
  const optionValues = await options.allTextContents();

  // Define expected languages
  const expectedLanguages = [
    'English',
    'Czech',
    'German',
    'Spanish',
    'French',
    'Portuguese'
  ];

  // Assert each expected language is present
  for (const lang of expectedLanguages) {
    expect(optionValues).toContain(lang);
  }
});

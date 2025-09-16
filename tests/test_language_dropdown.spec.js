const { test, expect } = require('@playwright/test');

test('Language selection dropdown shows supported languages', async ({ page }) => {
  await page.goto('https://jokes-app-ew5b.onrender.com/'); // Replace with your app URL

  // Locate the dropdown (update selector as needed)
  const dropdown = page.locator('#language-select'); // Replace with the actual selector

  // Click to open the dropdown if needed
  await dropdown.click();

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
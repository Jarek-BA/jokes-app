import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8000', // fallback for local dev
    headless: true,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 10000,
    navigationTimeout: 15000,
  },
  reporter: [
    ['junit', { outputFile: 'tests/test-results/junit.xml' }],
    // You can add 'list', 'html', or Testomat reporter here if needed
  ],
});

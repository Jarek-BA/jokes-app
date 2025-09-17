import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['list'],
    ['junit', { outputFile: 'tests/test-results/results.xml' }],
  ],
});

import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['junit', { outputFile: 'tests/test-results/junit.xml' }],
    // other reporters if needed
  ],
});
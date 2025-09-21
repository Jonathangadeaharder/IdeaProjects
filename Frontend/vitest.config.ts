import { defineConfig, configDefaults } from 'vitest/config'
import react from '@vitejs/plugin-react-swc'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react() as any],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    testTimeout: 30000, // 30 second timeout for all tests
    watch: false, // Disable watch mode by default
    exclude: [
      ...configDefaults.exclude,
      // Exclude Puppeteer E2E test that has its own runner in tests/e2e
      'src/test/auth-flow.test.ts',
    ],
    coverage: {
      reporter: ['text', 'json', 'html'],
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
})
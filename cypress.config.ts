import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    
    env: {
      // Backend API URL for E2E tests
      apiUrl: 'http://localhost:8000',
      // Test user credentials
      testUserEmail: 'cypress-test@example.com',
      testUserPassword: 'CypressTest123!',
    },

    setupNodeEvents(on, config) {
      // Add any plugins here
      
      // Task for seeding test data
      on('task', {
        seedDatabase() {
          // Implementation to seed test database
          return null
        },
        
        cleanDatabase() {
          // Implementation to clean test database
          return null
        }
      })
    },
  },

  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    specPattern: 'cypress/component/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.ts',
  },
})

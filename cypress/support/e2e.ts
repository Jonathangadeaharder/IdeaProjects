// ***********************************************************
// This file is processed and loaded automatically before your test files.
// You can read more here: https://on.cypress.io/configuration
// ***********************************************************

import './commands'

// Cypress configuration
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // on uncaught exceptions from the application under test
  if (err.message.includes('ResizeObserver')) {
    return false
  }
  return true
})

// Global test hooks
beforeEach(() => {
  // Intercept API calls if needed
  cy.intercept('GET', '/api/health', { 
    statusCode: 200, 
    body: { status: 'healthy' } 
  }).as('healthCheck')
})

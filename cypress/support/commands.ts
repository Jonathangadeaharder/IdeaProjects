// ***********************************************
// Custom commands for LangPlug E2E testing
// ***********************************************

/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Login command for authenticated test flows
       */
      login(email?: string, password?: string): Chainable<Element>
      
      /**
       * Register a new user for testing
       */
      registerUser(userData?: {
        username: string
        email: string
        password: string
      }): Chainable<Element>
      
      /**
       * Seed test database with sample data
       */
      seedTestData(): Chainable<null>
      
      /**
       * Clean test database
       */
      cleanTestData(): Chainable<null>
    }
  }
}

// Login command
Cypress.Commands.add('login', (
  email = Cypress.env('testUserEmail'), 
  password = Cypress.env('testUserPassword')
) => {
  cy.session([email, password], () => {
    cy.visit('/login')
    cy.get('[data-testid="email-input"]').type(email)
    cy.get('[data-testid="password-input"]').type(password)
    cy.get('[data-testid="login-button"]').click()
    
    // Wait for successful login
    cy.url().should('not.include', '/login')
    cy.get('[data-testid="user-menu"]').should('be.visible')
  })
})

// Register user command
Cypress.Commands.add('registerUser', (userData) => {
  const defaultUserData = {
    username: `cypress-${Date.now()}`,
    email: `cypress-${Date.now()}@example.com`,
    password: 'CypressTest123!'
  }
  
  const user = { ...defaultUserData, ...userData }
  
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/auth/register`,
    body: user
  }).then((response) => {
    expect(response.status).to.eq(201)
  })
  
  return cy.wrap(user)
})

// Database seeding
Cypress.Commands.add('seedTestData', () => {
  return cy.task('seedDatabase')
})

// Database cleanup
Cypress.Commands.add('cleanTestData', () => {
  return cy.task('cleanDatabase')
})

export {}

// ***********************************************
// E2E Authentication Flow Tests
// ***********************************************

describe('Authentication Flow', () => {
  beforeEach(() => {
    // Clean up any existing sessions
    cy.clearCookies()
    cy.clearLocalStorage()
  })

  it('should display login form and allow navigation to register', () => {
    cy.visit('/login')
    
    // Should see login form elements
    cy.contains('Sign In').should('be.visible')
    cy.get('input[placeholder="Username"]').should('be.visible')
    cy.get('input[placeholder="Password"]').should('be.visible')
    cy.contains('button', 'Sign In').should('be.visible')
    
    // Should be able to navigate to register
    cy.contains('Sign up now').click()
    cy.url().should('include', '/register')
  })

  it('should handle invalid login credentials', () => {
    cy.visit('/login')
    
    cy.get('input[placeholder="Username"]').type('invaliduser')
    cy.get('input[placeholder="Password"]').type('wrongpassword')
    cy.contains('button', 'Sign In').click()
    
    // Should show error message or stay on login page
    cy.url().should('include', '/login')
    
    // The form should still be visible
    cy.contains('Sign In').should('be.visible')
  })

  it('should redirect to login when accessing protected routes', () => {
    // Try to access a protected route without auth
    cy.visit('/')
    
    // Should redirect to login
    cy.url().should('include', '/login')
    cy.contains('Sign In').should('be.visible')
  })
})

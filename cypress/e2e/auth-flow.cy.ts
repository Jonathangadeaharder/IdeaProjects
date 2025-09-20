// ***********************************************
// E2E Authentication Flow Tests
// ***********************************************

describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.cleanTestData()
  })

  it('should complete full registration and login flow', () => {
    const userData = {
      username: `cypress-${Date.now()}`,
      email: `cypress-${Date.now()}@example.com`,
      password: 'CypressTest123!'
    }

    // Visit registration page
    cy.visit('/register')
    
    // Fill registration form
    cy.get('[data-testid="username-input"]').type(userData.username)
    cy.get('[data-testid="email-input"]').type(userData.email)
    cy.get('[data-testid="password-input"]').type(userData.password)
    cy.get('[data-testid="confirm-password-input"]').type(userData.password)
    
    // Submit registration
    cy.get('[data-testid="register-button"]').click()
    
    // Should redirect to dashboard or login
    cy.url().should('not.include', '/register')
    
    // If redirected to login, complete login flow
    cy.url().then(url => {
      if (url.includes('/login')) {
        cy.get('[data-testid="email-input"]').type(userData.email)
        cy.get('[data-testid="password-input"]').type(userData.password)
        cy.get('[data-testid="login-button"]').click()
      }
    })
    
    // Should be logged in and see user menu
    cy.get('[data-testid="user-menu"]').should('be.visible')
    cy.get('[data-testid="user-menu"]').should('contain', userData.username)
  })

  it('should handle login with existing user', () => {
    // Register user via API first
    cy.registerUser().then((userData) => {
      // Now test login flow
      cy.visit('/login')
      
      cy.get('[data-testid="email-input"]').type(userData.email)
      cy.get('[data-testid="password-input"]').type(userData.password)
      cy.get('[data-testid="login-button"]').click()
      
      // Should be redirected to dashboard
      cy.url().should('not.include', '/login')
      cy.get('[data-testid="user-menu"]').should('be.visible')
    })
  })

  it('should handle invalid login credentials', () => {
    cy.visit('/login')
    
    cy.get('[data-testid="email-input"]').type('invalid@example.com')
    cy.get('[data-testid="password-input"]').type('wrongpassword')
    cy.get('[data-testid="login-button"]').click()
    
    // Should show error message
    cy.get('[data-testid="error-message"]').should('be.visible')
    cy.get('[data-testid="error-message"]').should('contain', 'Invalid credentials')
    
    // Should stay on login page
    cy.url().should('include', '/login')
  })

  it('should handle logout flow', () => {
    // Login first
    cy.registerUser().then((userData) => {
      cy.login(userData.email, userData.password)
      
      // Visit dashboard
      cy.visit('/dashboard')
      cy.get('[data-testid="user-menu"]').should('be.visible')
      
      // Logout
      cy.get('[data-testid="user-menu"]').click()
      cy.get('[data-testid="logout-button"]').click()
      
      // Should redirect to home/login
      cy.url().should('not.include', '/dashboard')
      cy.get('[data-testid="user-menu"]').should('not.exist')
    })
  })
})

// ***********************************************
// E2E Video Learning Flow Tests
// ***********************************************

describe('Video Learning Flow', () => {
  beforeEach(() => {
    cy.cleanTestData()
    cy.seedTestData()
    
    // Login before each test
    cy.registerUser().then((userData) => {
      cy.login(userData.email, userData.password)
    })
  })

  it('should complete full video learning workflow', () => {
    // Navigate to video library
    cy.visit('/videos')
    cy.get('[data-testid="video-library"]').should('be.visible')
    
    // Select a video
    cy.get('[data-testid="video-card"]').first().click()
    
    // Should navigate to video player
    cy.url().should('include', '/videos/')
    cy.get('[data-testid="video-player"]').should('be.visible')
    
    // Play video
    cy.get('[data-testid="play-button"]').click()
    cy.get('[data-testid="video-player"]').should('have.attr', 'data-playing', 'true')
    
    // Check subtitles are available
    cy.get('[data-testid="subtitle-toggle"]').click()
    cy.get('[data-testid="subtitles"]').should('be.visible')
    
    // Interact with vocabulary features
    cy.get('[data-testid="vocabulary-panel-toggle"]').click()
    cy.get('[data-testid="vocabulary-panel"]').should('be.visible')
    
    // Mark a word as known
    cy.get('[data-testid="vocabulary-word"]').first().within(() => {
      cy.get('[data-testid="mark-known-button"]').click()
    })
    
    // Verify word is marked as known
    cy.get('[data-testid="vocabulary-word"]').first().should('have.attr', 'data-known', 'true')
    
    // Check progress tracking
    cy.get('[data-testid="progress-indicator"]').should('be.visible')
    cy.get('[data-testid="progress-percentage"]').should('not.contain', '0%')
  })

  it('should handle video upload workflow', () => {
    cy.visit('/upload')
    
    // Upload video file (using fixture)
    cy.fixture('sample-video.mp4', 'binary')
      .then(Cypress.Blob.binaryStringToBlob)
      .then(fileContent => {
        cy.get('[data-testid="video-upload-input"]').selectFile({
          contents: fileContent,
          fileName: 'test-video.mp4',
          mimeType: 'video/mp4'
        })
      })
    
    // Fill metadata
    cy.get('[data-testid="video-title-input"]').type('Test Video')
    cy.get('[data-testid="video-series-input"]').type('Test Series')
    
    // Start upload
    cy.get('[data-testid="upload-button"]').click()
    
    // Should show upload progress
    cy.get('[data-testid="upload-progress"]').should('be.visible')
    
    // Wait for upload completion
    cy.get('[data-testid="upload-success"]', { timeout: 30000 }).should('be.visible')
    
    // Should redirect to processing page
    cy.url().should('include', '/processing/')
  })

  it('should handle vocabulary learning game', () => {
    cy.visit('/vocabulary/game')
    
    // Start vocabulary game
    cy.get('[data-testid="start-game-button"]').click()
    
    // Should show game interface
    cy.get('[data-testid="game-interface"]').should('be.visible')
    cy.get('[data-testid="game-question"]').should('be.visible')
    
    // Answer questions
    for (let i = 0; i < 5; i++) {
      cy.get('[data-testid="game-option"]').first().click()
      cy.get('[data-testid="next-question-button"]').click()
    }
    
    // Should show results
    cy.get('[data-testid="game-results"]').should('be.visible')
    cy.get('[data-testid="game-score"]').should('be.visible')
    
    // Should update user progress
    cy.visit('/profile')
    cy.get('[data-testid="vocabulary-stats"]').should('be.visible')
  })

  it('should handle subtitle filtering and processing', () => {
    cy.visit('/videos')
    
    // Select video with subtitles
    cy.get('[data-testid="video-card"]').first().click()
    
    // Open subtitle tools
    cy.get('[data-testid="subtitle-tools-button"]').click()
    cy.get('[data-testid="subtitle-tools-panel"]').should('be.visible')
    
    // Filter subtitles by difficulty
    cy.get('[data-testid="difficulty-filter"]').select('beginner')
    cy.get('[data-testid="apply-filter-button"]').click()
    
    // Should show filtered subtitles
    cy.get('[data-testid="filtered-subtitles"]').should('be.visible')
    cy.get('[data-testid="subtitle-segment"]').should('have.length.greaterThan', 0)
    
    // Export filtered subtitles
    cy.get('[data-testid="export-subtitles-button"]').click()
    
    // Should trigger download
    cy.readFile('cypress/downloads/filtered-subtitles.srt').should('exist')
  })
})

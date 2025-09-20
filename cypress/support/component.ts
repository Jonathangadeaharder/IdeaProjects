// ***********************************************************
// Component testing support file for LangPlug
// ***********************************************************

import './commands'
import { mount } from 'cypress/react18'

// Add mount command for React component testing
declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount
    }
  }
}

Cypress.Commands.add('mount', mount)

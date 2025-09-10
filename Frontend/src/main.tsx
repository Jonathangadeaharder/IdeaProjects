import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { useAuthStore } from '@/store/useAuthStore'
import { logger } from '@/services/logger'

// Initialize authentication state
const initializeAuth = async () => {
  logger.info('App', 'Starting application initialization')
  try {
    const { checkAuth } = useAuthStore.getState()
    await checkAuth()
    logger.info('App', 'Authentication initialization complete')
  } catch (error) {
    logger.error('App', 'Failed to initialize authentication', { error: (error as Error).message }, error as Error)
    throw error
  }
}

// Initialize auth before rendering
logger.info('App', 'LangPlug Frontend starting up', {
  environment: import.meta.env.MODE,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  timestamp: new Date().toISOString()
})

initializeAuth().catch((error) => {
  logger.error('App', 'Critical initialization error', { error: (error as Error).message }, error as Error)
})

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
)

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
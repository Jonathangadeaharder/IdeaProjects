import { describe, it, expect, beforeAll } from 'vitest'
import { getApiConfig } from '../../config/api-config'

describe('API Connection Configuration', () => {
  it('should use environment variable for API URL when provided', () => {
    // Test that VITE_API_URL overrides the default
    const originalEnv = import.meta.env.VITE_API_URL

    // Set a custom URL
    import.meta.env.VITE_API_URL = 'http://localhost:9999'
    const config = getApiConfig()

    expect(config.baseUrl).toBe('http://localhost:9999')

    // Restore original
    import.meta.env.VITE_API_URL = originalEnv
  })

  it('should default to port 8000 when no environment variable is set', () => {
    // Ensure no env var is set
    const originalEnv = import.meta.env.VITE_API_URL
    delete import.meta.env.VITE_API_URL

    const config = getApiConfig()
    expect(config.baseUrl).toBe('http://localhost:8000')

    // Restore original
    if (originalEnv) {
      import.meta.env.VITE_API_URL = originalEnv
    }
  })

  it('should match Backend port configuration', () => {
    // This test documents the expected coordination between Frontend and Backend
    const config = getApiConfig()
    const url = new URL(config.baseUrl)

    // Backend should be running on the same port that Frontend expects
    // This is a contract test - if this fails, Frontend and Backend are misconfigured
    expect(['8000', '8001', '8002', '8003']).toContain(url.port || '80')
  })
})
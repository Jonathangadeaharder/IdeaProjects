/* eslint-disable @typescript-eslint/no-explicit-any */
import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'
import React from 'react'
import { ThemeProvider } from 'styled-components'
import { act } from 'react'

// extends Vitest's expect method with methods from react-testing-library
expect.extend(matchers)

// runs a cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
  cleanup()
})

// Mock theme for styled-components
const mockTheme = {
  colors: {
    primary: '#FF6B6B',
    primaryDark: '#EE5A52',
    primaryLight: '#FF8787',
    secondary: '#4ECDC4',
    secondaryDark: '#38B2AA',
    secondaryLight: '#6DD5CE',
    background: '#FFFFFF',
    surface: '#F8F9FA',
    surfaceHover: '#E9ECEF',
    text: '#1A1A1A',
    textSecondary: '#6C757D',
    textLight: '#ADB5BD',
    textInverse: '#FFFFFF',
    border: '#E1E4E8',
    borderLight: '#F0F2F5',
    success: '#52C41A',
    warning: '#FAAD14',
    error: '#F5222D',
    info: '#1890FF',
    disabled: '#D1D5DB',
    overlay: 'rgba(0, 0, 0, 0.5)',
    shadow: 'rgba(0, 0, 0, 0.1)',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
    '4xl': '6rem',
  },
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    primary: '0 10px 40px -10px rgba(255, 107, 107, 0.35)',
    secondary: '0 10px 40px -10px rgba(78, 205, 196, 0.35)',
  },
  transitions: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '350ms ease-in-out',
    easing: {
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
  },
  typography: {
    fontFamily: {
      primary: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      secondary: '"Poppins", "Inter", sans-serif',
      mono: '"JetBrains Mono", "Courier New", monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
    },
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
      loose: 2,
    },
  },
  radius: {
    none: '0',
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    '2xl': '1.5rem',
    full: '9999px',
  },
  breakpoints: {
    xs: '480px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
    toast: 1080,
  },
  grid: {
    columns: 12,
    gutter: '1rem',
    maxWidth: '1280px',
  },
}

// Make theme available global for tests
;(global as any).mockTheme = mockTheme

// Helper to wrap components with theme provider
;(global as any).withTheme = (component: React.ReactElement) =>
  React.createElement(ThemeProvider, { theme: mockTheme }, component)

// Make React.act available globally to replace ReactDOMTestUtils.act
;(global as any).act = act

// Enhanced act wrapper for async operations
;(global as any).actAsync = async (fn: () => Promise<any>) => {
  await act(async () => {
    await fn()
  })
}

// Suppress specific warnings that come from testing libraries
const originalConsoleWarn = console.warn
const originalConsoleError = console.error

console.warn = (...args) => {
  const message = args[0]
  if (
    typeof message === 'string' &&
    (message.includes('ReactDOMTestUtils.act') ||
      message.includes('React Router Future Flag Warning') ||
      (message.includes('An update to') && message.includes('was not wrapped in act')) ||
      message.includes('Warning: `ReactDOMTestUtils.act` is deprecated'))
  ) {
    return // Suppress these warnings
  }
  originalConsoleWarn.apply(console, args)
}

console.error = (...args) => {
  const message = args[0]
  if (
    typeof message === 'string' &&
    (message.includes('ReactDOMTestUtils.act') ||
      (message.includes('An update to') && message.includes('was not wrapped in act')))
  ) {
    return // Suppress these errors
  }
  originalConsoleError.apply(console, args)
}

// Mock IntersectionObserver
class MockIntersectionObserver {
  constructor() {
    // Mock constructor - no-op for testing
  }
  disconnect() {
    // Mock disconnect - no-op for testing
  }
  observe() {
    // Mock observe - no-op for testing
  }
  unobserve() {
    // Mock unobserve - no-op for testing
  }
  readonly root = null
  readonly rootMargin = ''
  readonly thresholds = []
  takeRecords() {
    return []
  }
}
global.IntersectionObserver = MockIntersectionObserver as any

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {
    // Mock constructor - no-op for testing
  }
  disconnect() {
    // Mock disconnect - no-op for testing
  }
  observe() {
    // Mock observe - no-op for testing
  }
  unobserve() {
    // Mock unobserve - no-op for testing
  }
}

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn(() => 'mocked-url')
global.URL.revokeObjectURL = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
  configurable: true,
})

// Fix URLSearchParams for jsdom
if (!global.URLSearchParams) {
  global.URLSearchParams = URLSearchParams
}

// Note: Vitest's jsdom environment automatically sets up the DOM
// No need for manual jsdom initialization here

// Framer-motion is mocked via resolve.alias in vitest.config.ts

// Mock axios to prevent network requests in tests
vi.mock('axios', async () => {
  const actual = await vi.importActual('axios')
  return {
    ...actual,
    default: {
      create: vi.fn(() => ({
        get: vi.fn(() => Promise.resolve({ data: {} })),
        post: vi.fn(() => Promise.resolve({ data: {} })),
        put: vi.fn(() => Promise.resolve({ data: {} })),
        delete: vi.fn(() => Promise.resolve({ data: {} })),
        interceptors: {
          request: { use: vi.fn(), eject: vi.fn() },
          response: { use: vi.fn(), eject: vi.fn() },
        },
      })),
      get: vi.fn(() => Promise.resolve({ data: {} })),
      post: vi.fn(() => Promise.resolve({ data: {} })),
      put: vi.fn(() => Promise.resolve({ data: {} })),
      delete: vi.fn(() => Promise.resolve({ data: {} })),
    },
  }
})

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
}
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
  writable: true,
  configurable: true,
})

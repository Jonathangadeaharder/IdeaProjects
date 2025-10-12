import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'

import { ThemeProvider, ThemeToggle, useTheme } from '../ThemeContext'
import { darkTheme, lightTheme as _lightTheme } from '@/styles/theme'

const TestComponent: React.FC = () => {
  const { theme, isDarkMode, toggleTheme, setDarkMode } = useTheme()

  return (
    <div>
      <div data-testid="theme-value">{theme.colors.background}</div>
      <div data-testid="mode">{isDarkMode ? 'dark' : 'light'}</div>
      <button data-testid="toggle" onClick={toggleTheme}>
        toggle
      </button>
      <button data-testid="force-dark" onClick={() => setDarkMode(true)}>
        force dark
      </button>
      <button data-testid="force-light" onClick={() => setDarkMode(false)}>
        force light
      </button>
    </div>
  )
}

type Listener = (event: MediaQueryListEvent) => void

let originalMatchMedia: typeof window.matchMedia
let metaTag: HTMLMetaElement
let systemPrefersDark = false
let listeners: Listener[] = []

const installMatchMediaMock = () => {
  listeners = []
  const mockQuery: MediaQueryList = {
    matches: systemPrefersDark,
    media: '(prefers-color-scheme: dark)',
    onchange: null,
    addEventListener: (type: string, listener: EventListenerOrEventListenerObject) => {
      listeners.push(listener as Listener)
    },
    removeEventListener: (type: string, listener: EventListenerOrEventListenerObject) => {
      listeners = listeners.filter(registered => registered !== listener)
    },
    addListener(handler: Listener) {
      listeners.push(handler)
    },
    removeListener(handler: Listener) {
      listeners = listeners.filter(registered => registered !== handler)
    },
    dispatchEvent: () => true,
  }

  window.matchMedia = vi.fn(() => mockQuery) as unknown as typeof window.matchMedia
}

const triggerSystemThemeChange = (matches: boolean) => {
  systemPrefersDark = matches
  const event = {
    matches,
    media: '(prefers-color-scheme: dark)',
  } as MediaQueryListEvent

  for (const handler of listeners) {
    handler(event)
  }
}

beforeEach(() => {
  window.localStorage.clear()
  document.documentElement.classList.remove('dark')
  document.body.innerHTML = ''
  document.head.innerHTML = ''

  metaTag = document.createElement('meta')
  metaTag.setAttribute('name', 'theme-color')
  document.head.appendChild(metaTag)

  originalMatchMedia = window.matchMedia
  listeners = []
  systemPrefersDark = false
  installMatchMediaMock()
})

afterEach(() => {
  window.localStorage.clear()
  if (originalMatchMedia) {
    window.matchMedia = originalMatchMedia
  }
  vi.restoreAllMocks()
})

const renderWithProvider = (ui: React.ReactElement) => render(<ThemeProvider>{ui}</ThemeProvider>)

describe('ThemeProvider', () => {
  it('uses stored preference when available', async () => {
    const getItemSpy = vi
      .spyOn(window.localStorage, 'getItem')
      .mockImplementation((key: string) => {
        if (key === 'theme') {
          return 'dark'
        }
        return null
      })

    renderWithProvider(<TestComponent />)

    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('dark'))
    expect(screen.getByTestId('theme-value').textContent).toBe(darkTheme.colors.background)
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    getItemSpy.mockRestore()
  })

  it('falls back to system preference when nothing stored', async () => {
    vi.spyOn(window.localStorage, 'getItem').mockReturnValue(null)
    systemPrefersDark = true
    installMatchMediaMock()

    renderWithProvider(<TestComponent />)

    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('dark'))
  })

  it('persists changes and updates DOM state when toggled', async () => {
    const setItemSpy = vi.spyOn(window.localStorage, 'setItem')

    renderWithProvider(<TestComponent />)

    fireEvent.click(screen.getByTestId('toggle'))

    await waitFor(() => expect(setItemSpy).toHaveBeenCalledWith('theme', 'dark'))
    expect(setItemSpy).toHaveBeenCalledWith('theme', 'dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(metaTag.getAttribute('content')).toBe(darkTheme.colors.background)
  })

  it('can force explicit light/dark modes', async () => {
    renderWithProvider(<TestComponent />)

    fireEvent.click(screen.getByTestId('force-dark'))
    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('dark'))

    fireEvent.click(screen.getByTestId('force-light'))
    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('light'))
  })

  it('responds to system theme changes when user has no preference', async () => {
    renderWithProvider(<TestComponent />)

    triggerSystemThemeChange(true)
    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('dark'))

    triggerSystemThemeChange(false)
    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('light'))
  })

  it('ignores system theme changes after user sets a preference', async () => {
    renderWithProvider(<TestComponent />)

    fireEvent.click(screen.getByTestId('toggle'))
    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('dark'))

    triggerSystemThemeChange(false)
    // stored preference should win
    await waitFor(() => expect(screen.getByTestId('mode').textContent).toBe('dark'))
  })
})

describe('ThemeToggle component', () => {
  const Wrapper = () => (
    <ThemeProvider>
      <ThemeToggle />
      <TestComponent />
    </ThemeProvider>
  )

  it('toggles theme when clicked', async () => {
    const setItemSpy = vi.spyOn(window.localStorage, 'setItem')

    render(<Wrapper />)

    fireEvent.click(screen.getByRole('button', { name: /toggle theme/i }))

    await waitFor(() => expect(setItemSpy).toHaveBeenCalledWith('theme', 'dark'))
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})

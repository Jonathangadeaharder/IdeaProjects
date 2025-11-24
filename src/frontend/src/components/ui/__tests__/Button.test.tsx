import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ThemeProvider } from 'styled-components'
import { lightTheme } from '@/styles/theme'
import { Button } from '../Button'

const theme = lightTheme

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
)

describe('Button Component', () => {
  it('renders with text content', () => {
    render(
      <TestWrapper>
        <Button>Click me</Button>
      </TestWrapper>
    )
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  it('handles click events properly', () => {
    const handleClick = vi.fn()
    render(
      <TestWrapper>
        <Button onClick={handleClick}>Click me</Button>
      </TestWrapper>
    )

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies disabled state correctly', () => {
    render(
      <TestWrapper>
        <Button disabled>Disabled Button</Button>
      </TestWrapper>
    )

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('applies loading state and disables button', () => {
    render(
      <TestWrapper>
        <Button loading>Loading Button</Button>
      </TestWrapper>
    )

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('accepts variant prop for different button types', () => {
    const { rerender } = render(
      <TestWrapper>
        <Button variant="primary" data-testid="test-button">
          Primary Button
        </Button>
      </TestWrapper>
    )

    const button = screen.getByTestId('test-button')
    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent('Primary Button')

    rerender(
      <TestWrapper>
        <Button variant="secondary" data-testid="test-button">
          Secondary Button
        </Button>
      </TestWrapper>
    )

    expect(button).toBeInTheDocument()
    expect(button).toHaveTextContent('Secondary Button')
  })

  it('prevents click when disabled', () => {
    const handleClick = vi.fn()
    render(
      <TestWrapper>
        <Button disabled onClick={handleClick}>
          Disabled Button
        </Button>
      </TestWrapper>
    )

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).not.toHaveBeenCalled()
  })
})

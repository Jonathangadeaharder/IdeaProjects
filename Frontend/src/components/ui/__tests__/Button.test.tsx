import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ThemeProvider } from 'styled-components';
import { Button } from '../Button';

const theme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#6b7280',
    danger: '#dc2626'
  }
};

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('Button Component', () => {
  it('renders with text content', () => {
    render(
      <TestWrapper>
        <Button>Click me</Button>
      </TestWrapper>
    );
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('handles click events properly', () => {
    const handleClick = vi.fn();
    render(
      <TestWrapper>
        <Button onClick={handleClick}>Click me</Button>
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies disabled state correctly', () => {
    render(
      <TestWrapper>
        <Button disabled>Disabled Button</Button>
      </TestWrapper>
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('applies loading state and disables button', () => {
    render(
      <TestWrapper>
        <Button loading>Loading Button</Button>
      </TestWrapper>
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('renders different variants with distinct styling', () => {
    const { rerender } = render(
      <TestWrapper>
        <Button variant="primary">Primary Button</Button>
      </TestWrapper>
    );

    const primaryButton = screen.getByRole('button');
    const primaryStyles = getComputedStyle(primaryButton);

    rerender(
      <TestWrapper>
        <Button variant="secondary">Secondary Button</Button>
      </TestWrapper>
    );

    const secondaryButton = screen.getByRole('button');
    const secondaryStyles = getComputedStyle(secondaryButton);

    // Test that variants have different styling without testing exact values
    expect(primaryStyles.background).not.toBe(secondaryStyles.background);

    // Ensure styling is applied (not transparent/default)
    expect(primaryStyles.background).not.toBe('rgba(0, 0, 0, 0)');
    expect(secondaryStyles.background).not.toBe('rgba(0, 0, 0, 0)');
  });

  it('prevents click when disabled', () => {
    const handleClick = vi.fn();
    render(
      <TestWrapper>
        <Button disabled onClick={handleClick}>Disabled Button</Button>
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });
});
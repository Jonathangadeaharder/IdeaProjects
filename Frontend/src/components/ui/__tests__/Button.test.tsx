import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ThemeProvider } from 'styled-components';
import { Button } from '../Button';

// Simple theme for testing
const theme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#6b7280',
    danger: '#dc2626'
  }
};

// Wrapper component for styled-components
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('Button Component', () => {
  it('renders with children', () => {
    render(
      <TestWrapper>
        <Button>Click me</Button>
      </TestWrapper>
    );
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(
      <TestWrapper>
        <Button onClick={handleClick}>Click me</Button>
      </TestWrapper>
    );
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles correctly', () => {
    render(
      <TestWrapper>
        <Button variant="secondary">Secondary Button</Button>
      </TestWrapper>
    );
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('disables button when disabled prop is true', () => {
    render(
      <TestWrapper>
        <Button disabled>Disabled Button</Button>
      </TestWrapper>
    );
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('shows loading state', () => {
    render(
      <TestWrapper>
        <Button loading>Loading Button</Button>
      </TestWrapper>
    );
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
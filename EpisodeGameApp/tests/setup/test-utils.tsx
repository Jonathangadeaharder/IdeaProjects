import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react-native';
import { ThemeProvider } from '../../src/theme/ThemeProvider';

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ThemeProvider>
      {children}
    </ThemeProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react-native';

// Override render method
export { customRender as render };

// Common test utilities
export const createMockEpisode = (overrides = {}) => ({
  id: 'test-episode-1',
  title: 'Test Episode',
  description: 'A test episode for testing purposes',
  videoUrl: 'https://example.com/video.mp4',
  subtitleUrl: 'https://example.com/subtitles.vtt',
  duration: 1800, // 30 minutes
  difficulty: 'A1' as const,
  ...overrides,
});

export const createMockVocabularyItem = (overrides = {}) => ({
  word: 'test',
  translation: 'Test',
  difficulty: 'A1' as const,
  context: 'This is a test word.',
  timestamp: 120,
  ...overrides,
});

// Mock navigation
export const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
  reset: jest.fn(),
  setParams: jest.fn(),
  dispatch: jest.fn(),
  setOptions: jest.fn(),
  isFocused: jest.fn(() => true),
  addListener: jest.fn(() => jest.fn()),
  removeListener: jest.fn(),
};

// Mock route
export const mockRoute = {
  key: 'test-route',
  name: 'TestScreen' as const,
  params: {},
};

// Wait for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0));
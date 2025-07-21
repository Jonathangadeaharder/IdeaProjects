/**
 * @format
 */

import React from 'react';
import { render } from './setup/test-utils';
import { ThemeProvider } from '../src/theme/ThemeProvider';
import { Text } from 'react-native';

// Simple test component to isolate the issue
const SimpleApp = () => (
  <ThemeProvider>
    <Text>Test App</Text>
  </ThemeProvider>
);

describe('App', () => {
  it('renders ThemeProvider correctly', () => {
    const { root } = render(<SimpleApp />);
    expect(root).toBeTruthy();
  });

  it('initializes without crashing', () => {
    expect(() => render(<SimpleApp />)).not.toThrow();
  });
});
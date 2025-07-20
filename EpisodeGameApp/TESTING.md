# Testing Guide for EpisodeGameApp

This document provides comprehensive information about the testing setup and how to run tests for the EpisodeGameApp project.

## Overview

The project includes unit and integration tests for:
- **Frontend**: React Native components, services, and context
- **Python API Integration**: Direct communication with Python FastAPI backend

## Test Structure

### Frontend Tests
Location: `src/` directory with `__tests__` subdirectories

#### Unit Tests
- **GameContext** (`src/context/__tests__/GameContext.test.tsx`)
  - Tests game state management
  - Covers starting/completing games, processing stages, episode status

- **SubtitleService** (`src/services/__tests__/SubtitleService.test.ts`)
  - Tests subtitle processing logic
  - Covers episode processing, vocabulary loading, progress updates

- **PythonBridgeService** (`src/services/__tests__/PythonBridgeService.test.ts`)
  - Tests direct Python API communication
  - Covers health checks, subtitle processing, vocabulary analysis

#### Integration Tests
- **A1DeciderGameScreen** (`src/screens/__tests__/A1DeciderGameScreen.test.tsx`)
  - Tests complete game flow
  - Covers processing, vocabulary check, word selection, navigation

- **VideoPlayerScreen** (`src/screens/__tests__/VideoPlayerScreen.test.tsx`)
  - Tests video playback integration
  - Covers subtitle display, processing status, error handling

### Python API Integration Tests
Note: The Node.js backend has been eliminated. The frontend now communicates directly with the Python FastAPI server.

#### Integration Testing
- Python API endpoints are tested through frontend service tests
- Direct API communication is validated in PythonBridgeService tests
- End-to-end testing covers the complete frontend-to-Python workflow

## Testing Dependencies

### Frontend
- `@testing-library/react-native` - React Native testing utilities
- `@testing-library/jest-native` - Additional Jest matchers
- `jest-fetch-mock` - Mock fetch API calls for Python API integration
- `react-test-renderer` - React component rendering

## Running Tests

### Individual Test Suites

#### Frontend Tests Only
```bash
# From project root
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific test file
npm test -- GameContext.test.tsx
```

### All Tests
```bash
# From project root - runs all frontend tests including Python API integration
npm run test:all
```

This command will:
1. Run all frontend tests
2. Run Python API integration tests
3. Provide a summary of results
4. Exit with appropriate code (0 for success, 1 for failure)

## Test Configuration

### Jest Configuration (`jest.config.js`)
- **Environment**: React Native
- **Setup**: `jest.setup.js` with mocks for React Native modules
- **Coverage**: Collects from `src/` directory
- **Transform**: Handles TypeScript and React Native modules
- **Ignores**: Backend directory (eliminated in ARCH-02)

## Mock Strategy

### Mock Strategy
- **React Native modules**: Animated, Alert, navigation
- **Fetch API**: Using `jest-fetch-mock` for Python API calls
- **PythonBridgeService**: Mocked in service tests to simulate Python API responses
- **Python API Endpoints**: Mocked to return expected response structures

## Coverage Reports

Generate coverage reports:

```bash
# Frontend and Python API integration coverage
npm test -- --coverage
```

Coverage reports are generated in the `coverage/` directory.

## Writing New Tests

### Frontend Test Template
```typescript
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import YourComponent from '../YourComponent';

describe('YourComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render correctly', () => {
    const { getByText } = render(<YourComponent />);
    expect(getByText('Expected Text')).toBeTruthy();
  });

  it('should handle user interaction', async () => {
    const { getByTestId } = render(<YourComponent />);
    fireEvent.press(getByTestId('button'));
    
    await waitFor(() => {
      expect(/* assertion */).toBeTruthy();
    });
  });
});
```

### Python API Integration Test Template
```typescript
import { PythonBridgeService } from '../PythonBridgeService';

// Mock fetch for Python API calls
jest.mock('jest-fetch-mock');
const fetchMock = require('jest-fetch-mock');

describe('Python API Integration', () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });

  it('should handle successful API response', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({
      success: true,
      message: 'Processing completed',
      results: { /* expected data */ }
    }));

    const service = new PythonBridgeService();
    const result = await service.requestSubtitleCreation('test.mp4', 'de');
    
    expect(result.success).toBe(true);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/process',
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('should handle API errors', async () => {
    fetchMock.mockRejectOnce(new Error('Network error'));

    const service = new PythonBridgeService();
    const result = await service.requestSubtitleCreation('test.mp4', 'de');
    
    expect(result.success).toBe(false);
    expect(result.error).toContain('Network error');
  });
});
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies and APIs
3. **Coverage**: Aim for high test coverage on critical paths
4. **Descriptive**: Use clear, descriptive test names
5. **Setup/Teardown**: Clean up after each test
6. **Edge Cases**: Test error conditions and edge cases
7. **Integration**: Test component interactions and data flow

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Check Jest configuration for module mapping
   - Ensure all dependencies are installed

2. **React Native component errors**
   - Verify mocks in `jest.setup.js`
   - Check for missing native module mocks

3. **Async test failures**
   - Use `waitFor` for async operations
   - Ensure proper cleanup in `afterEach`

4. **Backend test failures**
   - Check mock implementations
   - Verify Express app setup

### Debug Mode

Run tests with debug output:
```bash
# Frontend
npm test -- --verbose

# Backend
cd backend && npm test -- --verbose
```

## Continuous Integration

For CI/CD pipelines, use:
```bash
# Install dependencies
npm install
cd backend && npm install

# Run all tests
npm run test:all
```

This ensures both frontend and backend tests pass before deployment.
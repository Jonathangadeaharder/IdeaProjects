# Tests Directory

This directory contains all test files for the EpisodeGameApp project, organized by feature area.

## Structure

```
tests/
├── README.md                    # This file
├── components/                  # Component tests
├── screens/                     # Screen component tests
├── services/                    # Service layer tests
├── stores/                      # State management tests
├── hooks/                       # Custom hooks tests
├── utils/                       # Utility function tests
├── integration/                 # Integration tests
└── setup/                       # Test setup and configuration
    ├── jest.setup.js           # Jest setup file
    └── test-utils.tsx          # Common test utilities
```

## Running Tests

### All Tests
```bash
npm test
```

### Specific Test Categories
```bash
# Component tests
npm test tests/components

# Service tests
npm test tests/services

# Screen tests
npm test tests/screens

# Store tests
npm test tests/stores
```

### Watch Mode
```bash
npm test -- --watch
```

## Test Conventions

1. **File Naming**: Use `.test.tsx` for React components and `.test.ts` for TypeScript modules
2. **Test Structure**: Follow AAA pattern (Arrange, Act, Assert)
3. **Mocking**: Use Jest mocks for external dependencies
4. **Coverage**: Aim for >80% code coverage
5. **Async Testing**: Use `waitFor` and proper async/await patterns

## Test Categories

### Unit Tests
- Individual component functionality
- Service method behavior
- Utility function logic
- Hook behavior

### Integration Tests
- Component interaction with services
- State management flow
- API integration
- Navigation flow

### Performance Tests
- Render performance
- Memory usage
- State update efficiency
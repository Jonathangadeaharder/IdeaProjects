# LangPlug CRUSH Development Guide

## Build Commands

### Backend (Python/FastAPI)
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Build distribution (if applicable)
# python setup.py sdist bdist_wheel
```

### Frontend (TypeScript/React)
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Linting Commands

### Backend
```bash
# Run linter (Ruff)
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code
ruff format .
```

### Frontend
```bash
# Run ESLint
npm run lint

# Fix linting issues automatically (if supported)
npm run lint -- --fix
```

## Test Commands

### Backend (Python/Pytest)
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_file.py

# Run a specific test function
pytest tests/test_file.py::test_function_name

# Run tests with specific markers
pytest -m "unit"
pytest -m "integration"

# Run tests with coverage
pytest --cov=.

# Run tests in verbose mode
pytest -v
```

### Frontend (TypeScript/Vitest)
```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run a single test file
npm run test -- src/components/ComponentName.test.tsx

# Run tests with coverage
npm run test:coverage

# Run tests in UI mode
npm run test:ui
```

## Code Style Guidelines

### Backend (Python)

1. **Imports**:
   - Standard library imports first, then third-party, then local imports
   - Use specific imports rather than wildcard imports
   - Group imports logically

2. **Formatting**:
   - Follow PEP 8 with 4-space indentation
   - Line length: 88 characters (Ruff default)
   - Use Ruff for automatic formatting

3. **Types**:
   - Use type hints for all function parameters and return values
   - Import types from typing module as needed

4. **Naming Conventions**:
   - snake_case for variables and functions
   - PascalCase for classes
   - UPPER_CASE for constants

5. **Error Handling**:
   - Use specific exception types when possible
   - Log errors with appropriate context
   - Raise HTTPException for API errors with proper status codes

### Frontend (TypeScript/React)

1. **Imports**:
   - Use path aliases (@/*) for internal modules
   - Type-only imports use `import type {}`
   - Default imports for libraries

2. **Formatting**:
   - Use Prettier/ESLint for consistent formatting
   - TypeScript strict mode enabled

3. **Types**:
   - Define interfaces for component props
   - Use TypeScript for all components and functions
   - Union types for variant enums

4. **Naming Conventions**:
   - PascalCase for components and files
   - camelCase for variables and functions
   - UPPER_CASE for constants

5. **Component Structure**:
   - Functional components with TypeScript interfaces
   - Styled Components for CSS-in-JS
   - Default exports for components
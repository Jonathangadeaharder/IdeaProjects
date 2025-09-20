# Testing Strategy

This document outlines the comprehensive testing strategy for LangPlug, covering Contract-Driven Development (CDD), test management, and tooling.

## Overview

LangPlug uses a comprehensive three-tier testing approach to ensure reliability, maintainability, and professional development practices:

1. **Unit/Integration Tests** - Fast in-memory tests with dependency overrides
2. **Frontend Contract Tests** - Mocked API tests for components and services
3. **End-to-End Tests** - Full user workflow testing with Cypress
4. **Professional Test Management** - Proper handling of failing tests and comprehensive coverage

## In-Memory Testing with Dependency Overrides

### Philosophy

Instead of using live servers, we use FastAPI's TestClient and httpx with ASGI transport for fast, reliable in-process testing. This approach:

- ✅ Tests complete FastAPI application stack (routing, middleware, dependencies)
- ✅ Fast execution (~milliseconds vs seconds for live servers)
- ✅ Isolated per-test databases via dependency overrides
- ✅ Reliable without network dependencies or port conflicts
- ✅ Easy to mock external services and background tasks

### Implementation

**Location**: `Backend/tests/conftest.py` provides all necessary fixtures

**Key Components**:
- `app` fixture - FastAPI app with per-test SQLite DB override
- `client`/`http_client` fixtures - Synchronous TestClient for in-process requests
- `async_client`/`async_http_client` fixtures - Async httpx.AsyncClient with ASGI transport
- `url_builder` fixture - Static route mapping (no network discovery needed)
- Database dependency override for `core.database.get_async_session`

**Usage**:
```bash
# Run all backend tests (in-process)
cd Backend
python -m pytest

# Run with professional test management
python scripts/test_management.py --category api
```

### Example: In-Process Testing with Dependency Overrides

**✅ In-Process Testing (TestClient with dependency overrides)**:
```python
def test_login_with_db_override(client: TestClient):
    response = client.post("/api/auth/login", data=data)  # In-process via ASGI
    assert response.status_code == 200
```

**✅ Async In-Process Testing (httpx.AsyncClient with ASGI)**:
```python
async def test_login_async(async_client: httpx.AsyncClient, url_builder):
    url = url_builder.url_for("auth_login")
    response = await async_client.post(url, data=data)  # In-process via ASGI
    assert response.status_code == 200
```

## End-to-End Testing with Cypress

### Philosophy

Cypress provides the third tier of our testing strategy - true end-to-end testing that validates complete user workflows from frontend to backend. This approach:

- ✅ Tests complete user journeys and business flows
- ✅ Validates frontend-backend integration in real browser environments
- ✅ Catches UI/UX issues and cross-browser compatibility problems
- ✅ Tests actual user interactions (clicks, typing, navigation)
- ✅ Validates data persistence and state management across page loads

### Implementation

**Location**: `/cypress/` directory with E2E test suites

**Key Components**:
- `cypress.config.ts` - Cypress configuration with environment variables
- `cypress/e2e/` - End-to-end test scenarios
- `cypress/support/` - Custom commands and global configuration
- `cypress/fixtures/` - Test data and sample files

**Test Scenarios**:
- Authentication flows (register, login, logout)
- Video learning workflows (upload, play, vocabulary interaction)
- User progress tracking and vocabulary games
- Subtitle processing and filtering features

**Usage**:
```bash
# Run E2E tests in headless mode
npm run e2e

# Open Cypress Test Runner for interactive debugging
npm run e2e:open

# Run specific test file
npx cypress run --spec "cypress/e2e/auth-flow.cy.ts"
```

### Environment Setup for E2E Tests

E2E tests require both frontend and backend to be running:

```bash
# Terminal 1: Start backend
cd Backend && python run_backend.py

# Terminal 2: Start frontend  
cd Frontend && npm run dev

# Terminal 3: Run E2E tests
npm run e2e
```

## Professional Test Management

### Test Categorization

Tests are organized by markers for targeted execution:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.contract` - Contract-driven tests
- `@pytest.mark.slow` - Slow tests (with extended timeout)
- `@pytest.mark.xfail` - Expected to fail (known issues)

### Handling Failing Tests

**❌ Unprofessional Approach**: Maintaining a list of "passing tests" and ignoring failures

**✅ Professional Approach**: Proper test management with clear categorization

```bash
# Run all tests with comprehensive reporting
python scripts/test_management.py

# Run only failed tests from last run
python scripts/test_management.py --failed-only

# Run by category
python scripts/test_management.py --category unit
```

**For Expected Failures**:
```python
@pytest.mark.xfail(reason="Known issue: API endpoint under development")
def test_new_feature():
    # Test implementation
    pass
```

## Coverage Strategy

### Comprehensive Coverage

Our coverage configuration includes all production code:

```ini
# .coveragerc
[run]
omit =
    # Only exclude non-source code
    api_venv/*
    venv/*
    tests/*
    alembic/versions/*

[report]
fail_under = 80
show_missing = true
```

**✅ Includes**: `services/`, `database/`, `api/`, `core/` - all business logic
**❌ Excludes**: Only virtual environments, tests, and generated code

### Running Coverage

```bash
cd Backend
python -m pytest --cov=core --cov=api --cov=services --cov=database --cov-report=html
```

## Cross-Platform Tooling

### Unified Script Approach

Instead of maintaining duplicate `.sh` and `.ps1` scripts, we use Python for cross-platform compatibility:

**✅ New Unified Scripts**:
- `scripts/test_management.py` - Professional test runner
- `scripts/run_postgres_tests.py` - PostgreSQL integration tests  
- `scripts/generate_typescript_client.py` - TypeScript client generation

**Usage**:
```bash
# Works on Windows, macOS, and Linux
python scripts/test_management.py
python scripts/run_postgres_tests.py
python scripts/generate_typescript_client.py
```

### Migration from Legacy Scripts

**Deprecated Scripts** (still work but will be removed):
- `generate-ts-client.sh` / `generate-ts-client.bat`
- `Backend/scripts/run_tests_postgres.sh` / `run_tests_postgres.ps1`

## API Contract Management

### Single Source of Truth

- **Canonical OpenAPI Spec**: `/openapi_spec.json` (root level)
- **Generated From**: FastAPI application
- **Used By**: Frontend TypeScript client generation

### Generation Process

```bash
# Generate OpenAPI spec and TypeScript client
python scripts/generate_typescript_client.py
```

This script:
1. Exports OpenAPI spec from running FastAPI backend
2. Saves to canonical location (`/openapi_spec.json`)
3. Generates TypeScript client in `Frontend/src/client/`

## Frontend Testing

### SRT API Integration

The frontend uses the backend as the single source of truth for SRT parsing:

**✅ Professional Approach**:
```typescript
import { srtApi } from '../utils/srtApi'
const result = await srtApi.parseSRTContent(srtContent)
```

**❌ Old Approach** (duplicate logic):
```typescript
// Duplicate parsing logic - removed
function parseSRT(content) { /* ... */ }
```

### Test Structure

```
Frontend/src/test/
├── subtitle-parsing.test.ts    # API integration tests
├── contract/                   # Contract tests
└── utils/                      # Test utilities
```

## Best Practices

### ✅ DO:
- Use contract-driven testing for API endpoints
- Categorize tests with appropriate markers
- Address failing tests immediately (fix or mark with `@pytest.mark.xfail`)
- Use unified Python scripts for tooling
- Maintain comprehensive test coverage
- Use the backend as single source of truth for business logic

### ❌ DON'T:
- Maintain lists of "passing tests" while ignoring failures
- Exclude critical code (services, database) from coverage
- Create duplicate cross-platform scripts
- Duplicate business logic between frontend and backend
- Use TestClient for integration testing (bypasses HTTP layer)

## Continuous Integration

For CI/CD systems, use the unified scripts:

```yaml
# Professional CI configuration
- name: Run comprehensive tests
  run: python scripts/test_management.py --timeout 600

- name: Run PostgreSQL integration tests  
  run: python scripts/run_postgres_tests.py

- name: Check test coverage
  run: python -m pytest --cov=core --cov=api --cov=services --cov=database --cov-fail-under=80
```

## Historical Context

This strategy addresses several architectural issues that were previously present:

1. **Removed unprofessional test practices** (hardcoded passing test lists)
2. **Fixed coverage exclusions** (now includes services and database)
3. **Consolidated duplicate scripts** (unified Python approach)
4. **Eliminated code duplication** (single source of truth for SRT parsing)
5. **Standardized documentation** (this consolidated guide)

The result is a professional, maintainable, and reliable testing infrastructure that supports confident development and deployment.

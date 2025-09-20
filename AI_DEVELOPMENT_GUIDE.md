# AI Development Guide

This document consolidates guidance for AI coding assistants working on the LangPlug project. It replaces multiple scattered AI-specific configuration files with a unified, professional approach.

## Project Overview

LangPlug is a German language learning platform with a FastAPI backend and React frontend. The project follows professional development practices including:

- **Contract-Driven Development (CDD)** for API testing
- **Professional test management** (no hardcoded passing test lists)
- **Single source of truth** for business logic and specifications
- **Cross-platform tooling** using Python scripts
- **Comprehensive test coverage** including services and database layers

## Development Workflow

### Essential Commands

```bash
# Professional test management
python scripts/test_management.py                    # Run all tests
python scripts/test_management.py --category unit   # Run unit tests
python scripts/test_management.py --failed-only     # Re-run failed tests

# Cross-platform tooling
python scripts/run_postgres_tests.py               # PostgreSQL integration tests
python scripts/generate_typescript_client.py       # OpenAPI client generation

# Standard development
cd Backend && python run_backend.py                # Start backend server
cd Frontend && npm run dev                          # Start frontend dev server

# Three-tier testing approach
cd Backend && pytest                               # Unit/integration tests (in-memory)
cd Frontend && npm test                             # Frontend contract tests (mocked)
npm run e2e                                         # End-to-end tests (Cypress)
```

### Build/Test Commands (from AGENTS.md)

```bash
# Backend server (Windows/PowerShell from WSL)
powershell.exe -Command "python E:\Users\Jonandrop\IdeaProjects\LangPlug\Backend\run_backend.py"

# Backend server (Linux/WSL)
cd Backend && python run_backend.py

# Testing
cd Backend && pytest                               # All tests
cd Backend && pytest tests/api/test_auth_endpoints.py  # Single test file
cd Backend && pytest --cov=core --cov=api --cov=services  # With coverage

# Code quality
cd Backend && ruff check .                         # Linting
cd Backend && ruff format .                        # Formatting

# Frontend
cd Frontend && npm run dev                         # Development server
```

## Code Style Guidelines

### Python Formatting (from AGENTS.md)
- **Line length**: 88 characters
- **String quotes**: Double quotes for strings
- **Docstrings**: Google-style docstrings
- **Imports**: isort sorting (first-party: api, core, database, services, tests)

### Naming Conventions
- **Variables/functions**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_CASE

### Type Hints
- Use explicit type hints for all functions
- Prefer Pydantic models for data structures
- Use UUID for user IDs (not integers)

### Error Handling
- Use structured exception handling
- Log errors appropriately with context
- Return consistent error response formats

## Testing Best Practices

### In-Memory Testing Strategy
- **✅ Use**: FastAPI TestClient and httpx.AsyncClient with ASGI transport for fast, reliable in-process tests
- **✅ Use**: Dependency overrides (e.g., `get_async_session`) with per-test SQLite databases
- **✅ Use**: Mock external services and long-running processes in tests
- **❌ Avoid**: Live HTTP servers or network calls in unit/integration tests

### Professional Test Management
- **✅ Use**: `python scripts/test_management.py` for comprehensive test runs
- **❌ Avoid**: Hardcoded lists of "passing tests" 
- **Expected Failures**: Mark with `@pytest.mark.xfail(reason="Clear explanation")`
- **Test Categories**: Use markers (`@pytest.mark.unit`, `@pytest.mark.contract`, etc.)

### In-Process Testing with Dependency Overrides
- Use TestClient/httpx.AsyncClient with ASGI transport for fast in-process testing
- Override dependencies like `get_async_session` for isolated test databases
- Use fixtures from `tests/conftest.py` (app, client, async_client, url_builder)
- Mock external services and background tasks to eliminate network dependencies

### End-to-End Testing with Cypress
- **✅ Use**: Cypress for complete user workflow validation
- **✅ Use**: Real browser testing for UI/UX validation and cross-browser compatibility
- **✅ Use**: Custom commands for authentication and common workflows
- **❌ Avoid**: E2E tests for unit-level logic (use fast in-memory tests instead)

### Coverage Requirements
- **Minimum**: 80% coverage
- **Includes**: services/, database/, api/, core/ directories
- **Excludes**: Only tests, virtual environments, and generated code

## Architecture Principles

### Single Source of Truth
- **Backend**: Authoritative for all business logic (e.g., SRT parsing)
- **Frontend**: Consumes APIs, minimal business logic duplication
- **OpenAPI Spec**: `/openapi_spec.json` is canonical
- **Test Helpers**: Unified helpers in `tests/auth_helpers.py`

### Database Patterns
- Use async SQLAlchemy sessions consistently
- Implement `UserManager.parse_id()` for UUID handling
- Apply migrations with Alembic

### Cross-Platform Compatibility
- Use Python scripts for tooling (not shell-specific scripts)
- WSL/Windows interoperability: Use `powershell.exe -Command` when needed

## AI Assistant Specific Guidelines

### For Claude (from CLAUDE.md)
- **Context Management**: Save important context using the memory system
- **Tool Usage**: Prefer reading files before editing, use appropriate tools for tasks
- **Code Changes**: Generate runnable code immediately, add necessary imports
- **Error Handling**: Fix issues systematically, address root causes

### For CRUSH (from CRUSH.md)
- **File Operations**: Always verify file existence before operations
- **Test Integration**: Use proper pytest fixtures and markers
- **Documentation**: Keep inline comments concise but informative

### For Qwen Code CLI (from QWEN_CODE_CLI_CONFIG.md)
- **Project Structure**: Follow established directory conventions
- **Dependency Management**: Use requirements.txt with specific versions
- **Configuration**: Respect existing config files (pytest.ini, pyproject.toml)

## Common Pitfalls to Avoid

### ❌ Unprofessional Practices
- Maintaining hardcoded lists of passing tests
- Excluding critical code from test coverage
- Creating duplicate business logic
- Using platform-specific scripts for tooling
- Ignoring failing tests

### ✅ Professional Practices
- Address failing tests immediately (fix or mark as expected failure)
- Use comprehensive test coverage including services and database
- Maintain single source of truth for business logic
- Use cross-platform Python tooling
- Follow Contract-Driven Development for API testing

## File Organization

### Key Directories
```
LangPlug/
├── Backend/
│   ├── api/                    # API routes and endpoints
│   ├── core/                   # Core application logic
│   ├── database/               # Database models and repositories
│   ├── services/               # Business logic services
│   ├── tests/                  # Comprehensive test suite
│   └── utils/                  # Utility functions (e.g., SRT parsing)
├── Frontend/
│   ├── src/
│   │   ├── client/            # Generated API client
│   │   ├── test/              # Frontend tests
│   │   └── utils/             # Frontend utilities (API clients)
├── scripts/                    # Cross-platform Python scripts
└── docs/                      # Documentation
```

### Configuration Files
- **pytest.ini**: Test configuration
- **pyproject.toml**: Python project metadata
- **requirements.txt**: Python dependencies
- **openapi_spec.json**: Canonical API specification
- **.coveragerc**: Test coverage configuration

## Migration from Legacy Approaches

### Deprecated Files/Patterns
- ~~`run_passing_tests.py`~~ → Use `scripts/test_management.py`
- ~~`generate-ts-client.{sh,bat}`~~ → Use `scripts/generate_typescript_client.py`
- ~~`Backend/scripts/run_tests_postgres.{sh,ps1}`~~ → Use `scripts/run_postgres_tests.py`
- ~~`Frontend/src/test/utils.tsx` (console testing)~~ → Use proper Vitest tests
- ~~Duplicate SRT parsing in frontend~~ → Use backend API via `srtApi` client

### Documentation Consolidation
- **Primary**: `docs/TESTING_STRATEGY.md` - Comprehensive testing approach
- **OpenAPI**: `OPENAPI_SPECIFICATION.md` - API specification management
- **Scripts**: `SCRIPT_MIGRATION.md` - Migration from duplicate scripts
- **This Guide**: `AI_DEVELOPMENT_GUIDE.md` - Unified AI assistant guidance

## Conclusion

This unified guide replaces the fragmented AI-specific configuration files with a cohesive development approach. Follow these guidelines to maintain the professional, consistent, and maintainable codebase that LangPlug has become through its architectural cleanup efforts.

For specific technical details, refer to:
- `docs/TESTING_STRATEGY.md` for testing approach
- `Backend/tests/CONTRACT_DRIVEN_DEVELOPMENT.md` for CDD implementation
- `docs/tooling/contract_and_test_tooling.md` for updated tooling commands

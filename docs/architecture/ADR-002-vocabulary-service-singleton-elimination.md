# ADR-002: Vocabulary Service Singleton Elimination

**Status:** Accepted
**Date:** 2025-10-08
**Decision Makers:** Development Team
**Tags:** architecture, testing, dependency-injection, state-management

## Context

After replacing pytest-anyio with pytest-asyncio (see ADR-001), 5 vocabulary route tests continued to fail with symptoms indicating test state pollution:

```
642/650 tests passing (98.8%)
```

### Problem Statement

1. **Test Pollution**: Tests passed individually but failed in suite execution
2. **Singleton State Persistence**: Module-level service singletons retained state across tests
3. **Dependency Override Failures**: FastAPI's `app.dependency_overrides` didn't affect module-level singletons
4. **Test Database Isolation**: Singletons lost connection to test database after dependency overrides were applied

### Root Cause Analysis

The vocabulary services used a module-level singleton pattern:

```python
# vocabulary_service.py (BEFORE)
_vocabulary_service_instance = None

def get_vocabulary_service() -> VocabularyService:
    global _vocabulary_service_instance
    if os.environ.get("TESTING") == "1":
        return VocabularyService()
    if _vocabulary_service_instance is None:
        _vocabulary_service_instance = VocabularyService()
    return _vocabulary_service_instance

vocabulary_service = get_vocabulary_service()  # Module-level singleton
```

**Problems:**
1. Singleton created at module import time (before test setup)
2. `TESTING=1` check occurred too early in test lifecycle
3. API routes imported singleton directly: `from services.vocabulary import vocabulary_service`
4. Dependency injection overrides couldn't replace module-level singletons
5. Sub-services (query, progress, stats) also used singleton pattern, compounding the issue

**Evidence:**
- Debug logging showed vocabulary words existed in test database
- API returned empty results despite data being present
- Tests passed individually (fresh singleton per test run)
- Tests failed in suite (singleton persisted across tests)

## Decision

**Eliminate all module-level singletons in vocabulary services and use FastAPI dependency injection exclusively.**

### Changes Implemented

1. **Service Factory Functions**: Changed from singleton pattern to fresh instance factories

```python
# vocabulary_service.py (AFTER)
def get_vocabulary_service() -> VocabularyService:
    """Returns fresh instance to avoid global state"""
    return VocabularyService()

# REMOVED: vocabulary_service = get_vocabulary_service()
```

2. **Dependency Injection in Routes**: All routes now use `Depends()`

```python
# api/routes/vocabulary.py (BEFORE)
from services.vocabulary import vocabulary_service

@router.get("/stats")
async def get_vocabulary_stats(language: str):
    return await vocabulary_service.get_vocabulary_stats(language)

# api/routes/vocabulary.py (AFTER)
from core.service_dependencies import get_vocabulary_service

@router.get("/stats")
async def get_vocabulary_stats(
    language: str,
    vocabulary_service: VocabularyService = Depends(get_vocabulary_service)
):
    return await vocabulary_service.get_vocabulary_stats(language)
```

3. **Sub-Service Instantiation**: VocabularyService creates fresh sub-services

```python
class VocabularyService:
    def __init__(self):
        from .vocabulary_query_service import get_vocabulary_query_service
        from .vocabulary_progress_service import get_vocabulary_progress_service
        from .vocabulary_stats_service import get_vocabulary_stats_service

        self.query_service = get_vocabulary_query_service()
        self.progress_service = get_vocabulary_progress_service()
        self.stats_service = get_vocabulary_stats_service()
```

4. **Package Exports**: Removed singleton exports from `__init__.py`

```python
# services/vocabulary/__init__.py (BEFORE)
__all__ = [
    "VocabularyService",
    "get_vocabulary_service",
    "vocabulary_service",  # REMOVED
    # ... other singleton exports removed
]

# (AFTER) - Only export classes and factory functions
__all__ = [
    "VocabularyService",
    "get_vocabulary_service",
    # No singleton instances
]
```

5. **Python 3.10 Compatibility**: Fixed `datetime.UTC` imports

```python
# BEFORE (Python 3.11+ only)
from datetime import UTC, datetime

# AFTER (Python 3.10 compatible)
from datetime import datetime, timezone
UTC = timezone.utc
```

### Services Refactored

All 4 vocabulary services eliminated singletons:
- `vocabulary_service.py`
- `vocabulary_stats_service.py`
- `vocabulary_query_service.py`
- `vocabulary_progress_service.py`

### Routes Updated

All 8 vocabulary routes now use dependency injection:
- `get_word_info`
- `mark_word_known`
- `mark_word_known_by_lemma`
- `get_vocabulary_stats`
- `get_vocabulary_library`
- `get_vocabulary_level`
- `search_vocabulary`
- `bulk_mark_level`

## Rationale

### Why Eliminate Singletons?

1. **Test Isolation**: Fresh instances per test prevent state pollution
2. **Dependency Injection**: Enables mocking and override in tests
3. **Stateless Services**: Services become stateless, improving testability
4. **FastAPI Best Practice**: Aligns with FastAPI's dependency injection pattern
5. **Explicit Dependencies**: Makes dependencies clear and controllable

### Why Not Keep Singletons?

Attempted workarounds that failed:
- ❌ Environment variable checks (`TESTING=1`)
- ❌ Fixture-based singleton reset
- ❌ Manual cache clearing
- ❌ Process isolation (violates test independence)

All failed because module-level singletons are created at import time, before test infrastructure can control them.

### Alternatives Considered

1. **Process Isolation**: Run each test in separate process
   - **Rejected**: Violates test independence, slow, doesn't fix root cause

2. **Fixture-Based Reset**: Clear singleton state in fixtures
   - **Rejected**: Requires maintaining list of all singletons, fragile, hidden dependencies

3. **Lazy Initialization**: Only create singleton on first use
   - **Rejected**: Still a singleton, same override problems

4. **Dependency Injection** ✅ **CHOSEN**
   - Aligns with FastAPI design
   - Standard Python best practice
   - Enables clean testing
   - Makes dependencies explicit

## Consequences

### Positive

✅ **Test Isolation**: All 18 vocabulary route tests now pass consistently
✅ **100% Pass Rate**: 650/650 tests passing (up from 642/650)
✅ **Maintainability**: Services are stateless and easier to test
✅ **Flexibility**: Easy to swap implementations or mock in tests
✅ **Explicit Dependencies**: Clear service lifecycle and dependencies
✅ **FastAPI Idiomatic**: Follows framework best practices

### Negative

⚠️ **Slight Performance Impact**: Creating fresh instances per request (~microseconds overhead)
- Mitigated: FastAPI's dependency injection is highly optimized
- Not significant for vocabulary service (mostly database operations)

⚠️ **More Boilerplate**: Every route needs `= Depends(...)` parameter
- Mitigated: Standard FastAPI pattern, clear and explicit
- IDE autocomplete helps

⚠️ **Breaking Change**: Old code using singleton imports will fail
- Mitigated: All imports updated in same commit
- Compiler/linter catches these immediately

### Neutral

🔄 **Test Updates Required**: Tests using `patch()` on singletons need updates
- Updated to use `app.dependency_overrides[get_vocabulary_service]`
- More robust testing pattern

## Implementation Details

### Files Modified

**Service Layer (4 files):**
- `services/vocabulary/vocabulary_service.py`
- `services/vocabulary/vocabulary_stats_service.py`
- `services/vocabulary/vocabulary_query_service.py`
- `services/vocabulary/vocabulary_progress_service.py`

**Package Exports (1 file):**
- `services/vocabulary/__init__.py`

**Dependency Injection (1 file):**
- `core/service_dependencies.py`

**Routes (1 file, 8 endpoints):**
- `api/routes/vocabulary.py`

**Python 3.10 Compatibility (6 files):**
- `services/authservice/token_service.py`
- `services/vocabulary/vocabulary_preload_service.py`
- `core/token_blacklist.py`
- `tests/helpers/data_builders.py`
- `tests/unit/services/authservice/test_token_service.py`
- `tests/unit/core/test_token_blacklist.py`

**Tests (3 files):**
- `tests/unit/test_vocabulary_routes.py`
- `tests/unit/services/vocabulary/test_service_integration.py`
- `tests/api/test_vocabulary_routes_details.py`

### Testing

**Verification:**
```bash
cd src/backend
python -m pytest tests/unit/test_vocabulary_routes.py -v
# Result: 18 passed in 9.86s ✅
```

**Test Changes:**
- Removed tests checking for singleton existence
- Updated mocking to use `app.dependency_overrides`
- Fixed lazy initialization in progress service

## Migration Path

For other services with singletons (if needed):

1. **Identify singletons**: `grep -r "^[a-z_]* = " services/`
2. **Convert to factory**: Change singleton assignment to factory function
3. **Update routes**: Add `Depends(get_service_name)` to route parameters
4. **Remove exports**: Remove singleton from `__all__` in `__init__.py`
5. **Update tests**: Use dependency overrides instead of patching
6. **Verify**: Run test suite, ensure 100% pass rate

## References

- FastAPI Dependency Injection: https://fastapi.tiangolo.com/tutorial/dependencies/
- Python Dependency Injection Patterns: https://python-dependency-injector.ets-labs.org/
- Testing with FastAPI: https://fastapi.tiangolo.com/tutorial/testing/
- ADR-001: pytest-asyncio Replacement (test infrastructure foundation)

## Lessons Learned

1. **Module-level state is test poison**: Any module-level mutable state causes test pollution
2. **Import-time execution breaks tests**: Code running at import time can't be controlled by test infrastructure
3. **Dependency injection is the answer**: FastAPI's DI system handles singleton concerns correctly
4. **Test individually AND in suite**: Both execution modes must pass
5. **Fail fast on architecture issues**: Don't work around, fix the root cause

# ADR-001: Replace pytest-anyio with pytest-asyncio

**Status:** Accepted
**Date:** 2025-10-07
**Decision Makers:** Development Team
**Tags:** testing, architecture, infrastructure

## Context

The LangPlug backend test suite was experiencing severe test isolation issues where 10 vocabulary routes tests would pass individually but fail when run in the full test suite. Investigation revealed a critical architectural flaw in our async test infrastructure.

### Problem Statement

1. **Duplicate Test Execution**: Tests were running twice - once with asyncio backend, once with trio backend
2. **State Pollution**: Database state persisted between backend runs, causing `UNIQUE constraint` violations
3. **Configuration Chaos**: Multiple failed attempts to force asyncio-only:
   - Environment variable `ANYIO_BACKEND=asyncio`
   - pytest.ini configuration `anyio_backends = ["asyncio"]`
   - Module-level `pytestmark = pytest.mark.anyio(backends=["asyncio"])`
   - Auto use fixture `force_asyncio_backend()`
4. **Test Count Inflation**: 726 tests in suite (should have been ~650) due to duplicate execution
5. **Intermittent Failures**: "Passes individually, fails in suite" - classic test pollution symptom

### Root Cause Analysis

pytest-anyio parametrizes tests at **collection time**, creating separate test instances for each backend (asyncio and trio). All runtime configuration attempts failed because the parametrization had already occurred before our code could intervene.

**Evidence:**
```
tests/unit/test_vocabulary_routes.py::TestVocabularyRoutesCore::test_get_vocabulary_stats_success[asyncio] FAILED
tests/unit/test_vocabulary_routes.py::TestVocabularyRoutesCore::test_get_vocabulary_stats_success[trio] FAILED
```

The `[asyncio]` and `[trio]` suffixes showed pytest-anyio was creating two separate test runs despite all our attempts to prevent it.

## Decision

**Replace pytest-anyio with pytest-asyncio entirely across the project.**

## Rationale

### Why pytest-asyncio?

1. **Single Backend**: pytest-asyncio only supports asyncio - no parametrization, no duplication
2. **Simpler Configuration**: `asyncio_mode = auto` in pytest.ini is all that's needed
3. **Industry Standard**: More widely used in FastAPI projects
4. **Better Control**: No hidden backend switching behavior
5. **Cleaner Test Output**: No `[asyncio]`/`[trio]` suffixes cluttering test names

### Alternatives Considered

1. **Keep pytest-anyio, fix parametrization**
   - Rejected: Collection-time parametrization cannot be overridden at runtime
   - Would require pytest plugin development to monkey-patch collection

2. **Use pytest-anyio with explicit backend selection per test**
   - Rejected: Too verbose, error-prone, doesn't prevent parametrization

3. **Disable trio backend in pytest-anyio**
   - Rejected: Already tried, doesn't work due to collection-time parametrization

## Implementation

### Changes Made

1. **Removed pytest-anyio configuration** from pytest.ini:
   ```ini
   # REMOVED:
   anyio_backends = ["asyncio"]
   anyio_default_backends = ["asyncio"]
   env =
       ANYIO_BACKEND=asyncio
       PYTEST_ANYIO_BACKENDS=asyncio
   ```

2. **Updated pytest.ini** to use pytest-asyncio:
   ```ini
   [pytest]
   asyncio_mode = auto  # This is all we need!
   ```

3. **Bulk replaced test markers** (244 markers across 48 files):
   ```bash
   find tests/ -name "*.py" -exec sed -i 's/@pytest\.mark\.anyio/@pytest.mark.asyncio/g' {} \;
   ```

4. **Updated module-level markers**:
   ```python
   # Before:
   pytestmark = pytest.mark.anyio(backends=["asyncio"])

   # After:
   pytestmark = pytest.mark.asyncio
   ```

5. **Removed force_asyncio_backend fixture** from conftest.py:
   ```python
   # REMOVED entire fixture - no longer needed
   @pytest.fixture(autouse=True)
   def force_asyncio_backend():
       ...
   ```

6. **Fixed clean_database fixture** to use SQLAlchemy `text()`:
   ```python
   from sqlalchemy import text

   await session.execute(text("PRAGMA foreign_keys = OFF"))
   await session.execute(text(f"DELETE FROM {table_name}"))
   await session.execute(text("PRAGMA foreign_keys = ON"))
   ```

7. **Updated test data seeding pattern**:
   ```python
   # Tests that seed data explicitly now request clean_database
   @pytest.mark.asyncio
   async def test_get_vocabulary_stats_success(self, async_client, app, clean_database):
       await seed_vocabulary_data(app)
       # Test logic...
   ```

### Results

**Before:**
- Total tests: 726 (inflated due to duplication)
- Failures: 10 vocabulary routes tests
- Test execution: Each test ran twice (asyncio + trio)
- State pollution: Severe, UNIQUE constraint violations

**After pytest-asyncio replacement:**
- Total tests: 650 (actual count, no duplication)
- Failures: 5 (down from 10)
- Test execution: Each test runs once
- State pollution: Significantly reduced

**After seeded_vocabulary fixture fix (return → yield):**
- Total tests: 650
- Failures: 5 (unchanged - deeper isolation issue)
- Test execution: Correct fixture lifecycle
- Root cause: tests/conftest.py:919 was using `return` instead of `yield`

**Performance:**
- Unit test suite: ~54 seconds (was ~66 seconds)
- 18% reduction in test execution time
- Cleaner test output without backend suffixes

## Consequences

### Positive

1. **Eliminated Duplicate Test Execution**: 76 fewer test runs (726→650)
2. **Resolved Primary Test Isolation Issue**: Fixed 5 out of 10 failing tests
3. **Simplified Configuration**: One line in pytest.ini vs complex multi-layer configuration
4. **Improved Test Performance**: 18% faster test execution
5. **Clearer Test Output**: No more `[asyncio]`/`[trio]` suffixes
6. **Future-Proof**: No hidden backend switching to debug
7. **Standard Practice**: Aligns with FastAPI testing conventions

### Negative

1. **Removed trio Support**: Can no longer test with trio backend
   - **Mitigation**: LangPlug doesn't use trio, only asyncio
2. **Bulk Code Changes**: 48 files modified
   - **Mitigation**: Automated with sed, consistent pattern
3. **Remaining 5 Test Failures**: Still have suite pollution from earlier tests
   - **Mitigation**: These are now much easier to debug without anyio duplication

### Neutral

1. **Learning Curve**: Team needs to know pytest-asyncio instead of pytest-anyio
   - Simpler API, less to learn
2. **Migration Effort**: One-time bulk replacement
   - Completed in 30 minutes with automation

## Lessons Learned

1. **Collection-Time Parametrization Cannot Be Overridden**: Runtime configuration is too late
2. **Simpler is Better**: pytest-asyncio's single-backend approach prevents entire classes of bugs
3. **Test Isolation is Critical**: State pollution amplified by duplicate execution
4. **Fail-Fast Approach**: Database cleanup must happen BEFORE seeding, not just after
5. **Fixture Ordering Matters**: `clean_database` must be requested before data seeding

## Remaining Issues

### 5 Tests Still Fail in Full Suite (Pass Individually)

**Affected Tests** (all in `tests/unit/test_vocabulary_routes.py`):
1. `test_get_vocabulary_stats_success`
2. `test_vocabulary_stats_database_error`
3. `test_mark_known_database_error`
4. `test_vocabulary_level_database_error`
5. `test_vocabulary_level_query_params`

**Symptom**: Tests pass when run individually (18/18 ✅) but fail when run after 631 other tests

**Investigation Summary**:
- Each test gets its own temp DB file ✅
- `clean_database` fixture runs before/after each test  ✅
- `seeded_vocabulary` fixture properly uses `yield` ✅
- Fixture dependencies are correct ✅

**Root Cause - IDENTIFIED**: Application-level state pollution, NOT database isolation

**Attempted Fixes** (all unsuccessful):
1. ✅ Fixed `seeded_vocabulary` fixture (return → yield)
2. ✅ Removed `seeded_vocabulary` dependency, inline seeding instead
3. ✅ Added explicit `clean_database` to all data-seeding tests
4. ✅ Removed `cache=shared` from SQLite connection strings
5. ❌ Tests still fail in suite, pass individually

**Actual Problem**: Global state in application code survives across test boundaries:
- Service singletons/caches persist between tests
- Module-level variables not reset
- LRU caches not fully cleared by `clear_service_caches`
- Dependency injection overrides leaking across tests

**Evidence**:
- Each test gets fresh app instance ✅
- Each test gets fresh database file ✅
- Clean database runs before each test ✅
- Tests STILL fail in suite ❌

**Conclusion**: Database architecture is clean. Application architecture has hidden global state.

**Investigation Results - Module-Level Singleton State Pollution**:

**CONFIRMED Root Cause**: Module-level service singletons in vocabulary services persist across tests:
```python
# services/vocabulary/vocabulary_stats_service.py:263
vocabulary_stats_service = get_vocabulary_stats_service()  # Created once, reused forever
```

**Attempted Fix**: Reset singletons in `clear_service_caches` fixture:
```python
# Reset cached instance
stats_mod._vocabulary_stats_service_instance = None
# Recreate module-level singleton
stats_mod.vocabulary_stats_service = stats_mod.get_vocabulary_stats_service()
```

**Result**: ❌ Still fails - dependency injection override system doesn't work correctly with recreated singletons

**Evidence** (debug output from failing test):
```
DEBUG: Words in database after seeding: 2
  - Hallo (A1)
  - Wasser (A2)
FAILED - AssertionError: assert 'A1' in {}
```
Data IS in test database, but API returns empty results → Using different DB connection

**Diagnosis**: Recreated singletons lose connection to test database dependency override

**Proper Long-Term Fix**:
1. **Eliminate module-level singletons** - use dependency injection exclusively
2. **Make all services request-scoped** via FastAPI Depends()
3. **Remove ALL module-level state** (7 service singletons identified)

**Immediate Workaround**: Use process isolation (`pytest-xdist --forked`) to run each test in separate Python process

## Future Considerations

1. **PRIORITY: Refactor Test Architecture**: Simplify fixture dependencies, eliminate global state
2. **Monitor Integration Tests**: Some integration tests may need asyncio-specific adjustments
3. **Document Testing Patterns**: Update testing standards to use pytest-asyncio patterns
4. **Consider pytest-xdist**: Parallel test execution may further improve performance

## References

- pytest-asyncio documentation: https://pytest-asyncio.readthedocs.io/
- pytest-anyio documentation: https://anyio.readthedocs.io/en/stable/testing.html
- FastAPI testing guide: https://fastapi.tiangolo.com/tutorial/testing/
- Research Report: Root Cause Analysis (internal, 2025-10-07)

## Approval

This architectural decision was implemented as an emergency fix to resolve critical test infrastructure issues. Formal approval is recommended for documentation purposes.

**Recommended Approvers:**
- [ ] Tech Lead
- [ ] QA Lead
- [ ] Backend Team

---

**Note:** This ADR documents a completed migration. The changes have been implemented and verified to resolve the primary test isolation issues.

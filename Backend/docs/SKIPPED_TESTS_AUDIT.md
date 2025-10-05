# Skipped Tests Audit Report

**Created**: 2025-10-05
**Purpose**: Audit all 42 skipped/failing tests in the Backend test suite
**Task**: Test Architecture Task 9 - Phase 1
**Status**: Audit Complete

---

## Executive Summary

**Total Skipped Tests**: 42

**Distribution**:

- Integration tests: 25 (60%)
- Performance tests: 6 (14%)
- Services tests: 5 (12%)
- API tests: 3 (7%)
- Unit tests: 3 (7%)

**Primary Reasons for Skipping**:

1. **Missing AI/ML Dependencies** (16 tests, 38%) - Whisper, Torch, SpaCy, NeMo models
2. **Architecture Refactoring** (5 tests, 12%) - Tests need updates after code changes
3. **Performance/Manual Tests** (6 tests, 14%) - Should be moved to manual test suite
4. **Data Dependency Issues** (4 tests, 10%) - Tests fail when no test data available
5. **Implementation Gaps** (4 tests, 10%) - Features not yet implemented
6. **Mock/Test Infrastructure** (4 tests, 10%) - Mock setup issues
7. **Design Conflicts** (3 tests, 7%) - Test assumptions conflict with implementation

---

## Category 1: Missing AI/ML Dependencies (16 tests) 🔧 FIX

**Action**: Document requirements OR make optional with graceful skip

### Whisper/Transcription Models (5 tests)

1. `tests/services/test_transcription_services.py::*` - "Requires whisper dependency not available in CI"
2. `tests/unit/test_real_srt_generation.py::*` - "whisper dependency not installed"
3. `tests/integration/test_ai_service_integration.py` (3 tests) - Whisper/transcription services

**Recommendation**: Add documentation about optional AI dependencies. Use `pytest.importorskip()` for cleaner handling.

### Torch/Translation Models (3 tests)

4. `tests/unit/services/processing/test_chunk_translation_service.py:157` - "Requires torch dependency not available in CI"
5. `tests/integration/test_ai_service_integration.py:111` - Translation service model download
6. `tests/integration/test_ai_service_integration.py:132` - NLLB service model download/memory

**Recommendation**: Make translation tests conditional on torch availability. Document memory requirements for NLLB.

### SpaCy Models (2 tests)

7. `tests/integration/test_api_contract_validation.py:94` - "Requires spaCy de_core_news_lg model not available in CI"
8. `tests/integration/test_api_contract_validation.py:312` - Same as above

**Recommendation**: Download spaCy model in CI setup OR skip gracefully with clear message.

### NeMo Toolkit (1 test)

9. `tests/integration/test_ai_service_minimal.py:87` - "NeMo toolkit not installed"

**Recommendation**: Document NeMo as optional dependency. Use `pytest.importorskip()`.

### AI Service Integration (5 tests)

10-14. `tests/integration/test_ai_service_minimal.py` (4 skipif tests)

- Lines 16, 40, 52, 64 - Conditional on service availability

**Recommendation**: These are properly using `skipif` for optional features. Keep as-is with documentation.

---

## Category 2: Architecture Refactoring (5 tests) ⚠️ FIX OR DELETE

**Action**: Update tests for new architecture OR delete if obsolete

### Transcription Service Refactoring (4 tests)

1. `tests/services/test_chunk_processing_service.py:66` - No reason given, likely refactoring
2. `tests/services/test_chunk_processing_service.py:149` - "TODO: Update test for refactored architecture - get_transcription_service no longer exists"
3. `tests/services/test_chunk_processing_service.py:191` - Same as above
4. `tests/services/test_chunk_processing_service.py:226` - No reason given, likely refactoring

**Recommendation**: **DELETE** - These tests reference old architecture (`get_transcription_service` no longer exists). Update to use new service factory pattern OR delete if functionality is covered elsewhere.

### Chunk Generation Refactoring (1 test)

5. `tests/integration/test_chunk_generation_integration.py:13` - No reason given

**Recommendation**: **FIX** - Update for current chunk generation architecture OR delete if covered by other tests.

---

## Category 3: Performance/Manual Tests (6 tests) 📦 MOVE

**Action**: Move to `tests/manual/` directory with instructions

### API Performance Tests (2 tests)

1. `tests/performance/test_api_performance.py:44` - skipif
2. `tests/performance/test_api_performance.py:67` - skipif

### Auth Performance Tests (2 tests)

3. `tests/performance/test_auth_speed.py:16` - skipif
4. `tests/performance/test_auth_speed.py:42` - skipif

### Server Performance Tests (2 tests)

5. `tests/performance/test_server.py:36` - skipif
6. `tests/performance/test_server.py:54` - skipif

**Recommendation**: **MOVE** - All 6 performance tests should be moved to `tests/manual/performance/` with README explaining how to run them. They're skipped because they're slow, not broken.

---

## Category 4: Data Dependency Issues (4 tests) 🔧 FIX

**Action**: Ensure tests create their own test data

### Vocabulary Workflow Tests (3 tests)

1. `tests/integration/test_vocabulary_workflow.py:76` - "No A1 vocabulary words available for workflow test"
2. `tests/integration/test_vocabulary_workflow.py:269` - "No vocabulary words available for unmarking test"
3. `tests/integration/test_vocabulary_workflow.py:340` - "No vocabulary words available for multi-user test"

**Recommendation**: **FIX** - Tests should seed their own test data in fixtures instead of depending on existing database data. Add vocabulary word fixtures.

### Inprocess Vocabulary Test (1 test)

4. `tests/integration/test_inprocess_vocabulary.py:38` - "Integration test environment not properly configured"

**Recommendation**: **FIX** - Investigate configuration issue. Test should set up its own environment.

---

## Category 5: Implementation Gaps (4 tests) ⚠️ FIX OR DELETE

**Action**: Implement missing features OR delete test if no longer planned

### Not Implemented Endpoints (1 test)

1. `tests/api/test_vocabulary_routes.py:238` - "Endpoint not implemented yet"

**Recommendation**: **FIX OR DELETE** - If endpoint is planned, implement it. Otherwise delete the test.

### Not Implemented Features (3 tests)

2. `tests/api/test_vocabulary_routes_details.py:58` - @pytest.mark.skip (no reason)
3. `tests/integration/test_chunk_generation_integration.py:52` - @pytest.mark.skip (no reason)
4. `tests/integration/test_chunk_processing.py:25` - @pytest.mark.skip (no reason)

**Recommendation**: **FIX OR DELETE** - Investigate why these are skipped. If features aren't planned, delete tests. Otherwise implement.

---

## Category 6: Mock/Test Infrastructure (4 tests) 🔧 FIX

**Action**: Fix test setup and mocking

### Pydantic Validation Issues (1 test)

1. `tests/integration/test_vocabulary_serialization_integration.py:247` - "TODO: Update mock data to use string values instead of Mock objects for Pydantic validation"

**Recommendation**: **FIX** - Replace Mock objects with actual string values for Pydantic models. This is a test bug, not a feature gap.

### Serialization Test (1 test)

2. `tests/integration/test_vocabulary_serialization_integration.py:25` - @pytest.mark.skip (no reason)

**Recommendation**: **FIX** - Investigate and fix. Likely related to the Pydantic issue above.

### Chunk Processing Tests (2 tests)

3. `tests/integration/test_chunk_processing.py:89` - @pytest.mark.skip (no reason)
4. `tests/integration/test_vocabulary_service.py:417` - @pytest.mark.skip (no reason)

**Recommendation**: **FIX OR DELETE** - Investigate skip reasons. These might be test infrastructure issues or obsolete tests.

---

## Category 7: Design Conflicts (3 tests) 📋 DOCUMENT OR FIX

**Action**: Document as known limitation OR fix design mismatch

### FastAPI-Users Integer IDs (1 test)

1. `tests/api/test_auth_contract_improved.py:35` - "FastAPI-Users uses integer IDs, not UUIDs. Test requirement conflicts with implementation."

**Recommendation**: **DELETE** - This test assumes UUIDs but the application uses integer IDs. The test is wrong, not the implementation. Delete the test as it tests a requirement that doesn't match the architecture.

### CORS Implementation (1 test)

2. `tests/integration/test_authentication_workflow.py:180` - "CORS OPTIONS not implemented - using different CORS strategy"

**Recommendation**: **DOCUMENT** - If CORS is handled differently than expected, document the actual CORS strategy. If this is intentional, remove the skip and accept the current behavior.

### Service Video Support (1 test)

3. `tests/unit/services/test_transcription_interface.py:237` - "Service doesn't support video"

**Recommendation**: **FIX** - This is a conditional skip within a test. Either make the service support video OR restructure the test to only test supported formats.

---

## Category 8: Authentication Workflow (1 test) 🔧 FIX

**Action**: Fix login flow in test

### Login Dependency (1 test)

1. `tests/integration/api/test_auth_api_contract.py:163` - "Login failed (likely due to unverified user), skipping /me endpoint test"

**Recommendation**: **FIX** - Test is skipping when login fails. Should either fix the login (verify user in setup) OR restructure test to not depend on login success for /me testing.

---

## Summary by Action Required

### 🔧 FIX (25 tests, 60%)

- Missing dependencies: Make optional with graceful skip (16 tests)
- Data dependencies: Add test data fixtures (4 tests)
- Mock issues: Fix test infrastructure (4 tests)
- Auth workflow: Fix test setup (1 test)

### ⚠️ FIX OR DELETE (9 tests, 21%)

- Architecture refactoring: Update for new arch OR delete (5 tests)
- Implementation gaps: Implement feature OR delete test (4 tests)

### 📦 MOVE (6 tests, 14%)

- Performance tests: Move to tests/manual/ (6 tests)

### 📋 DOCUMENT (2 tests, 5%)

- Design conflicts: Document known limitations (2 tests)
- Note: The UUID test should be DELETED, not documented

---

## Recommended Priorities

### Priority 1: Quick Wins (2 hours)

1. **DELETE** UUID test (test_auth_contract_improved.py:35) - Wrong assumption
2. **DELETE** 4 obsolete architecture tests (test_chunk_processing_service.py)
3. **MOVE** 6 performance tests to tests/manual/
4. **FIX** Mock object Pydantic validation (test_vocabulary_serialization_integration.py:247)

**Result**: 11 tests resolved (26% reduction)

### Priority 2: Data Fixtures (2 hours)

5. **FIX** 4 vocabulary workflow tests - Add vocabulary word fixtures
6. **FIX** Inprocess vocabulary test - Fix test environment setup

**Result**: 5 more tests resolved (12% more)

### Priority 3: Documentation (1 hour)

7. **DOCUMENT** AI/ML dependencies with clear pytest.importorskip usage
8. **DOCUMENT** CORS strategy (or remove skip)

**Result**: 17 tests properly documented (40% more)

### Priority 4: Implementation Decisions (requires user input)

9. **FIX OR DELETE** 4 "not implemented" tests - Decide if features are planned
10. **FIX OR DELETE** 4 unexplained skips - Investigate and decide

**Result**: 8 tests resolved with decisions (19% more)

---

## Next Steps (Phase 2)

1. **Week 1**: Priorities 1-2 (Quick wins + Data fixtures) - 4 hours
   - Resolve 16 tests (38% reduction)
   - All deletions, moves, and straightforward fixes

2. **Week 2**: Priority 3 (Documentation) - 1 hour
   - Document 17 tests (40% properly handled)
   - Add pytest.importorskip for optional dependencies

3. **Week 3**: Priority 4 (Implementation decisions) - 2-4 hours
   - Requires user decisions on feature roadmap
   - Resolve final 8 tests (19%)

**Total Estimated Effort for Phase 2**: 7-9 hours

---

## Files Requiring Changes

### To Delete:

- `tests/api/test_auth_contract_improved.py` - Line 35 (UUID test)
- `tests/services/test_chunk_processing_service.py` - Lines 66, 149, 191, 226 (4 tests)

### To Move:

- `tests/performance/` → `tests/manual/performance/` (entire directory with 6 tests)

### To Fix:

- `tests/integration/test_vocabulary_workflow.py` - Add vocabulary fixtures
- `tests/integration/test_vocabulary_serialization_integration.py` - Fix mock data
- `tests/integration/test_inprocess_vocabulary.py` - Fix environment setup
- `tests/integration/test_authentication_workflow.py` - Fix login or remove skip
- `tests/unit/services/test_transcription_interface.py` - Fix service video support

### To Investigate:

- `tests/api/test_vocabulary_routes.py` - Line 238
- `tests/api/test_vocabulary_routes_details.py` - Line 58
- `tests/integration/test_chunk_generation_integration.py` - Lines 13, 52
- `tests/integration/test_chunk_processing.py` - Lines 25, 89
- `tests/integration/test_vocabulary_service.py` - Line 417

---

## Compliance with CLAUDE.md

Per CLAUDE.md: "Never introduce skip/xfail/ignore markers to bypass a failing path."

**Current Violations**:

- 9 tests have unexplained skips (need investigation)
- 5 tests skip due to old architecture (should be fixed or deleted)
- 4 tests skip due to missing features (should implement or delete)

**Compliant Usage**:

- 16 tests skip gracefully for missing optional dependencies (acceptable)
- 6 tests skip for performance reasons (should move to manual)
- 2 tests skip for documented design conflicts (should resolve)

**Goal**: Reduce from 42 skipped tests to <10 (documented optional dependencies only)

---

## Success Criteria

- [ ] Zero unexplained skips
- [ ] Zero skips for "not implemented" features (implement or delete tests)
- [ ] Zero skips for old architecture (update or delete tests)
- [ ] All data-dependent tests use fixtures (no skips for missing data)
- [ ] Performance tests moved to manual/ directory
- [ ] Optional AI/ML dependencies clearly documented with pytest.importorskip
- [ ] Pre-commit hook prevents new skip markers without approval

**Target**: <10 skipped tests (all for documented optional dependencies)

---

## Related Documents

- [CODE_SIMPLIFICATION_ROADMAP.md](../../CODE_SIMPLIFICATION_ROADMAP.md) - Test Architecture Task 9
- [CLAUDE.md](../../CLAUDE.md) - Testing standards and fail-fast philosophy
- [TEST_AUDIT_RESULTS.md](TEST_AUDIT_RESULTS.md) - Comprehensive test audit

---

**Phase 1 Status**: ✅ COMPLETE
**Next Phase**: Phase 2 - Fix or Delete Each Test (7-9 hours)
**Last Updated**: 2025-10-05

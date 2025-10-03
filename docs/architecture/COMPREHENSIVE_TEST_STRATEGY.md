# Comprehensive Test Strategy

**Project**: LangPlug - German Language Learning Platform
**Date**: 2025-10-02
**Status**: Active
**Test Coverage Target**: 80% (60% minimum)

---

## Executive Summary

LangPlug's test strategy follows the **Test Pyramid** approach with three layers:

1. **Unit Tests** (60%) - Fast, isolated component testing
2. **Integration Tests** (30%) - Service interaction testing
3. **E2E Tests** (10%) - Full user workflow testing

### Current State

- **Backend Coverage**: 85% (Excellent ✅)
- **Frontend Coverage**: 45% (Needs Improvement 🔴)
- **E2E Coverage**: Basic (20 scenarios)

### Target State

- **Backend**: Maintain 85%+
- **Frontend**: Achieve 60%+
- **E2E**: Expand to 50 scenarios

---

## 1. Test Pyramid

```
        /\
       /E2E\          10% - Full user workflows (slow, brittle)
      /______\
     /        \
    /Integration\    30% - Service interactions (medium speed)
   /__________  \
  /              \
 /   Unit Tests   \  60% - Component isolation (fast, reliable)
/__________________\
```

### Layer Distribution (Target)

| Layer       | Percentage | Count     | Avg Speed | Flakiness |
| ----------- | ---------- | --------- | --------- | --------- |
| Unit        | 60%        | 600 tests | < 50ms    | Low       |
| Integration | 30%        | 300 tests | 100-500ms | Medium    |
| E2E         | 10%        | 100 tests | 2-10s     | Higher    |

---

## 2. Unit Testing Strategy

### Backend Unit Tests (pytest)

#### Coverage Target: 85%+

**What to Test**:

- ✅ Business logic in services
- ✅ Data transformations
- ✅ Validation rules
- ✅ Utility functions
- ✅ Exception handling

**What NOT to Test**:

- ❌ Framework code (FastAPI, SQLAlchemy)
- ❌ Third-party libraries
- ❌ Generated code (migrations, OpenAPI schemas)
- ❌ Trivial getters/setters

**Example**:

```python
# tests/unit/services/test_vocabulary_service.py
@pytest.mark.asyncio
async def test_filter_vocabulary_removes_known_words():
    """Unit test: Isolated service logic"""
    # Arrange
    service = VocabularyFilterService()
    words = ["Hund", "Katze", "Elephant"]
    known_words = {"Hund"}

    # Act
    filtered = service.filter_known_words(words, known_words)

    # Assert
    assert filtered == ["Katze", "Elephant"]
    assert "Hund" not in filtered
```

### Frontend Unit Tests (Vitest + React Testing Library)

#### Coverage Target: 60%+

**What to Test**:

- ✅ Component rendering
- ✅ User interactions
- ✅ State changes
- ✅ Custom hooks
- ✅ Utility functions

**What NOT to Test**:

- ❌ React internals
- ❌ Third-party component libraries
- ❌ CSS/styling
- ❌ External API behavior (mock instead)

**Example**:

```typescript
// src/components/__tests__/VocabularyCard.test.tsx
describe('VocabularyCard', () => {
  it('should call onToggle when clicked', async () => {
    const onToggle = vi.fn();
    render(<VocabularyCard word="Hund" onToggle={onToggle} />);

    await userEvent.click(screen.getByText('Hund'));

    expect(onToggle).toHaveBeenCalledWith('Hund');
  });
});
```

---

## 3. Integration Testing Strategy

### Backend Integration Tests

#### Coverage Target: 30% of total tests

**What to Test**:

- ✅ Service → Repository → Database interactions
- ✅ API routes → Services → Database flows
- ✅ Multi-service orchestration
- ✅ External service mocks (AI models)

**Test Database**:

- Use in-memory SQLite for speed
- Isolate tests with transactional fixtures
- Clear data between tests

**Example**:

```python
# tests/integration/test_video_processing_flow.py
@pytest.mark.asyncio
async def test_complete_video_processing_flow(db_session, mock_whisper):
    """Integration test: Multiple services working together"""
    # Arrange
    video_service = VideoService(db_session)
    transcription_service = TranscriptionService()
    vocabulary_service = VocabularyService(db_session)

    # Act
    video = await video_service.create_video("test.mp4")
    transcript = await transcription_service.transcribe(video.id)
    vocabulary = await vocabulary_service.extract_vocabulary(transcript)

    # Assert
    assert video.status == "completed"
    assert len(transcript) > 0
    assert len(vocabulary) > 0
```

### Frontend Integration Tests

#### Coverage Target: 20% of total tests

**What to Test**:

- ✅ Component → API → State flow
- ✅ Multi-component interactions
- ✅ Context providers
- ✅ Routing flows

**Example**:

```typescript
// src/__tests__/integration/vocabulary-flow.test.tsx
describe('Vocabulary Learning Flow', () => {
  it('should display vocabulary from API and allow interaction', async () => {
    // Mock API
    server.use(
      rest.get('/api/vocabulary', (req, res, ctx) => {
        return res(ctx.json([{ id: 1, word: 'Hund', translation: 'dog' }]));
      })
    );

    render(<VocabularyLibrary />);

    // Wait for API data
    await waitFor(() => {
      expect(screen.getByText('Hund')).toBeInTheDocument();
    });

    // Interact
    await userEvent.click(screen.getByText('Hund'));

    // Verify state change
    expect(screen.getByText('Translation: dog')).toBeInTheDocument();
  });
});
```

---

## 4. End-to-End Testing Strategy

### E2E Test Coverage: 50 Scenarios

**What to Test**:

- ✅ Complete user workflows
- ✅ Cross-browser compatibility
- ✅ Performance benchmarks
- ✅ Critical business paths

**Tools**:

- Playwright (primary)
- Puppeteer (alternative)
- Cypress (considered but Playwright chosen)

**Example**:

```typescript
// tests/e2e/video-learning-workflow.spec.ts
test("User can complete video learning session", async ({ page }) => {
  // Login
  await page.goto("/login");
  await page.fill('[name="email"]', "user@test.com");
  await page.fill('[name="password"]', "password");
  await page.click('button[type="submit"]');

  // Select video
  await page.click("text=Superstore Episode 1");

  // Start learning
  await page.click("text=Start Learning");

  // Complete vocabulary game
  for (let i = 0; i < 10; i++) {
    await page.click('[data-testid="swipe-right"]');
  }

  // Watch video
  await page.click('[data-testid="play-button"]');
  await page.waitForTimeout(5000); // Watch 5 seconds

  // Verify progress saved
  await expect(page.locator('[data-testid="progress"]')).toContainText(
    "5% complete",
  );
});
```

---

## 5. Test Organization

### Backend Test Structure

```
Backend/tests/
├── unit/                      # 60% of tests
│   ├── services/             # Service logic tests
│   ├── utils/                # Utility function tests
│   └── models/               # Model validation tests
├── integration/              # 30% of tests
│   ├── api/                  # API endpoint tests
│   ├── database/             # Repository tests
│   └── services/             # Multi-service tests
├── e2e/                      # 10% of tests
│   └── workflows/            # Complete user flows
└── fixtures/                 # Shared test fixtures
    ├── mock_services.py
    └── fast_auth.py
```

### Frontend Test Structure

```
Frontend/src/
├── components/
│   └── __tests__/            # Component unit tests
├── hooks/
│   └── __tests__/            # Custom hook tests
├── utils/
│   └── __tests__/            # Utility tests
└── __tests__/
    ├── integration/          # Multi-component tests
    └── e2e/                  # Playwright E2E tests
```

---

## 6. Test Quality Standards

### Unit Test Quality

- ✅ **Fast**: < 50ms per test
- ✅ **Isolated**: No external dependencies
- ✅ **Deterministic**: Same result every time
- ✅ **Readable**: Clear Arrange-Act-Assert structure
- ✅ **Single Assertion**: One logical assertion per test

### Anti-Patterns to Avoid

- ❌ Testing implementation details
- ❌ Mocking too much (brittle tests)
- ❌ Slow tests in unit test suite
- ❌ Flaky tests (timing-dependent)
- ❌ Tests that pass with `assert True`

---

## 7. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: |
          cd Backend
          pytest --cov=. --cov-report=term-missing
      - name: Enforce 60% Coverage
        run: |
          coverage=$(pytest --cov=. --cov-report=json | jq '.totals.percent_covered')
          if [ $coverage < 60 ]; then exit 1; fi

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Frontend Tests
        run: |
          cd Frontend
          npm test -- --coverage
      - name: Enforce 60% Coverage
        run: |
          npm run test:coverage-check

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E Tests
        run: |
          npm run test:e2e
```

---

## 8. Test Execution

### Local Development

```bash
# Backend
cd Backend
pytest                              # Run all tests
pytest -k "test_vocabulary"         # Run specific tests
pytest --cov=services               # With coverage

# Frontend
cd Frontend
npm test                            # Run all tests
npm test -- --watch                 # Watch mode
npm test -- --coverage              # With coverage
```

### CI/CD

```bash
# Full test suite (CI)
make test-all

# Fast test suite (pre-commit)
make test-fast

# E2E tests (nightly)
make test-e2e
```

---

## 9. Test Maintenance

### Weekly Tasks

- [ ] Review flaky tests (> 1% failure rate)
- [ ] Update test data/fixtures
- [ ] Remove obsolete tests
- [ ] Add tests for new features

### Monthly Tasks

- [ ] Review test coverage trends
- [ ] Identify untested code paths
- [ ] Refactor slow tests
- [ ] Update testing dependencies

---

## 10. Success Metrics

| Metric                  | Current | Target  | Status |
| ----------------------- | ------- | ------- | ------ |
| **Backend Coverage**    | 85%     | 85%+    | ✅     |
| **Frontend Coverage**   | 45%     | 60%+    | 🔴     |
| **Test Execution Time** | 2 min   | < 5 min | ✅     |
| **Flaky Test Rate**     | < 1%    | < 1%    | ✅     |
| **E2E Scenarios**       | 20      | 50      | 🔴     |

---

## Appendix: Testing Tools

### Backend

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **faker**: Test data generation
- **factory_boy**: Model factories
- **httpx**: API testing

### Frontend

- **Vitest**: Test framework (Vite-native)
- **React Testing Library**: Component testing
- **MSW**: API mocking
- **Playwright**: E2E testing
- **@testing-library/user-event**: User interaction simulation

---

**Status**: ✅ Active
**Next Review**: Quarterly
**Owner**: QA + Development Teams

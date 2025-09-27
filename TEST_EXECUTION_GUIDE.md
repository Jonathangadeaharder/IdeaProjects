# Test Execution Guide

## Quick Start

### Run All Tests (PowerShell)
```powershell
./run-all-tests.ps1
```

### Run Individual Test Suites

#### Frontend Tests Only
```bash
cd Frontend
npm test -- --run
```

#### Backend Tests Only
```powershell
cd Backend
powershell.exe -Command ". api_venv/Scripts/activate; python -m pytest tests/unit/ --tb=short"
```

#### Contract Tests Only
```bash
cd Frontend
npm run test:contract
```

---

## TypeScript Compilation Check

```bash
cd Frontend
npx tsc --noEmit
```

---

## Test Coverage Commands

### Frontend Coverage
```bash
cd Frontend
npm test -- --coverage
```

### Backend Coverage
```powershell
cd Backend
powershell.exe -Command ". api_venv/Scripts/activate; python -m pytest tests/unit/ --cov=. --cov-report=term-missing"
```

---

## Known Issues & Workarounds

### Backend Tests Timeout
**Issue**: Service tests timeout when run in bulk
**Workaround**: Run individual test files:
```powershell
python -m pytest tests/unit/services/test_auth_service.py --tb=short
```

### Frontend Async Warnings
**Issue**: React state update warnings
**Status**: Fixed with act() wrappers

### Contract Schema Mismatches
**Issue**: 3 tests fail due to schema differences
**Action**: Update OpenAPI spec to match implementation

---

## Test Execution Times

| Suite | Time | Status |
|-------|------|--------|
| Frontend | ~20-30s | 98% pass |
| Backend Unit | ~35s | 100% pass |
| Backend Services | ~60s (individual) | 100% pass |
| Contract | ~10s | 92% pass |

---

## Environment Requirements

### Frontend
- Node.js 18+
- npm 9+

### Backend
- Python 3.11+
- Virtual environment: `api_venv`
- Environment variables:
  - `TESTING=1`
  - `ANYIO_BACKEND=asyncio`

### PowerShell
- Windows PowerShell 5.1+
- Or PowerShell Core 7+

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - run: ./run-all-tests.ps1
        shell: pwsh
```

---

## Debugging Failed Tests

### Frontend
```bash
# Run specific test file
npm test src/components/__tests__/VideoSelection.test.tsx

# Debug mode
npm test -- --no-coverage --inspect
```

### Backend
```powershell
# Verbose output
python -m pytest tests/unit/ -vv

# Stop on first failure
python -m pytest tests/unit/ -x

# Run last failed
python -m pytest tests/unit/ --lf
```

---

## Test Reports

- **Frontend HTML Report**: `Frontend/test-results/index.html`
- **Backend Coverage Report**: `Backend/htmlcov/index.html`
- **Test Status Reports**:
  - `FULL_TEST_SUMMARY.md`
  - `Backend/TEST_STATUS_REPORT.md`
  - `FINAL_TEST_REPORT.md`

---

Generated: 2025-09-27
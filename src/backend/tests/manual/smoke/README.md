# E2E Smoke Tests

End-to-end browser tests using Playwright to verify the complete user workflow.

## Prerequisites

### 1. Install Playwright

```bash
pip install playwright
python -m playwright install chromium
```

### 2. Server Startup (Automatic)

**Tests automatically start servers if not running!**

The E2E tests will:

1. Check if backend (http://localhost:8000/health) is healthy
2. Check if frontend (http://localhost:3000) is accessible
3. If either is down, automatically run `scripts/start-all.bat` (or `.sh`)
4. Wait up to 60 seconds for servers to become healthy
5. Fail with clear error if servers don't start

**Manual startup** (optional):

```bash
# From repository root
scripts/start-all.bat  # Windows
# OR
scripts/start-all.sh   # Linux/Mac
```

Verify servers are running:

- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000

### 3. Set Environment Variables

**Required**:

```bash
# Windows PowerShell
$env:E2E_TEST_PASSWORD = "YourSecurePassword123!"

# Windows CMD
set E2E_TEST_PASSWORD=YourSecurePassword123!

# Linux/Mac
export E2E_TEST_PASSWORD="YourSecurePassword123!"
```

**Optional**:

```bash
# Custom URLs
export E2E_BACKEND_URL="http://localhost:8000"
export E2E_FRONTEND_URL="http://localhost:3000"

# Custom credentials
export E2E_TEST_EMAIL="customuser@example.com"

# Headless mode (default: visible browser)
export E2E_HEADLESS=1

# Record video for debugging
export E2E_RECORD_VIDEO=1
```

## Running Tests

### Run All Smoke Tests

```bash
cd Backend
pytest tests/manual/smoke/ -m manual -v
```

### Run Individual Tests

```bash
# Simple workflow test (faster)
pytest tests/manual/smoke/test_e2e_simple.py -m manual -v

# Comprehensive test (multi-chunk processing)
pytest tests/manual/smoke/test_e2e_subtitle_verification.py -m manual -v
```

### Run as Standalone Scripts

```bash
# From Backend directory
python tests/manual/smoke/test_e2e_simple.py

# Requires E2E_TEST_PASSWORD to be set
```

## Test Coverage

### test_e2e_simple.py

- ✅ Login workflow
- ✅ Series selection
- ✅ Episode playback initiation
- ✅ Vocabulary game skipping
- ✅ Video player verification
- ✅ Subtitle track validation

### test_e2e_subtitle_verification.py

- ✅ User registration (auto)
- ✅ Complete login flow
- ✅ Multi-chunk episode processing
- ✅ Game screen navigation (multiple chunks)
- ✅ Video player with subtitles
- ✅ Subtitle contract validation (language codes, track count)

## Debugging

### Screenshots

All screenshots are saved to `tests/manual/smoke/screenshots/`:

- `01_after_login.png` - After successful login
- `02_video_with_subtitles.png` - Final video player state
- `error_*.png` - Error screenshots with context
- `debug_*.html` - Page HTML snapshots for debugging

### Video Recording

Enable video recording for complex debugging:

```bash
export E2E_RECORD_VIDEO=1
pytest tests/manual/smoke/ -m manual -v
```

Videos saved to `screenshots/` directory.

### Common Issues

**Backend not responding**:

```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend manually
cd Backend
python run_backend.py
```

**Frontend not loading**:

```bash
# Check if frontend is running
curl http://localhost:3000

# Start frontend manually
cd Frontend
npm run dev
```

**E2E_TEST_PASSWORD not set**:

```
ValueError: E2E_TEST_PASSWORD environment variable is required
```

Solution: Set the environment variable before running tests.

**Playwright not installed**:

```
ImportError: Playwright not installed
```

Solution: `pip install playwright && python -m playwright install chromium`

## Best Practices

### ✅ DO

- Run tests in visible browser mode first (easier debugging)
- Check screenshots after test failures
- Use semantic selectors (`data-testid`)
- Set E2E_TEST_PASSWORD as environment variable
- Verify servers are running before tests

### ❌ DON'T

- Don't run in automated CI without proper isolation
- Don't hard-code credentials in test files
- Don't rely on sleep/timeouts for assertions
- Don't use brittle selectors (text matching, array indices)
- Don't skip manual verification of screenshots

## Security

⚠️ **IMPORTANT**: Never commit E2E_TEST_PASSWORD to version control!

- Use environment variables only
- Add `.env` files to `.gitignore`
- Use test-specific credentials (not production)
- Rotate test credentials regularly

## Architecture

```
tests/manual/smoke/
├── e2e_config.py                       # Environment configuration
├── test_e2e_simple.py                  # Fast smoke test
├── test_e2e_subtitle_verification.py   # Comprehensive test
├── screenshots/                        # Test artifacts
│   ├── *.png                          # Screenshots
│   ├── *.html                         # Page dumps
│   └── *.webm                         # Video recordings
└── README.md                          # This file
```

## Maintenance

### Adding New E2E Tests

1. Create test file in `tests/manual/smoke/`
2. Add `@pytest.mark.manual` decorator
3. Import config from `config.py`
4. Use assertions, not return True/False
5. Use semantic selectors with fallbacks
6. Save debug screenshots on failures
7. Document test purpose in docstring

### Updating Selectors

When frontend changes:

1. Update `data-testid` attributes in Frontend components
2. Update selectors in E2E tests
3. Add fallback selectors for backward compatibility
4. Run tests to verify

## References

- [Playwright Documentation](https://playwright.dev/python/)
- [Testing Best Practices](../../TESTING_BEST_PRACTICES.md)
- [CLAUDE.md Testing Standards](../../../../CLAUDE.md)

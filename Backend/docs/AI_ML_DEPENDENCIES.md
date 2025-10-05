# AI/ML Dependencies Documentation

**Last Updated**: 2025-10-05
**Status**: Complete documentation of all optional AI/ML dependencies

---

## Overview

LangPlug uses several AI/ML models for language processing features. These dependencies are **optional** and tests gracefully skip when dependencies are not available.

This document explains:

- What AI/ML dependencies exist
- Why they're optional
- How to install them
- How tests handle missing dependencies

---

## Dependencies by Feature

### 1. Transcription Services (OpenAI Whisper)

**Purpose**: Convert audio/video to text transcripts

**Packages**:

```bash
pip install openai-whisper torch transformers
```

**Models Used**:

- `whisper-tiny` (150MB) - Testing and development
- `whisper-base` (290MB) - Production fallback
- `whisper-small` (967MB) - Production default

**Tests Affected** (5 tests):

- `tests/services/test_transcription_services.py` - Service factory tests
- `tests/unit/test_real_srt_generation.py` - WhisperTranscriptionService tests
- `tests/integration/test_ai_service_integration.py` - Integration tests (3 tests)

**Skip Behavior**:

- Tests skip with clear message if whisper not installed
- Module-level skip in test_real_srt_generation.py using `pytest.skip(..., allow_module_level=True)`
- Individual test skip in test_transcription_services.py using `@pytest.mark.skip`

---

### 2. Translation Services (PyTorch + Transformers)

**Purpose**: Translate text between languages

**Packages**:

```bash
pip install torch transformers sentencepiece
```

**Models Used**:

- `Helsinki-NLP/opus-mt-de-es` (300MB) - German-Spanish translation
- `Helsinki-NLP/opus-mt-de-en` (300MB) - German-English translation
- `facebook/nllb-200-distilled-600M` (2.4GB) - Multilingual translation

**Tests Affected** (3 tests):

- `tests/unit/services/processing/test_chunk_translation_service.py` - Translation service tests (1 test)
- `tests/integration/test_ai_service_integration.py` - Translation integration tests (2 tests)

**Skip Behavior**:

- Tests skip with `@pytest.mark.skip` if torch not available
- Environment variable `SKIP_HEAVY_AI_TESTS=1` skips model download tests

---

### 3. Vocabulary Extraction (spaCy)

**Purpose**: Extract and analyze German vocabulary from subtitles

**Packages**:

```bash
pip install spacy
python -m spacy download de_core_news_lg
```

**Models Used**:

- `de_core_news_lg` (560MB) - German language model for lemmatization and POS tagging

**Tests Affected** (2 tests):

- `tests/integration/test_api_contract_validation.py` - Vocabulary contract tests (2 tests)

**Skip Behavior**:

- Tests skip with `@pytest.mark.skip` if spaCy model not available
- Clear installation instructions in skip reason

---

### 4. Alternative Transcription (NVIDIA NeMo) - OPTIONAL

**Purpose**: Alternative transcription engine (Parakeet models)

**Packages**:

```bash
pip install nemo_toolkit
```

**Models Used**:

- `nvidia/parakeet-ctc-0.6b` (600MB) - Parakeet CTC model

**Tests Affected** (1 test):

- `tests/integration/test_ai_service_minimal.py` - Parakeet hello world test

**Skip Behavior**:

- Test uses try/except ImportError with `pytest.skip()` for graceful handling
- NeMo is completely optional - Whisper is the primary transcription engine

---

### 5. AI Service Integration Tests

**Purpose**: Test AI service factory and configuration with real models

**Environment Control**:

```bash
# Skip heavy AI tests in CI
export SKIP_HEAVY_AI_TESTS=1

# Run all AI tests locally
export SKIP_HEAVY_AI_TESTS=0
```

**Tests Affected** (5 tests in test_ai_service_minimal.py, 3 tests in test_ai_service_integration.py):

- Whisper-tiny hello world test
- OPUS translation hello world test
- NLLB translation hello world test
- Parakeet hello world test (optional)
- Various integration tests

**Skip Behavior**:

- All tests use `@pytest.mark.skipif(os.environ.get("SKIP_HEAVY_AI_TESTS") == "1")`
- Default in CI: SKIP_HEAVY_AI_TESTS=1 (set in conftest.py)
- Tests download models on first run (may take several minutes)

---

## Test Count Summary

**Total AI/ML Dependency Tests**: 16

**By Dependency**:

- Whisper/Transcription: 5 tests
- PyTorch/Translation: 3 tests
- spaCy Models: 2 tests
- NeMo Toolkit: 1 test
- AI Service Integration: 5 tests (environment-controlled)

**Skip Patterns Used**:

- `@pytest.mark.skip(reason="...")` - Hard skip with installation instructions
- `pytest.skip(..., allow_module_level=True)` - Module-level skip for missing imports
- `@pytest.mark.skipif(SKIP_HEAVY_AI_TESTS)` - Environment-controlled skip
- `pytest.skip()` in try/except - Graceful ImportError handling

---

## Installation Guide

### Minimal Installation (No AI Features)

```bash
# Just run the application without AI features
pip install -r requirements.txt
```

### Development Installation (Whisper + Translation)

```bash
# Most common setup for development
pip install -r requirements.txt
pip install openai-whisper torch transformers sentencepiece
```

### Full Installation (All AI Features)

```bash
# Complete installation with all optional dependencies
pip install -r requirements.txt
pip install openai-whisper torch transformers sentencepiece spacy
python -m spacy download de_core_news_lg

# Optional: NeMo for alternative transcription
pip install nemo_toolkit
```

---

## Running AI/ML Tests Locally

### Run All Tests (Skip AI Tests)

```bash
export SKIP_HEAVY_AI_TESTS=1
pytest tests/
```

### Run AI Tests with Dependencies Installed

```bash
export SKIP_HEAVY_AI_TESTS=0
pytest tests/integration/test_ai_service_minimal.py -v
pytest tests/integration/test_ai_service_integration.py -v
```

### Run Specific AI Feature Tests

```bash
# Whisper transcription tests
pytest tests/services/test_transcription_services.py -v
pytest tests/unit/test_real_srt_generation.py -v

# Translation tests
pytest tests/unit/services/processing/test_chunk_translation_service.py -v

# spaCy vocabulary tests
pytest tests/integration/test_api_contract_validation.py::TestFrontendBackendContract::test_vocabulary_response_matches_frontend_type -v
```

---

## CI/CD Configuration

### Current CI Setup

- `SKIP_HEAVY_AI_TESTS=1` set in conftest.py for all test environments
- AI dependencies NOT installed in CI (to save build time and resources)
- Tests gracefully skip with clear messages

### Future CI Enhancement Options

1. **Separate AI Test Job**: Optional CI job that runs only AI tests with dependencies
2. **Cached Models**: Cache downloaded models in CI for faster runs
3. **Smaller Models**: Use only whisper-tiny and opus-de-es in CI

---

## Best Practices

### For Test Authors

**DO**:

- ✅ Use `@pytest.mark.skip` with installation instructions in reason
- ✅ Use module-level skip for entire files: `pytest.skip(..., allow_module_level=True)`
- ✅ Use environment variables for heavy model tests: `@pytest.mark.skipif(SKIP_HEAVY_AI_TESTS)`
- ✅ Document dependencies in module docstrings
- ✅ Use smallest available models (whisper-tiny, opus-de-es)

**DON'T**:

- ❌ Fail tests when optional dependencies are missing
- ❌ Download large models in unit tests
- ❌ Use @pytest.mark.xfail for missing dependencies (use skip instead)
- ❌ Hard-code model paths or assume models are downloaded

### For Contributors

**Before Running AI Tests**:

1. Check which dependencies you need (see Installation Guide above)
2. Install dependencies for features you want to test
3. Set `SKIP_HEAVY_AI_TESTS=0` to enable model tests
4. First run will download models (expect several minutes)
5. Models are cached locally for future runs

**Model Storage Locations**:

- Whisper: `~/.cache/whisper/`
- HuggingFace models: `~/.cache/huggingface/`
- spaCy models: `<venv>/lib/python3.x/site-packages/de_core_news_lg/`

---

## Troubleshooting

### Test Skipped: "Requires openai-whisper dependency"

```bash
pip install openai-whisper torch transformers
```

### Test Skipped: "Requires PyTorch for translation models"

```bash
pip install torch transformers sentencepiece
```

### Test Skipped: "Requires spaCy de_core_news_lg model"

```bash
pip install spacy
python -m spacy download de_core_news_lg
```

### Test Skipped: "NeMo toolkit not installed"

```bash
# Optional - only if you want to test NeMo transcription
pip install nemo_toolkit
```

### Tests Taking Too Long

```bash
# Skip heavy model tests
export SKIP_HEAVY_AI_TESTS=1
pytest tests/
```

### Model Download Failures

- Check internet connection
- Check disk space (models require several GB)
- Some corporate networks block HuggingFace downloads
- Try downloading models manually first

---

## Related Documentation

- [CODE_SIMPLIFICATION_ROADMAP.md](../../CODE_SIMPLIFICATION_ROADMAP.md) - Test Architecture Task 9
- [SKIPPED_TESTS_AUDIT.md](SKIPPED_TESTS_AUDIT.md) - Complete audit of all skipped tests
- [CLAUDE.md](../../CLAUDE.md) - Testing standards and best practices

---

**Status**: Priority 3 Documentation Complete ✅
**Next Steps**: All AI/ML dependencies are now documented with clear skip patterns and installation instructions

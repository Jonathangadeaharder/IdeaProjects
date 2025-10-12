# DDD Cleanup Action Plan

## TL;DR

**The `domains/` directory is 90% dead code that duplicates working functionality.**

- **Size**: 192KB, ~2000 lines
- **Usage**: Only event system is used (by cache invalidation)
- **Status**: Routes not registered, services not used, imports broken
- **Recommendation**: Remove and extract valuable parts

---

## Analysis Results

### What's in domains/?

1. **domains/auth/** (4 files, ~400 LOC)
   - ❌ Routes fail to import (broken dependencies)
   - ❌ Services superseded by FastAPI-Users
   - **Status**: Dead code

2. **domains/vocabulary/** (8 files, ~1500 LOC)
   - ✅ Event system (USED by cache invalidation)
   - ❌ Routes not registered in app
   - ❌ Services not used (superseded by `services/vocabulary/`)
   - ⭐ Domain logic services (unused but potentially valuable):
     - `VocabularyDifficultyAnalyzer` - Smart difficulty calculation
     - `LearningProgressCalculator` - User level & spaced repetition
     - `SpacedRepetitionScheduler` - Optimal review intervals
   - **Status**: Event system valuable, rest unused

3. **domains/learning/** (1 file, ~5 LOC)
   - ❌ Empty (only `__init__.py`)
   - **Status**: Stub

4. **domains/processing/** (1 file, ~5 LOC)
   - ❌ Empty (only `__init__.py`)
   - **Status**: Stub

### What's Actually Being Used?

**Production Architecture**:

- ✅ `api/routes/*.py` (16 files) - All registered and working
- ✅ `services/*/*` (62 files) - All active
- ✅ FastAPI-Users for authentication
- ✅ `services/vocabulary/` (facade pattern with 3 specialized services)

**From domains/**:

- ✅ `domains/vocabulary/events.py` - Used by `core/event_cache_integration.py`
- ⚠️ `domains/vocabulary/entities.py` - Used as DTOs (not true entities)
- ❌ Everything else - Unused

---

## Recommended Action: Remove domains/

### Option A: Clean Removal (Recommended)

**Effort**: 2-3 hours
**Risk**: Low
**Value**: High (code clarity, reduced maintenance)

#### Step-by-Step Plan

**1. Extract Event System (30 min)**

```bash
# Create events directory
mkdir -p services/vocabulary/events

# Move event system
cp domains/vocabulary/events.py services/vocabulary/events/events.py

# Update imports in core/event_cache_integration.py
sed -i 's/from domains\.vocabulary\.events/from services.vocabulary.events.events/g' \
    core/event_cache_integration.py
```

**2. Extract Domain Logic (Optional, 30 min)**

If you want to keep the advanced algorithms:

```bash
# Move domain services
cp domains/vocabulary/domain_services.py services/vocabulary/domain_logic.py

# Later, integrate into vocabulary_service.py:
# - VocabularyDifficultyAnalyzer for smarter difficulty
# - LearningProgressCalculator for user level calculation
# - SpacedRepetitionScheduler for optimal review timing
```

**3. Update Database Repositories (15 min)**

Replace domain entity imports with Pydantic models:

```python
# In database/repositories/vocabulary_repository.py
# BEFORE:
from domains.vocabulary.entities import DifficultyLevel, VocabularyWord, WordType

# AFTER:
from core.enums import CEFRLevel as DifficultyLevel, WordType
from database.models import VocabularyWord  # Use SQLAlchemy model
```

**4. Remove domains/ (5 min)**

```bash
# Backup first (just in case)
tar -czf domains_backup_$(date +%Y%m%d).tar.gz domains/

# Remove
rm -rf domains/

# Update .gitignore if needed
echo "domains_backup_*.tar.gz" >> .gitignore
```

**5. Update Tests (30 min)**

```bash
# Find tests importing from domains
grep -r "from domains" tests/ --include="*.py"

# Update imports in:
# - tests/integration/test_vocabulary_service_integration.py
# - Any other tests found
```

**6. Update Documentation (15 min)**

- Remove DDD references from README
- Document service layer architecture
- Update architecture diagrams

**Total Time**: ~2.5 hours

---

### Option B: Keep and Complete DDD (NOT Recommended)

**Effort**: 3 weeks
**Risk**: High
**Value**: Low for current scale

This would require:

1. Fix import errors in domain routes
2. Implement all repository interfaces
3. Create infrastructure adapters
4. Migrate all routes to domains
5. Complete empty domains (learning, processing)
6. Comprehensive testing

**Why not recommended**:

- Codebase scale doesn't justify DDD complexity
- Service layer already provides good separation
- No clear business benefit
- High risk of breaking working functionality

---

## Detailed File Changes

### Files to Modify

**core/event_cache_integration.py**

```python
# Change import from:
from domains.vocabulary.events import (
    DomainEvent,
    EventType,
    get_event_bus,
)

# To:
from services.vocabulary.events.events import (
    DomainEvent,
    EventType,
    get_event_bus,
)
```

**database/repositories/vocabulary_repository.py**

```python
# Change import from:
from domains.vocabulary.entities import DifficultyLevel, VocabularyWord, WordType

# To:
from core.enums import CEFRLevel as DifficultyLevel, WordType
from database.models import VocabularyWord
# Or create Pydantic DTOs in api/models/vocabulary.py
```

**database/repositories/user_vocabulary_progress_repository.py**

```python
# Similar changes - replace domain entity imports with models
```

### Files to Delete

```
domains/
├── auth/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── services.py
├── learning/
│   └── __init__.py
├── processing/
│   └── __init__.py
├── vocabulary/
│   ├── __init__.py
│   ├── domain_services.py    # Consider extracting first
│   ├── entities.py
│   ├── events.py              # EXTRACT FIRST
│   ├── models.py
│   ├── repositories.py
│   ├── routes.py
│   ├── services.py
│   └── value_objects.py
└── __init__.py
```

**Total**: 16 files to delete after extraction

---

## What to Extract (Optional Enhancements)

### 1. Event System (Required)

**Extract**: `domains/vocabulary/events.py` → `services/vocabulary/events/events.py`

**Why**: Currently used for cache invalidation, valuable pattern

**Usage**:

```python
from services.vocabulary.events.events import (
    WordLearnedEvent,
    WordMasteredEvent,
    get_event_bus,
    publish_event
)

# In vocabulary_progress_service.py
def mark_word_known(user_id, word_id, is_known):
    # ... update database

    # Publish event for cache invalidation
    event = WordLearnedEvent(
        user_id=user_id,
        vocabulary_word=word,
        confidence_level="WEAK"
    )
    publish_event(event)
```

### 2. Domain Logic (Optional)

**Extract**: `domains/vocabulary/domain_services.py` → `services/vocabulary/domain_logic.py`

**Why**: Advanced algorithms that could enhance vocabulary features

**Useful Components**:

1. **VocabularyDifficultyAnalyzer**
   - Smarter difficulty calculation based on frequency and context
   - Could replace basic difficulty assignment

2. **LearningProgressCalculator**
   - Calculate user's overall language level
   - Recommend next words to learn
   - Calculate learning streaks

3. **SpacedRepetitionScheduler**
   - Optimal review intervals based on success rate
   - Could enhance review system

**Integration Example**:

```python
# In services/vocabulary/vocabulary_progress_service.py
from .domain_logic import SpacedRepetitionScheduler

def update_review_schedule(progress):
    scheduler = SpacedRepetitionScheduler()
    next_review = scheduler.calculate_optimal_review_interval(progress)
    progress.next_review_at = next_review
```

---

## Verification Checklist

After cleanup, verify:

- [ ] ✅ All imports resolved (no `ModuleNotFoundError`)
- [ ] ✅ All tests pass (`pytest tests/`)
- [ ] ✅ Cache invalidation still works
- [ ] ✅ Vocabulary API endpoints functional
- [ ] ✅ No references to `domains/` in codebase
- [ ] ✅ Documentation updated
- [ ] ✅ Git history preserved (backup exists)

**Commands**:

```bash
# Check for remaining domain imports
grep -r "from domains" . --include="*.py" --exclude-dir=domains

# Run tests
pytest tests/ -v

# Check cache invalidation
pytest tests/integration/test_vocabulary_service_integration.py -v -k cache
```

---

## Migration Script

Create `scripts/cleanup_domains.sh`:

```bash
#!/bin/bash
set -e

echo "Starting domains/ cleanup..."

# 1. Backup
echo "Creating backup..."
tar -czf "domains_backup_$(date +%Y%m%d_%H%M%S).tar.gz" domains/

# 2. Create events directory
echo "Setting up events directory..."
mkdir -p services/vocabulary/events
touch services/vocabulary/events/__init__.py

# 3. Move event system
echo "Extracting event system..."
cp domains/vocabulary/events.py services/vocabulary/events/events.py

# 4. Update imports
echo "Updating imports..."
find . -type f -name "*.py" -not -path "./domains/*" -exec \
    sed -i 's/from domains\.vocabulary\.events/from services.vocabulary.events.events/g' {} +

# 5. Optional: Extract domain logic
read -p "Extract domain logic? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Extracting domain logic..."
    cp domains/vocabulary/domain_services.py services/vocabulary/domain_logic.py
fi

# 6. Remove domains
echo "Removing domains directory..."
rm -rf domains/

# 7. Run tests
echo "Running tests..."
pytest tests/ -v --tb=short

echo "Cleanup complete! Backup saved as domains_backup_*.tar.gz"
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Update documentation"
echo "  3. Commit changes: git add . && git commit -m 'refactor: remove unused domains directory'"
```

**Usage**:

```bash
chmod +x scripts/cleanup_domains.sh
./scripts/cleanup_domains.sh
```

---

## Expected Outcomes

### Before Cleanup

```
Backend/
├── domains/          # 192KB, ~2000 LOC, 90% unused
│   ├── auth/         # Broken imports
│   ├── vocabulary/   # Only events used
│   ├── learning/     # Empty
│   └── processing/   # Empty
├── services/         # 960KB, working
└── api/routes/       # 16 files, registered
```

**Issues**:

- ❌ Confusing dual architecture
- ❌ Dead code paths
- ❌ Import errors
- ❌ Maintenance burden

### After Cleanup

```
Backend/
├── services/
│   └── vocabulary/
│       ├── events/              # Extracted from domains
│       │   └── events.py
│       ├── domain_logic.py      # Optional: Advanced algorithms
│       ├── vocabulary_service.py
│       └── ...
├── api/routes/                   # Clear, single route layer
└── core/
    └── event_cache_integration.py  # Uses services/vocabulary/events
```

**Benefits**:

- ✅ Single, clear architecture
- ✅ No dead code
- ✅ All imports working
- ✅ Event system preserved
- ✅ Easier to understand and maintain

---

## Timeline

### Quick Cleanup (2-3 hours)

- Extract event system
- Remove domains/
- Update imports
- Run tests

### With Domain Logic Extraction (4-5 hours)

- Above +
- Extract domain_services.py
- Integrate algorithms into vocabulary_service.py
- Update tests for new features

### Full Feature Integration (1-2 days)

- Above +
- Implement spaced repetition in review system
- Add difficulty analyzer to word processing
- Enhance user level calculation
- Comprehensive testing

---

## Risk Assessment

| Risk                        | Probability | Impact | Mitigation                                         |
| --------------------------- | ----------- | ------ | -------------------------------------------------- |
| Breaking cache invalidation | Low         | High   | Extract events carefully, test thoroughly          |
| Lost valuable code          | Low         | Medium | Backup before deletion, extract domain_services.py |
| Test failures               | Medium      | Low    | Update imports, fix tests incrementally            |
| Merge conflicts             | Low         | Low    | Coordinate with team, do cleanup in single PR      |

**Overall Risk**: ✅ **LOW** - Removing unused code is low-risk

---

## Decision

**Recommendation**: ✅ **Proceed with Option A (Clean Removal)**

**Rationale**:

1. domains/ is 90% unused (only events are used)
2. Duplicates working functionality in services/
3. Creates confusion and maintenance burden
4. Event system easily extracted
5. Domain logic algorithms can be optionally preserved

**Next Step**: Create PR with cleanup script and execute migration

**Estimated Total Effort**: 2-3 hours for core cleanup, 1-2 days if integrating advanced features

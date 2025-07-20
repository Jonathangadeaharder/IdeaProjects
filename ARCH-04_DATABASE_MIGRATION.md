# ARCH-04: Database Migration for Vocabulary and User Data Management

## 🎯 Project Overview

**Objective:** Replace brittle flat-file storage with a robust database system (SQLite/PostgreSQL) to ensure data integrity, enable concurrent access, and provide a foundation for future scalability.

**Current State:** The A1Decider system uses multiple flat files for data persistence:
- `globalunknowns.json` - Unknown word frequency tracking
- `vocabulary.txt` - Word frequency data
- `giuliwords.txt` - Known German words list
- `charaktere.txt` - Character names list
- `a1.txt` - A1-level vocabulary
- `brands.txt`, `onomatopoeia.txt`, `interjections.txt` - Specialized word lists

## 📊 Current Data Analysis

### File-Based Storage Issues
1. **Concurrency Problems:** Multiple processes cannot safely write to JSON/text files simultaneously
2. **Data Integrity:** No ACID transactions, risk of corruption during writes
3. **Performance:** Linear search through large text files
4. **Scalability:** Memory limitations when loading entire files
5. **Backup/Recovery:** No built-in backup mechanisms
6. **Query Limitations:** No complex queries or relationships

### Data Structures Identified

#### 1. Word Lists (Text Files)
```
Format: One word per line
Files: giuliwords.txt (3,283 words), charaktere.txt (114 names), a1.txt, etc.
Usage: Set operations for known word checking
```

#### 2. Global Unknowns (JSON)
```json
{
  "word": frequency_count,
  "johnny": 7,
  "kreese": 13,
  "captain": 5
}
Usage: Track unknown word frequencies across all processed content
```

#### 3. Vocabulary Data (Text)
```
Format: word: frequency
team: 32
trainerin: 22
ins: 20
Usage: Word frequency analysis for specific content
```

## 🗄️ Database Schema Design

### SQLite Implementation (Primary Choice)
**Rationale:** 
- Zero-configuration setup
- ACID compliance
- Cross-platform compatibility
- Perfect for single-application use
- Easy backup (single file)
- Built into Python standard library

### Database Schema

```sql
-- Word Categories/Lists Management
CREATE TABLE word_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    file_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core vocabulary storage
CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(100) NOT NULL,
    lemma VARCHAR(100),
    language VARCHAR(10) DEFAULT 'de',
    difficulty_level VARCHAR(10), -- A1, A2, B1, B2, etc.
    word_type VARCHAR(20), -- noun, verb, adjective, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(word, language)
);

-- Word category associations (many-to-many)
CREATE TABLE word_category_associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES vocabulary(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES word_categories(id) ON DELETE CASCADE,
    UNIQUE(word_id, category_id)
);

-- Global unknown words tracking
CREATE TABLE unknown_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(100) NOT NULL,
    lemma VARCHAR(100),
    frequency_count INTEGER DEFAULT 1,
    first_encountered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_encountered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language VARCHAR(10) DEFAULT 'de',
    UNIQUE(word, language)
);

-- User learning progress
CREATE TABLE user_learning_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) DEFAULT 'default_user',
    word_id INTEGER NOT NULL,
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_level INTEGER DEFAULT 1, -- 1-5 scale
    review_count INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES vocabulary(id) ON DELETE CASCADE,
    UNIQUE(user_id, word_id)
);

-- Content processing sessions
CREATE TABLE processing_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    content_type VARCHAR(50), -- subtitle, video, text
    content_path VARCHAR(500),
    total_words INTEGER,
    unknown_words_found INTEGER,
    processing_time_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session word discoveries
CREATE TABLE session_word_discoveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    word VARCHAR(100) NOT NULL,
    frequency_in_session INTEGER DEFAULT 1,
    context_examples TEXT, -- JSON array of example sentences
    FOREIGN KEY (session_id) REFERENCES processing_sessions(session_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_vocabulary_word ON vocabulary(word);
CREATE INDEX idx_vocabulary_lemma ON vocabulary(lemma);
CREATE INDEX idx_vocabulary_difficulty ON vocabulary(difficulty_level);
CREATE INDEX idx_unknown_words_word ON unknown_words(word);
CREATE INDEX idx_unknown_words_frequency ON unknown_words(frequency_count DESC);
CREATE INDEX idx_user_progress_user ON user_learning_progress(user_id);
CREATE INDEX idx_session_discoveries_session ON session_word_discoveries(session_id);
```

## 🔄 Migration Strategy

### Phase 1: Database Setup and Core Infrastructure
1. **Create Database Manager Class**
   - Connection management
   - Schema creation and migrations
   - Transaction handling
   - Error handling and logging

2. **Data Access Layer (DAL)**
   - Repository pattern implementation
   - CRUD operations for each entity
   - Query builders for complex operations
   - Connection pooling

### Phase 2: Data Migration
1. **Migrate Word Lists**
   - Parse all `.txt` word list files
   - Populate `word_categories` and `vocabulary` tables
   - Create associations in `word_category_associations`

2. **Migrate Global Unknowns**
   - Parse `globalunknowns.json`
   - Populate `unknown_words` table
   - Preserve frequency counts and timestamps

3. **Migrate Vocabulary Data**
   - Parse `vocabulary.txt`
   - Create processing session records
   - Link word discoveries to sessions

### Phase 3: Application Integration
1. **Update Configuration**
   - Add database connection settings
   - Maintain backward compatibility during transition

2. **Replace File I/O Operations**
   - Update `load_word_list()` functions
   - Replace JSON file operations
   - Implement caching for frequently accessed data

3. **Update Processing Pipeline**
   - Modify subtitle processing to use database
   - Update vocabulary learning game
   - Enhance API endpoints with database queries

## 🛠️ Implementation Plan

### Success Criteria
- ✅ All flat-file data successfully migrated to database
- ✅ Zero data loss during migration
- ✅ Improved performance for word lookups
- ✅ Concurrent access support
- ✅ Automatic backup and recovery mechanisms
- ✅ Backward compatibility maintained during transition
- ✅ Enhanced query capabilities for analytics

### Key Benefits
1. **Data Integrity:** ACID transactions prevent corruption
2. **Performance:** Indexed queries vs. linear file searches
3. **Concurrency:** Multiple processes can safely access data
4. **Scalability:** Efficient handling of large datasets
5. **Analytics:** Complex queries for learning insights
6. **Backup:** Built-in database backup/restore capabilities
7. **Relationships:** Proper foreign key constraints
8. **Versioning:** Schema migration support

### Migration Timeline
- **Phase 1:** Database infrastructure (2-3 days)
- **Phase 2:** Data migration scripts (2-3 days)
- **Phase 3:** Application integration (3-4 days)
- **Testing & Validation:** (1-2 days)

## 📁 File Structure
```
A1Decider/
├── database/
│   ├── __init__.py
│   ├── database_manager.py      # Core DB management
│   ├── models.py               # SQLAlchemy models (optional)
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── vocabulary_repository.py
│   │   ├── unknown_words_repository.py
│   │   └── user_progress_repository.py
│   ├── migrations/             # Schema migration scripts
│   │   ├── __init__.py
│   │   ├── 001_initial_schema.sql
│   │   └── migrate.py
│   └── seeds/                  # Data migration scripts
│       ├── __init__.py
│       ├── migrate_word_lists.py
│       ├── migrate_global_unknowns.py
│       └── migrate_vocabulary.py
├── vocabulary.db               # SQLite database file
└── config.py                   # Updated with DB settings
```

## 🔧 Configuration Updates

### Database Configuration
```python
@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    db_type: str = "sqlite"  # sqlite or postgresql
    db_path: str = "vocabulary.db"  # SQLite file path
    db_host: str = "localhost"  # PostgreSQL host
    db_port: int = 5432  # PostgreSQL port
    db_name: str = "vocabulary"  # PostgreSQL database name
    db_user: str = ""  # PostgreSQL username
    db_password: str = ""  # PostgreSQL password
    connection_pool_size: int = 5
    enable_logging: bool = False
```

## 📋 Implementation Status

**Status:** READY FOR IMPLEMENTATION

**Next Steps:**
1. Create database infrastructure
2. Implement data migration scripts
3. Update application to use database
4. Test and validate migration
5. Deploy and monitor

---

*This document outlines the complete database migration strategy for ARCH-04. The implementation will provide a solid foundation for future scalability and enhanced data management capabilities.*
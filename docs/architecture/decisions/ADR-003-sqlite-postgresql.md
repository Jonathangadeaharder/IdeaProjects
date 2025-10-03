# ADR-003: SQLite Database for Development, PostgreSQL for Production

## Status

Accepted

## Context

LangPlug requires a relational database to store:

- User accounts and authentication data
- Video metadata and processing status
- Vocabulary entries and learning progress
- Subtitle segments and translations
- Study session history

The database choice impacts:

- Local development setup complexity
- Production scalability and performance
- Cost of hosting and maintenance
- Data integrity and transaction support

We need a solution that balances ease of development with production readiness.

## Decision

We will use a dual-database strategy:

**Development Environment:**

- **SQLite**: File-based database (`langplug.db`) for local development
- No separate database server required
- Zero configuration setup for new developers

**Production Environment:**

- **PostgreSQL 15+**: Production-grade RDBMS
- Hosted on cloud provider (e.g., Render, Railway, DigitalOcean)
- Connection pooling and async driver (asyncpg)

**Migration Strategy:**

- **Alembic** for database migrations
- Migrations written to be compatible with both SQLite and PostgreSQL
- Environment variable controls database URL (`DATABASE_URL`)

**SQLAlchemy Configuration:**

```python
# Development
DATABASE_URL = "sqlite+aiosqlite:///./langplug.db"

# Production
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/langplug"
```

## Consequences

**Positive:**

- Developers can start coding immediately without installing PostgreSQL
- SQLite is reliable and sufficient for local testing
- PostgreSQL provides production-grade features (concurrent connections, full-text search, JSON queries)
- SQLAlchemy abstracts database differences for most operations
- Alembic migrations work across both databases
- Easy to test migration scripts locally before production deployment
- PostgreSQL has excellent performance for read-heavy workloads (vocabulary lookups)
- Cost-effective: free for development, pay-as-you-grow for production

**Negative:**

- Potential differences in SQL dialects between SQLite and PostgreSQL (e.g., date functions, JSON operators)
- Migration scripts must be tested on both databases
- SQLite lacks some advanced features used in production (e.g., concurrent writes, replication)
- Developers might not catch PostgreSQL-specific issues until production

**Risks:**

- Migrations that work in SQLite might fail in PostgreSQL (or vice versa)
- Performance characteristics differ (SQLite is single-threaded, PostgreSQL is multi-process)
- Subtle behavior differences (e.g., type coercion, NULL handling)

## Alternatives Considered

- **Alternative 1: PostgreSQL for both development and production**
  - _Why rejected_: Requires every developer to install and configure PostgreSQL locally. Increases onboarding friction. Overkill for local development.

- **Alternative 2: MySQL/MariaDB for production**
  - _Why rejected_: PostgreSQL has superior JSON support, full-text search, and async Python drivers (asyncpg). PostgreSQL is the standard for modern Python web apps.

- **Alternative 3: NoSQL (MongoDB, DynamoDB)**
  - _Why rejected_: LangPlug data is highly relational (users → videos → vocabulary → subtitles). SQL provides better data integrity with foreign keys and transactions.

- **Alternative 4: SQLite for production**
  - _Why rejected_: SQLite lacks concurrent write support and replication. Not suitable for production web applications with multiple workers.

## References

- Database configuration: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/core/database.py`
- Alembic migrations: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/alembic/`
- SQLAlchemy models: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/models/`
- Related: ADR-007 (Repository Pattern for Data Access)

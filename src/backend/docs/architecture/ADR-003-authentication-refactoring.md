# ADR-003: Authentication Architecture Refactoring (No Redis/Rate Limiting for MVP)

**Status**: Implemented
**Date**: 2025-10-09
**Decision Makers**: Development Team
**Related**: ADR-001 (pytest-asyncio), ADR-002 (Vocabulary Service)

## Context

The LangPlug authentication system had accumulated technical debt through:
- Dual authentication systems (FastAPI-Users + custom AuthService)
- Mixed password hashing algorithms (bcrypt + Argon2)
- Global singleton pollution (token_blacklist, login_tracker)
- Premature complexity (Redis, distributed rate limiting, token rotation)
- Over-engineering for current scale (MVP stage)

This created confusion, maintenance burden, and slowed development velocity.

## Decision

We decided to perform a comprehensive authentication refactoring following these principles:

### 1. Single Authentication System
- **Standardize on FastAPI-Users** as the sole authentication framework
- **Delete custom AuthService** to eliminate duplication
- Maintain only specialized components (TokenService, PasswordValidator)

### 2. Argon2 Password Hashing
- **Standardize on Argon2id** algorithm exclusively
- Remove all bcrypt compatibility code
- Implement through custom `Argon2PasswordHelper` extending FastAPI-Users

### 3. Simplified MVP Architecture
- **No Redis** - In-memory token blacklist sufficient for MVP
- **No rate limiting** - Not required at current scale
- **No token rotation** - Simple refresh tokens adequate for development
- **No audit logging** - Focus on core functionality first
- **SQLite database** - Simple, file-based storage for development

### 4. Fail-Fast Within Scope
- **No silent fallbacks** - errors propagate immediately
- **Clear error messages** guide developers to root causes
- **Fail fast on actual problems**, not on missing optional infrastructure

### 5. Proper Dependency Injection
- **Eliminate global singletons** (token_blacklist, login_tracker, rate_limiters)
- Module-level singleton management via `init_*()` / `cleanup_*()` functions
- Fail-fast if required dependencies not initialized

### 6. In-Memory Token Blacklist
- **TokenBlacklist** - Simple in-memory dictionary with expiration
- **Single-instance deployment** - No horizontal scaling needed for MVP
- **Automatic cleanup** - Periodic cleanup of expired tokens
- **No persistence** - Restart clears blacklist (acceptable for development)

## Implementation Summary

### Phase 1: Critical Infrastructure Fixes (2 hours)
- Standardized password hashing to Argon2
- Eliminated global singletons with proper DI
- Modified 5 core files

### Phase 2: Simplified Architecture (1 hour)
- Removed Redis dependencies
- Removed rate limiting infrastructure
- Removed token rotation complexity
- Kept simple in-memory token blacklist

### Phase 3: Architecture Cleanup (0.5 hours)
- Deleted custom AuthService (482 lines)
- Removed duplicate authentication logic
- Simplified to single system

### Phase 4: Database Migration (0.5 hours)
- Replaced PostgreSQL with SQLite
- Removed Redis configuration from docker-compose
- Updated environment configuration

## Consequences

### Positive

1. **Development Velocity**:
   - No Redis deployment required
   - No rate limiting infrastructure to maintain
   - Simple SQLite database setup
   - Faster development cycle

2. **Code Quality**:
   - Removed 719+ lines of dead/duplicate code
   - Eliminated premature optimization
   - Clean, simple architecture
   - Single source of truth for authentication

3. **Simplicity**:
   - Single-instance deployment (no horizontal scaling complexity)
   - No distributed state management
   - Easy local development setup
   - Minimal infrastructure requirements

4. **Maintainability**:
   - Single authentication system (FastAPI-Users)
   - Proper dependency injection
   - Clear error messages
   - Well-documented code

5. **Security** (Sufficient for MVP):
   - Modern Argon2id password hashing (OWASP recommended)
   - Token blacklist for logout functionality
   - HTTPS for production deployment
   - Input validation and sanitization

### Negative (Accepted Trade-offs for MVP)

1. **Scalability Limitations**:
   - In-memory token blacklist doesn't survive restarts
   - No horizontal scaling support (single instance only)
   - SQLite not suitable for high-concurrency production
   - No distributed rate limiting

2. **Security Limitations** (Acceptable for MVP):
   - No token rotation or theft detection
   - No comprehensive audit logging
   - No rate limiting against brute force attacks
   - No session management across multiple instances

3. **Production Readiness**:
   - Requires migration to PostgreSQL/Redis before scaling
   - Token blacklist lost on restart (users must re-login)
   - No compliance-ready audit trail

## When to Revisit This Decision

This architecture is appropriate for:
- ✅ MVP development and testing
- ✅ Single-instance deployments
- ✅ Small user bases (< 1000 users)
- ✅ Development and staging environments

**Revisit this decision when**:
1. **User base grows** beyond 1000 active users
2. **Horizontal scaling** becomes necessary (multiple instances)
3. **Production deployment** requires high availability
4. **Compliance requirements** mandate audit logging (SOC 2, HIPAA, GDPR)
5. **Security incidents** indicate need for rate limiting or theft detection
6. **Token theft** becomes a realistic concern

## Migration Path to Production Architecture

When the above conditions are met:

### Phase 1: Add Redis
1. Deploy Redis service
2. Migrate TokenBlacklist to Redis-backed implementation
3. Add Redis health checks and monitoring

### Phase 2: Add Rate Limiting
1. Implement distributed rate limiting with Redis
2. Configure per-endpoint limits
3. Add rate limit monitoring and alerts

### Phase 3: Add Token Rotation
1. Implement refresh token rotation with family tracking
2. Add token theft detection
3. Update client applications for rotation

### Phase 4: Add Audit Logging
1. Create audit_logs table
2. Log all authentication events
3. Add security incident detection
4. Configure compliance reporting

### Phase 5: Migrate to PostgreSQL
1. Deploy PostgreSQL service
2. Run database migrations
3. Update connection configuration
4. Test with production load

## Alternatives Considered

### Alternative 1: Implement Redis/Rate Limiting Now
**Rejected**: Premature optimization. Current scale doesn't justify the complexity. Better to iterate quickly with simple architecture and migrate when needed.

### Alternative 2: Keep Dual Authentication Systems
**Rejected**: Maintaining both FastAPI-Users and custom AuthService creates confusion, duplication, and technical debt.

### Alternative 3: Keep bcrypt Compatibility
**Rejected**: Per project standards, no legacy fallback code. Clean migration is preferred over backward compatibility pollution.

### Alternative 4: Use PostgreSQL Instead of SQLite
**Rejected**: SQLite is simpler for development, sufficient for MVP, and easier to set up. PostgreSQL adds deployment complexity without current benefit.

## Preventing Future Scope Creep

**IMPORTANT**: This ADR explicitly documents the decision NOT to implement:
- ❌ Redis (in-memory token blacklist sufficient)
- ❌ Rate limiting (not required at current scale)
- ❌ Token rotation (simple refresh adequate)
- ❌ Audit logging (future compliance requirement)
- ❌ Horizontal scaling (single instance sufficient)
- ❌ Docker/Containerization (direct execution simpler for MVP)

**Future developers**: Before adding these features, review the "When to Revisit" section above. These features add significant complexity and should only be implemented when there's a clear business need.

### Why No Docker for MVP

**Decision**: Run services directly using `scripts/start-all.bat` instead of Docker containers.

**Rationale**:
- **Simplicity**: Direct execution (`python run_backend.py`, `npm run dev`) is faster and simpler
- **Development Speed**: No container build time, immediate code changes
- **Resource Usage**: Lower overhead without containerization layer
- **Debugging**: Easier to debug with direct process access
- **Alignment**: Matches SQLite + in-memory architecture (no multi-instance coordination needed)

**When Docker becomes necessary**:
1. Production deployment with multiple instances
2. Need for environment isolation and reproducibility
3. Migration to PostgreSQL/Redis (containerized services)
4. CI/CD pipeline requiring consistent build environment
5. Team onboarding requiring standardized setup

**Development Workflow**:
```batch
# Start all services
scripts\start-all.bat

# Stop all services
scripts\stop-all.bat
```

**Removed Files** (2025-10-09):
- `docker-compose.yml` - Production orchestration (premature)
- `.github/workflows/docker-build.yml` - Container build automation (not needed)
- `Backend/Dockerfile` - Backend container definition (unnecessary complexity)
- `Frontend/Dockerfile` - Frontend container definition (unnecessary complexity)

## Current Architecture

### Token Blacklist
- **Implementation**: In-memory dictionary with expiration
- **Location**: `core/token_blacklist.py`
- **Scope**: Single process only
- **Persistence**: None (lost on restart)
- **Cleanup**: Periodic background task

### Database
- **Implementation**: SQLite
- **Location**: `data/langplug.db`
- **Scope**: Single instance
- **Backup**: File-based backup
- **Migration**: Alembic migrations

### Password Hashing
- **Implementation**: Argon2id via custom PasswordHelper
- **Location**: `core/auth_security.py`
- **Configuration**: OWASP recommended parameters

## Monitoring & Alerts (Minimal for MVP)

### Key Metrics to Monitor

1. **Authentication Events**:
   - Login success/failure rates
   - Token generation rates
   - Basic anomaly detection

2. **Performance**:
   - Response times for auth endpoints
   - Database query performance

### Recommended Alerts

- Abnormal login failure rates (warning)
- Authentication endpoint errors (critical)
- Database connection failures (critical)

## Future Enhancements (Out of Scope for MVP)

While not included in this refactoring, future considerations when scale demands:

1. **Distributed Infrastructure**:
   - Redis for token blacklist
   - PostgreSQL for primary database
   - Horizontal scaling support

2. **Security Enhancements**:
   - Token rotation with theft detection
   - Comprehensive audit logging
   - Distributed rate limiting
   - Multi-Factor Authentication (MFA)

3. **Session Management**:
   - Active session management UI
   - Device tracking
   - Geographic anomaly detection

4. **OAuth2 Providers**:
   - Google Sign-In
   - GitHub integration
   - Social authentication

## References

- [FastAPI-Users Documentation](https://fastapi-users.github.io/fastapi-users/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [SQLite When To Use](https://www.sqlite.org/whentouse.html)
- [YAGNI Principle](https://martinfowler.com/bliki/Yagni.html)

## Related Documents

- [AUTHENTICATION_REFACTORING_PROGRESS.md](../../AUTHENTICATION_REFACTORING_PROGRESS.md) - Detailed implementation log
- [AUTHENTICATION_REFACTORING_PLAN.md](../../AUTHENTICATION_REFACTORING_PLAN.md) - Original refactoring plan
- [SECURITY_AND_TRANSACTIONS.md](../SECURITY_AND_TRANSACTIONS.md) - Security best practices

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-09 | Use Argon2 exclusively | OWASP recommended, modern security |
| 2025-10-09 | NO Redis for MVP | Premature optimization, adds complexity |
| 2025-10-09 | NO rate limiting for MVP | Not required at current scale |
| 2025-10-09 | NO Docker for MVP | Direct execution simpler, faster development |
| 2025-10-09 | Use SQLite for MVP | Simple, file-based, sufficient for development |
| 2025-10-09 | Delete custom AuthService | Eliminate dual systems, reduce complexity |
| 2025-10-09 | In-memory token blacklist | Simple, adequate for single-instance MVP |
| 2025-10-09 | Skip token rotation | Not required for MVP, future enhancement |
| 2025-10-09 | Skip audit logging | Not required for MVP, compliance future |
| 2025-10-09 | Skip MFA implementation | Not required for MVP, future enhancement |

## Approval

This ADR documents implemented changes. The refactoring was completed successfully with simplified architecture focusing on MVP requirements.

**Implementation Time**: 4 hours
**Net Code Change**: -200+ lines (removed premature complexity)
**Files Modified**: 12 files changed, 5 files deleted
**Infrastructure Simplified**: Removed Redis, PostgreSQL; using SQLite, in-memory solutions

# ADR-004: FastAPI-Users for Authentication

## Status

Accepted

## Context

LangPlug requires secure user authentication to:

- Protect user data and videos
- Track learning progress per user
- Manage user preferences and settings
- Control access to processing resources

Authentication requirements:

- User registration with email and password
- Secure password hashing
- Session management (JWT and/or cookies)
- Email verification (future)
- Password reset flow (future)
- Optional OAuth integration (Google, GitHub)

Building authentication from scratch is time-consuming and error-prone. Security vulnerabilities in custom auth can be catastrophic.

## Decision

We will use **FastAPI-Users** library for authentication with the following configuration:

**Authentication Strategy:**

- **Dual strategy**: JWT (Bearer token) + Cookie-based authentication
- JWT for API clients and mobile apps (future)
- Cookie for browser sessions (HttpOnly, Secure, SameSite)

**Password Security:**

- Bcrypt hashing with CryptContext
- Configurable work factor (default: 12 rounds)

**User Management:**

- SQLAlchemy adapter for user storage
- Built-in user CRUD operations
- Email verification support (disabled initially)
- Password reset via email (disabled initially)

**Integration:**

```python
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
    CookieTransport,
)

# JWT strategy
jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)

# Cookie strategy
cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=CookieTransport(cookie_max_age=3600),
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [jwt_backend, cookie_backend],
)
```

## Consequences

**Positive:**

- Production-ready authentication out of the box
- Security best practices implemented by library maintainers
- Reduces custom code and potential vulnerabilities
- Supports multiple authentication strategies simultaneously
- Built-in email verification and password reset flows
- Active maintenance and security updates
- Well-documented with examples
- Easy to extend with custom logic (e.g., custom claims, user roles)
- Integrates seamlessly with FastAPI dependency injection

**Negative:**

- Adds external dependency and potential breaking changes
- Less control over authentication flow compared to custom implementation
- Learning curve for library-specific patterns
- Potential bloat if we only need basic features
- Migration effort if we need to move away from Fastapi-users

**Risks:**

- Library abandonment (mitigation: active maintenance as of 2024)
- Breaking changes in major versions (mitigation: pin versions, test before upgrading)
- Security vulnerabilities in library (mitigation: monitor security advisories, update promptly)

## Alternatives Considered

- **Alternative 1: Custom JWT authentication with PassLib**
  - _Why rejected_: Reinventing the wheel. Error-prone and time-consuming. Fastapi-users provides battle-tested implementation.

- **Alternative 2: Auth0 / Firebase Auth**
  - _Why rejected_: External service dependency and cost. Lock-in to third-party provider. Overkill for current requirements.

- **Alternative 3: Django-style session authentication**
  - _Why rejected_: Sessions stored in database are slower than stateless JWT. Django patterns don't fit FastAPI's async nature.

- **Alternative 4: OAuth only (no password auth)**
  - _Why rejected_: Forces users to have Google/GitHub accounts. Not all users want to link external accounts. Password auth is widely expected.

## References

- Authentication setup: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/core/auth.py`
- User model: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/models/user.py`
- Auth routes: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/routes/auth.py`
- FastAPI-Users documentation: https://fastapi-users.github.io/fastapi-users/
- Related: ADR-001 (Layered Architecture)

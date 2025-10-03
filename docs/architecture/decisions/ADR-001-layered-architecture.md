# ADR-001: Layered Architecture with Service-Oriented Design

## Status

Accepted

## Context

LangPlug is a language learning platform that processes videos, generates transcriptions, creates subtitles, and manages vocabulary. The application requires:

- Clear separation of concerns between API endpoints, business logic, and data access
- Testability at each layer without coupling to implementation details
- Maintainability as the codebase grows with new AI models and features
- Flexibility to swap data sources or business logic without cascading changes

Without a clear architectural pattern, the codebase risks becoming a monolithic tangle where API routes directly access databases, making testing difficult and changes risky.

## Decision

We will implement a 4-layer architecture with strict dependency rules:

1. **API Layer** (`Backend/routes/`): FastAPI routers that handle HTTP requests/responses, authentication, and validation
2. **Service Layer** (`Backend/services/`): Business logic, orchestration, and domain operations
3. **Repository Layer** (`Backend/repositories/`): Data access abstraction using Repository pattern
4. **Database Layer** (`Backend/models/`): SQLAlchemy ORM models and database schema

**Dependency Rules:**

- API Layer depends on Service Layer only
- Service Layer depends on Repository Layer only
- Repository Layer depends on Database Layer only
- No upward dependencies (Database cannot depend on Repository, etc.)

## Consequences

**Positive:**

- Clear separation of concerns makes the codebase easier to navigate and understand
- Each layer can be tested independently with appropriate mocks/fakes
- Business logic is isolated from HTTP concerns and database implementation details
- Easy to swap implementations (e.g., SQLite to PostgreSQL, mock repositories for testing)
- Reduces coupling and increases cohesion
- New developers can contribute to specific layers without understanding the entire system

**Negative:**

- More boilerplate code compared to a simpler architecture (models, repositories, services, routes)
- Increased complexity for simple CRUD operations
- Potential performance overhead from multiple abstraction layers
- Requires discipline to maintain layer boundaries and avoid shortcuts

**Risks:**

- Developers may bypass layers for "quick fixes" (e.g., API calling Repository directly)
- Over-engineering simple features with unnecessary abstractions
- Confusion about where specific logic belongs (Service vs Repository)

## Alternatives Considered

- **Alternative 1: Monolithic FastAPI routes with direct database access**
  - _Why rejected_: Poor testability, high coupling, difficult to maintain as complexity grows. This pattern works for simple CRUD apps but LangPlug has complex AI processing workflows.

- **Alternative 2: Domain-Driven Design (DDD) with Aggregates and Domain Services**
  - _Why rejected_: DDD is powerful but adds significant complexity with concepts like aggregates, domain events, and bounded contexts. Too heavyweight for LangPlug's current scale. Can revisit if the domain becomes more complex.

- **Alternative 3: Vertical Slice Architecture**
  - _Why rejected_: While vertical slices reduce coupling between features, LangPlug has significant shared logic (authentication, database sessions, AI model management) that benefits from horizontal layers.

## References

- Backend service layer: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/services/`
- Backend repository layer: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/repositories/`
- Backend API routes: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/routes/`
- Related: ADR-007 (Repository Pattern for Data Access)

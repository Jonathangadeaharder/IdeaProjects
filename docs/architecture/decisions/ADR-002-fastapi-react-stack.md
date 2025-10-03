# ADR-002: FastAPI + React/TypeScript Technology Stack

## Status

Accepted

## Context

LangPlug requires a full-stack solution that can:

- Handle high-performance video processing and AI model inference on the backend
- Provide a modern, responsive user interface with real-time updates
- Support type safety across the entire stack to reduce runtime errors
- Integrate with Python-based AI/ML libraries (Whisper, NLLB, Parakeet)
- Enable rapid development with excellent tooling and community support

The technology stack choice impacts development velocity, maintainability, performance, and the ability to attract contributors.

## Decision

We will use the following technology stack:

**Backend:**

- **FastAPI** (Python 3.11+): Modern async web framework with automatic OpenAPI generation
- **SQLAlchemy 2.0**: Async ORM for database operations
- **Pydantic V2**: Data validation and serialization
- **Alembic**: Database migrations

**Frontend:**

- **React 18**: Component-based UI library with hooks and concurrent rendering
- **TypeScript 5**: Type-safe JavaScript superset
- **Vite**: Fast build tool and dev server
- **TanStack Query (React Query)**: Data fetching and caching
- **React Router 6**: Client-side routing

**Integration:**

- OpenAPI schema generation from FastAPI
- TypeScript client generation from OpenAPI schema
- WebSocket for real-time communication

## Consequences

**Positive:**

- FastAPI provides excellent async performance for I/O-bound operations (video processing, AI inference)
- Automatic OpenAPI documentation and schema generation
- Native Python integration with AI/ML libraries (PyTorch, Transformers, NeMo)
- TypeScript provides type safety across frontend, reducing runtime errors
- React ecosystem offers mature tooling (testing, state management, component libraries)
- Strong type contracts between frontend and backend via OpenAPI
- Excellent developer experience with hot reload, type checking, and linting
- Large community support for both FastAPI and React

**Negative:**

- Python GIL limits true parallelism (mitigated by async/await for I/O operations)
- React has a steeper learning curve than simpler frameworks
- TypeScript adds compilation step and complexity
- Frontend build tools (Webpack, Vite) can be complex to configure

**Risks:**

- Breaking changes in major version updates (React, FastAPI)
- Dependency management complexity (Python virtual environments, npm packages)
- Potential performance bottlenecks with large video files

## Alternatives Considered

- **Alternative 1: Django + Vanilla JavaScript**
  - _Why rejected_: Django is synchronous by default, poor fit for async video processing. Vanilla JS lacks type safety. Django's batteries-included approach adds unused features.

- **Alternative 2: Node.js (Express/NestJS) + React**
  - _Why rejected_: Python ecosystem is superior for AI/ML. PyTorch, Transformers, and NeMo are primarily Python libraries. Node.js AI libraries are less mature.

- **Alternative 3: FastAPI + Vue 3/Svelte**
  - _Why rejected_: React has larger ecosystem, better TypeScript support, and more learning resources. Vue and Svelte are excellent but smaller communities.

- **Alternative 4: Go/Rust + HTMX**
  - _Why rejected_: Go/Rust lack mature AI/ML libraries. HTMX limits interactivity for complex UIs like video players with real-time subtitle overlays.

## References

- Backend setup: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/main.py`
- Frontend setup: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Frontend/src/main.tsx`
- OpenAPI schema: Backend auto-generates at `/docs` endpoint
- Related: ADR-008 (OpenAPI-First API Design)

# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the LangPlug project. ADRs document significant architectural decisions made during the development of the project.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences. ADRs help future developers understand:

- Why certain architectural choices were made
- What alternatives were considered
- What trade-offs were accepted
- What consequences (positive and negative) result from the decision

## Format

Each ADR follows a standard format:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: The issue or problem being addressed
- **Decision**: The architectural choice being made
- **Consequences**: The positive and negative outcomes of the decision
- **Alternatives Considered**: Other options that were evaluated
- **References**: Links to relevant code or documentation

## Current ADRs

| ADR                                                      | Title                                                      | Status   | Summary                                                                                       |
| -------------------------------------------------------- | ---------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------- |
| [ADR-001](./ADR-001-layered-architecture.md)             | Layered Architecture with Service-Oriented Design          | Accepted | 4-layer architecture (API → Service → Repository → Database) for clear separation of concerns |
| [ADR-002](./ADR-002-fastapi-react-stack.md)              | FastAPI + React/TypeScript Technology Stack                | Accepted | Modern stack: FastAPI backend with React 18 + TypeScript frontend                             |
| [ADR-003](./ADR-003-sqlite-postgresql.md)                | SQLite Database for Development, PostgreSQL for Production | Accepted | Dual database strategy for easy development and production scalability                        |
| [ADR-004](./ADR-004-fastapi-users-authentication.md)     | FastAPI-Users for Authentication                           | Accepted | Production-ready authentication using FastAPI-Users library with JWT + Cookie                 |
| [ADR-005](./ADR-005-websocket-realtime-communication.md) | WebSocket for Real-Time Communication                      | Accepted | WebSocket-based real-time progress updates during video processing                            |
| [ADR-006](./ADR-006-strategy-pattern-ai-models.md)       | Strategy Pattern for AI Model Integration                  | Accepted | Factory + Strategy pattern for hot-swappable AI models (Whisper, Parakeet, OPUS, NLLB)        |
| [ADR-007](./ADR-007-repository-pattern-data-access.md)   | Repository Pattern for Data Access                         | Accepted | Repository pattern to decouple business logic from database implementation                    |
| [ADR-008](./ADR-008-openapi-first-api-design.md)         | OpenAPI-First API Design                                   | Accepted | OpenAPI schema generation with TypeScript client generation for type-safe API calls           |

## Contributing

When making significant architectural decisions:

1. **Create a new ADR** using the next sequential number
2. **Follow the standard format** (see existing ADRs as examples)
3. **Document the context** - explain the problem and constraints
4. **Be explicit about trade-offs** - list both positive and negative consequences
5. **Consider alternatives** - show what options were evaluated
6. **Link to code** - reference relevant files and directories
7. **Update this README** - add the new ADR to the table above

## When to Create an ADR

Create an ADR when:

- Introducing a new architectural pattern or framework
- Choosing between multiple technology options
- Making decisions that will impact multiple teams or components
- Establishing conventions that should be followed consistently
- Deprecating or replacing existing architectural components

## When NOT to Create an ADR

Do not create ADRs for:

- Implementation details that don't affect overall architecture
- Temporary workarounds or experiments
- Routine code changes or bug fixes
- Changes that are easily reversible

## Resources

- [Michael Nygard's original ADR post](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [GitHub ADR organization](https://adr.github.io/)
- [ADR Tools](https://github.com/npryce/adr-tools)

# LangPlug Architecture Documentation - Index

This is the central index for all architecture documentation for the LangPlug language learning platform.

## 📚 Documentation Structure

```
docs/architecture/
├── INDEX.md                           # This file - central navigation
├── DIAGRAMS_SUMMARY.md               # Comprehensive diagram overview
│
├── diagrams/                         # PlantUML architecture diagrams
│   ├── README.md                     # Diagram usage guide
│   │
│   ├── system-context.puml           # C4 Level 1: System boundaries
│   ├── container-diagram.puml        # C4 Level 2: Technology containers
│   ├── backend-components.puml       # C4 Level 3: Backend internals
│   ├── frontend-components.puml      # C4 Level 3: Frontend internals
│   │
│   ├── sequence-authentication.puml  # Auth flow (JWT + Cookie)
│   ├── sequence-video-processing.puml # AI pipeline with WebSocket
│   │
│   ├── entity-relationship.puml      # Database schema & relationships
│   └── deployment-diagram.puml       # Infrastructure topology
│
└── [Future: ADRs, API docs, etc.]
```

## 🎯 Quick Navigation

### By Role

#### 👤 New Team Member (Start Here)

1. [System Context Diagram](diagrams/system-context.puml) - Big picture overview
2. [Container Diagram](diagrams/container-diagram.puml) - Technology stack
3. [Deployment Diagram](diagrams/deployment-diagram.puml) - Infrastructure
4. [Diagrams Summary](DIAGRAMS_SUMMARY.md) - Comprehensive guide

#### 💻 Backend Developer

1. [Backend Components Diagram](diagrams/backend-components.puml) - Service architecture
2. [Entity-Relationship Diagram](diagrams/entity-relationship.puml) - Database schema
3. [Sequence: Video Processing](diagrams/sequence-video-processing.puml) - AI pipeline
4. [Sequence: Authentication](diagrams/sequence-authentication.puml) - Auth flow

#### 🎨 Frontend Developer

1. [Frontend Components Diagram](diagrams/frontend-components.puml) - Component structure
2. [Sequence: Authentication](diagrams/sequence-authentication.puml) - Login flow
3. [Sequence: Video Processing](diagrams/sequence-video-processing.puml) - WebSocket updates
4. [Container Diagram](diagrams/container-diagram.puml) - API communication

#### 🏗️ DevOps / Infrastructure

1. [Deployment Diagram](diagrams/deployment-diagram.puml) - Infrastructure topology
2. [Container Diagram](diagrams/container-diagram.puml) - Application containers
3. [System Context](diagrams/system-context.puml) - External dependencies

#### 🔒 Security / Compliance

1. [Sequence: Authentication](diagrams/sequence-authentication.puml) - Security flow
2. [Deployment Diagram](diagrams/deployment-diagram.puml) - Security layers
3. [Container Diagram](diagrams/container-diagram.puml) - Communication protocols

### By Diagram Type

#### C4 Model Diagrams (Structural)

- **Level 1 - Context:** [System Context](diagrams/system-context.puml)
- **Level 2 - Containers:** [Container Diagram](diagrams/container-diagram.puml)
- **Level 3 - Components:**
  - [Backend Components](diagrams/backend-components.puml)
  - [Frontend Components](diagrams/frontend-components.puml)

#### Sequence Diagrams (Behavioral)

- [Authentication Flow](diagrams/sequence-authentication.puml) - User login with JWT
- [Video Processing Flow](diagrams/sequence-video-processing.puml) - AI pipeline with progress updates

#### Data Diagrams

- [Entity-Relationship Diagram](diagrams/entity-relationship.puml) - Database schema

#### Infrastructure Diagrams

- [Deployment Diagram](diagrams/deployment-diagram.puml) - Physical deployment topology

## 🔍 Architecture Highlights

### System Architecture Pattern

**Layered Architecture** with clear separation of concerns:

```
Frontend (React)
    ↕ HTTPS/WebSocket
Backend API Layer (FastAPI Routes)
    ↕ Business Logic
Service Layer (Orchestration)
    ↕ Data Access
Repository Layer (ORM)
    ↕ Persistence
Database Layer (PostgreSQL)
```

### Technology Stack

- **Frontend:** React 18 + TypeScript + Zustand + TanStack Query
- **Backend:** FastAPI + Python 3.11 + SQLAlchemy 2.0 + Alembic
- **Database:** PostgreSQL 15 (production) / SQLite (development)
- **AI/ML:** Whisper, NLLB-200, OPUS-MT, SpaCy
- **Auth:** FastAPI-Users with JWT + HttpOnly cookies
- **Real-time:** WebSocket for progress updates

### Key Features

1. **AI-Powered Video Processing**
   - Transcription: Whisper/Parakeet
   - Translation: NLLB/OPUS-MT
   - Vocabulary: SpaCy NLP

2. **Chunked Learning System**
   - Videos divided into learnable segments
   - Integrated subtitles and translations
   - Vocabulary highlighting

3. **Spaced Repetition Learning**
   - SM-2 algorithm for review scheduling
   - Knowledge levels: New → Native (0-5)
   - Progress tracking and analytics

4. **Real-time Progress Updates**
   - WebSocket for live processing status
   - Progress bar: 0% → 100% with status messages

## 📊 Diagram Viewing Guide

### Option 1: VS Code (Recommended for Developers)

```bash
# Install PlantUML extension
code --install-extension jebbs.plantuml

# Open diagram file
code diagrams/system-context.puml

# Preview: Alt+D (Windows/Linux) or Cmd+D (macOS)
```

### Option 2: Generate Images (Recommended for Documentation)

```bash
# Install PlantUML
# Ubuntu/Debian:
sudo apt-get install plantuml

# macOS:
brew install plantuml

# Generate all diagrams
cd docs/architecture/diagrams
plantuml *.puml              # PNG images
plantuml -tsvg *.puml        # SVG images (scalable)
```

### Option 3: Online Viewer (Quick Preview)

1. Visit: http://www.plantuml.com/plantuml/uml/
2. Copy diagram content from `.puml` file
3. Paste and view rendered diagram

## 🚀 Getting Started

### For Architects / Tech Leads

1. Review [Diagrams Summary](DIAGRAMS_SUMMARY.md) for comprehensive overview
2. Study [System Context](diagrams/system-context.puml) for big picture
3. Dive into [Backend](diagrams/backend-components.puml) and [Frontend](diagrams/frontend-components.puml) components
4. Review [Deployment](diagrams/deployment-diagram.puml) for infrastructure planning

### For Developers

1. Start with [Container Diagram](diagrams/container-diagram.puml) to understand technology stack
2. Study your area:
   - Backend: [Components](diagrams/backend-components.puml) + [ERD](diagrams/entity-relationship.puml)
   - Frontend: [Components](diagrams/frontend-components.puml) + [Sequences](diagrams/sequence-authentication.puml)
3. Review relevant [Sequence Diagrams](diagrams/) for workflow understanding

### For Operations / DevOps

1. Study [Deployment Diagram](diagrams/deployment-diagram.puml) for infrastructure
2. Review [Container Diagram](diagrams/container-diagram.puml) for service dependencies
3. Check [System Context](diagrams/system-context.puml) for external integrations

## 📝 Maintenance Guidelines

### When to Update Diagrams

- ✅ New features or services added
- ✅ Database schema changes
- ✅ API or service boundary modifications
- ✅ New external integrations
- ✅ Infrastructure or deployment changes
- ✅ Security or authentication updates

### How to Update

1. **Edit `.puml` source file** with changes
2. **Regenerate images:** `plantuml diagram-name.puml`
3. **Update README** if adding new diagrams
4. **Commit both source and images** to Git
5. **Update this INDEX.md** if structure changes

### Diagram Quality Standards

- Clear, readable labels
- Consistent styling and colors
- Appropriate level of detail for audience
- Notes explaining complex relationships
- Version/date information where relevant

## 📖 Additional Resources

### Internal Documentation

- [Diagrams Summary](DIAGRAMS_SUMMARY.md) - Detailed diagram guide
- [Diagrams README](diagrams/README.md) - Usage and conventions
- [Project README](../../README.md) - Project overview

### External Resources

- [PlantUML Documentation](https://plantuml.com/)
- [C4 Model](https://c4model.com/)
- [PlantUML C4](https://github.com/plantuml-stdlib/C4-PlantUML)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

### Architecture Patterns

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)

## 🔄 Version History

| Version | Date       | Changes                               | Author            |
| ------- | ---------- | ------------------------------------- | ----------------- |
| 1.0     | 2025-10-02 | Initial architecture diagrams created | Architecture Team |

## 📧 Contact & Contribution

For questions about architecture or to propose changes:

1. Open an issue in the project repository
2. Tag with `architecture` label
3. Reference specific diagram(s) if applicable

For diagram improvements:

1. Edit `.puml` source file
2. Follow existing conventions
3. Submit pull request with both source and generated images

---

**Last Updated:** 2025-10-02
**Location:** `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/docs/architecture/`
**Total Diagrams:** 8
**Maintained By:** LangPlug Architecture Team

# LangPlug Architecture Diagrams - Summary

## Overview

This document provides a comprehensive summary of all PlantUML architecture diagrams created for the LangPlug language learning platform. These diagrams follow the C4 Model methodology and provide visual documentation of the system architecture from multiple perspectives.

## Diagram Inventory

### 📋 Created Diagrams (8 Total)

| #   | Diagram Name                | Type       | File                             | Purpose                                                         |
| --- | --------------------------- | ---------- | -------------------------------- | --------------------------------------------------------------- |
| 1   | **System Context**          | C4 Level 1 | `system-context.puml`            | Big picture - system boundaries and external dependencies       |
| 2   | **Container Diagram**       | C4 Level 2 | `container-diagram.puml`         | High-level technology choices and container communication       |
| 3   | **Backend Components**      | C4 Level 3 | `backend-components.puml`        | FastAPI backend internal structure (API → Service → Repository) |
| 4   | **Frontend Components**     | C4 Level 3 | `frontend-components.puml`       | React frontend structure (Pages → Components → State)           |
| 5   | **Authentication Flow**     | Sequence   | `sequence-authentication.puml`   | User login flow with JWT and cookies                            |
| 6   | **Video Processing Flow**   | Sequence   | `sequence-video-processing.puml` | AI-powered video processing pipeline with WebSocket updates     |
| 7   | **Entity-Relationship**     | ERD        | `entity-relationship.puml`       | Database schema and entity relationships                        |
| 8   | **Deployment Architecture** | Deployment | `deployment-diagram.puml`        | Infrastructure and deployment topology                          |

## Quick Reference Guide

### When to Use Each Diagram

#### 🎯 For New Team Members

- Start with: **System Context** → **Container Diagram** → **Deployment Architecture**
- Purpose: Understand the big picture and technology stack

#### 💻 For Backend Developers

- Focus on: **Backend Components** → **Sequence Diagrams** → **Entity-Relationship**
- Purpose: Understand service architecture, flows, and data model

#### 🎨 For Frontend Developers

- Focus on: **Frontend Components** → **Sequence Diagrams** → **Container Diagram**
- Purpose: Understand component structure, API communication, and state management

#### 🏗️ For DevOps/Infrastructure

- Focus on: **Deployment Architecture** → **Container Diagram** → **System Context**
- Purpose: Understand deployment topology, scaling strategy, and infrastructure requirements

#### 🔒 For Security Audits

- Focus on: **Authentication Flow** → **Deployment Architecture** → **Container Diagram**
- Purpose: Understand authentication mechanisms, secure communication, and system boundaries

## Key Architectural Insights

### Backend Architecture (Layered)

```
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database Layer (SQLAlchemy Models)
```

**Key Services:**

- AuthService → User authentication & JWT
- VideoService → Video metadata management
- TranscriptionService → Whisper/Parakeet AI integration
- TranslationService → NLLB/OPUS-MT integration
- VocabularyService → SpaCy NLP for word extraction
- ProcessingService → Orchestrates the entire pipeline

### Frontend Architecture (Component-Based)

```
App (Router)
    ↓
Pages (Dashboard, Learning, Vocabulary, Game)
    ↓
Components (Player, Flow, VideoSelection, VocabularyGame)
    ↓
UI Components (Button, Card, Input, Loading)
```

**State Management:**

- Zustand stores: Auth, Video, Vocabulary
- TanStack Query: API data fetching and caching
- React Context: Theme preferences

### AI Processing Pipeline

```
1. Transcription (0-40%)
   Video → Audio Extraction → Whisper/Parakeet → SRT Subtitles

2. Translation (40-70%)
   Subtitles → NLLB/OPUS-MT → Translated SRT

3. Vocabulary Extraction (70-90%)
   Text → SpaCy NLP → Word Analysis → Difficulty Scoring

4. Finalization (90-100%)
   Save to Database → Update Video Record → Complete Task
```

**Real-time Updates:** WebSocket provides progress notifications throughout all phases

### Database Schema (Core Entities)

**User Management:**

- `User` → Authentication, profile, preferences
- `LearningSession` → Tracks user engagement and progress

**Content Management:**

- `Video` → Series, episodes, file metadata
- `VideoChunk` → Learnable segments with subtitles
- `Vocabulary` → Extracted words with translations

**Learning Progress:**

- `UserVocabulary` → Spaced repetition system (SRS)
  - Knowledge levels: 0 (New) → 5 (Native)
  - Next review calculated using SM-2 algorithm
  - Tracks review history and success rate

**Processing:**

- `ProcessingTask` → Async AI operations tracking
  - Status: PENDING → PROCESSING → COMPLETED/FAILED
  - Progress updates (0-100%)
  - Error handling and retry logic

### Deployment Topology

**Development Environment:**

- Frontend: Vite dev server (Port 3000)
- Backend: Uvicorn with hot reload (Port 8000)
- Database: SQLite (local file)
- AI Models: CPU-based (no GPU required)
- Storage: Local filesystem

**Production Environment:**

- Frontend: React SPA → Nginx → CDN (optional)
- Backend: FastAPI → Uvicorn → Nginx (reverse proxy)
- Database: PostgreSQL cluster with read replicas
- AI Models: GPU-accelerated (CUDA 12.1, NVIDIA A100/V100/T4)
- Storage: Object storage (AWS S3 / Azure Blob)
- Scaling: Horizontal scaling with load balancer

## Technology Stack Summary

### Frontend

- **Framework:** React 18 + TypeScript
- **State:** Zustand, TanStack Query
- **Styling:** Tailwind CSS
- **API Client:** OpenAPI-generated (type-safe)
- **Build Tool:** Vite

### Backend

- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0 (async)
- **Auth:** FastAPI-Users (JWT + Cookie)
- **Validation:** Pydantic v2
- **Migrations:** Alembic
- **Server:** Uvicorn (ASGI)

### AI/ML Services

- **Transcription:**
  - OpenAI Whisper (whisper-large-v3)
  - NVIDIA Parakeet (parakeet-ctc-1.1b)
- **Translation:**
  - Meta NLLB-200 (distilled-600M)
  - Helsinki OPUS-MT (language pairs)
- **NLP:**
  - SpaCy with language models
  - POS tagging, lemmatization, NER

### Database

- **Development:** SQLite (file-based)
- **Production:** PostgreSQL 15
- **Connection:** Async SQLAlchemy with connection pooling

### Infrastructure

- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes (optional), AWS ECS/EKS
- **Web Server:** Nginx (reverse proxy, load balancer)
- **Real-time:** WebSocket (FastAPI WebSocket support)

## Security Architecture

### Authentication & Authorization

- **Strategy:** JWT (access tokens) + HttpOnly cookies (refresh tokens)
- **Password:** Bcrypt hashing
- **Verification:** Email verification flow
- **RBAC:** User roles (superuser, regular user)

### Communication Security

- **Transport:** HTTPS/TLS (production)
- **WebSocket:** WSS (secure WebSocket)
- **CORS:** Configured for frontend origin
- **Headers:** Security headers (HSTS, CSP, X-Frame-Options)

### Data Security

- **Validation:** Pydantic models for input validation
- **SQL Injection:** SQLAlchemy ORM (parameterized queries)
- **XSS Protection:** React auto-escaping + CSP headers
- **Rate Limiting:** API endpoint throttling

## Scalability Considerations

### Horizontal Scaling

- **API Servers:** Stateless FastAPI instances behind load balancer
- **Database:** Read replicas for query load distribution
- **AI Processing:** Dedicated GPU nodes with job queue
- **Storage:** Distributed object storage (S3/Azure)

### Performance Optimization

- **Caching:** Redis for session data and frequent queries
- **CDN:** Static assets and media delivery
- **Database:** Indexed queries, connection pooling
- **AI Models:** Batch inference, model quantization

### Monitoring & Observability

- **Logging:** Structured logging (JSON format)
- **Metrics:** Application performance metrics
- **Tracing:** Distributed tracing for request flows
- **Alerts:** Error rates, performance degradation

## Maintenance and Updates

### Diagram Update Triggers

Update diagrams when:

- ✅ Adding new major features or services
- ✅ Changing database schema or entity relationships
- ✅ Modifying API architecture or service boundaries
- ✅ Adding external integrations (AI models, third-party APIs)
- ✅ Changing deployment infrastructure or scaling strategy
- ✅ Updating authentication/authorization mechanisms

### Version Control

- **Source Files:** All `.puml` files committed to Git
- **Generated Images:** PNG/SVG images committed for easy viewing
- **Documentation:** This README and diagram-specific notes

## How to Generate Images

### Using PlantUML CLI

```bash
# Navigate to diagrams directory
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/docs/architecture/diagrams

# Generate all PNG images
plantuml *.puml

# Generate all SVG images (scalable, recommended)
plantuml -tsvg *.puml

# Generate specific diagram
plantuml system-context.puml
```

### Using VS Code

1. Install "PlantUML" extension
2. Open any `.puml` file
3. Press `Alt+D` (Windows/Linux) or `Cmd+D` (macOS)
4. View preview in side panel

### Using Online Editor

1. Visit http://www.plantuml.com/plantuml/uml/
2. Copy `.puml` file content
3. Paste and view rendered diagram
4. Export as PNG/SVG

## Resources

- **All Diagrams:** `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/docs/architecture/diagrams/`
- **PlantUML Documentation:** https://plantuml.com/
- **C4 Model:** https://c4model.com/
- **PlantUML C4 Library:** https://github.com/plantuml-stdlib/C4-PlantUML

---

**Created:** 2025-10-02
**Location:** `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/docs/architecture/diagrams/`
**Total Diagrams:** 8
**Format:** PlantUML (.puml)
**Generated Images:** PNG/SVG (on-demand)

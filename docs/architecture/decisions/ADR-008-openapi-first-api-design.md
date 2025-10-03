# ADR-008: OpenAPI-First API Design

## Status

Accepted

## Context

LangPlug has a decoupled frontend and backend architecture:

- Backend: FastAPI (Python)
- Frontend: React + TypeScript

The frontend needs to communicate with the backend via HTTP APIs. This creates several challenges:

- **Type Safety**: TypeScript frontend needs to know backend API contracts
- **Documentation**: Developers need API documentation
- **Validation**: Request/response validation on both sides
- **Contract Testing**: Ensure frontend and backend stay in sync
- **Breaking Changes**: Detect API changes before production

Without a formal contract, API changes can break the frontend silently, and developers must manually sync types between backend and frontend.

## Decision

We will use an **OpenAPI-first approach** with automatic schema generation and TypeScript client generation.

**Architecture:**

1. **Backend: Automatic OpenAPI Generation**

```python
# FastAPI auto-generates OpenAPI schema from Pydantic models
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="LangPlug API",
    version="1.0.0",
    openapi_url="/openapi.json",
)

class VideoResponse(BaseModel):
    id: int
    title: str
    status: str

    class Config:
        from_attributes = True

@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int):
    # FastAPI validates and serializes based on response_model
    pass
```

2. **OpenAPI Schema Export**

```bash
# Generate OpenAPI schema
python -c "import json; from Backend.main import app; print(json.dumps(app.openapi()))" > openapi.json
```

3. **TypeScript Client Generation**

```bash
# Generate TypeScript client from OpenAPI schema
npx openapi-typescript-codegen --input openapi.json --output Frontend/src/api
```

4. **Type-Safe Frontend API Calls**

```typescript
// Auto-generated TypeScript client
import { VideosService } from "./api";

// Fully type-safe API call
const video = await VideosService.getVideo(videoId);
// TypeScript knows: video has id, title, status properties
```

5. **CI/CD Integration**

```yaml
# In GitHub Actions / CI pipeline
- name: Generate OpenAPI schema
  run: python scripts/generate_openapi.py

- name: Generate TypeScript client
  run: npm run generate:api

- name: Check for uncommitted changes
  run: git diff --exit-code
  # Fails if schema changed but client wasn't regenerated
```

**Workflow:**

1. Define Pydantic models in backend (single source of truth)
2. FastAPI auto-generates OpenAPI schema
3. CI generates TypeScript client from schema
4. Frontend uses type-safe client
5. Tests validate request/response against schema

## Consequences

**Positive:**

- Single source of truth: backend Pydantic models define contract
- Type safety: TypeScript catches API misuse at compile time
- Automatic documentation: OpenAPI schema serves as interactive docs (`/docs` endpoint)
- Contract testing: OpenAPI schema enables contract validation
- Breaking change detection: TypeScript compilation fails if API changes
- Developer experience: Autocomplete and type hints in IDE
- Reduced bugs: Catch type mismatches before runtime
- API versioning: OpenAPI supports versioning strategies

**Negative:**

- Build step required: must regenerate client when API changes
- CI complexity: pipeline must generate and validate schema
- Potential drift: if developers forget to regenerate client
- Code generation overhead: generates many files (can be verbose)
- Learning curve: developers must understand OpenAPI concepts

**Risks:**

- Schema generation breaks if Pydantic models are invalid
- Generated client may have quirks (e.g., naming collisions)
- Large APIs generate large client files (bundle size)
- Breaking changes can be painful (coordinate frontend and backend updates)

## Alternatives Considered

- **Alternative 1: Manual TypeScript interfaces**
  - _Why rejected_: Manual duplication is error-prone. No guarantee frontend and backend stay in sync. Tedious to maintain.

- **Alternative 2: GraphQL**
  - _Why rejected_: Adds complexity (schema definition language, resolvers, query parsing). Overkill for LangPlug's CRUD-heavy API. REST is simpler.

- **Alternative 3: tRPC (type-safe RPC)**
  - _Why rejected_: Requires TypeScript on backend. LangPlug uses Python backend. tRPC is Node.js-specific.

- **Alternative 4: Protobuf/gRPC**
  - _Why rejected_: Binary protocol is overkill for web application. Poor browser support. REST/JSON is standard for web APIs.

- **Alternative 5: Swagger Codegen**
  - _Why rejected_: `openapi-typescript-codegen` is more modern, better TypeScript support, actively maintained.

## References

- FastAPI app with OpenAPI: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/main.py`
- Pydantic schemas: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/schemas/`
- Generated TypeScript client: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Frontend/src/api/`
- OpenAPI generation script: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/scripts/generate_openapi.py`
- FastAPI OpenAPI docs: https://fastapi.tiangolo.com/features/#automatic-docs
- openapi-typescript-codegen: https://github.com/ferdikoomen/openapi-typescript-codegen
- Related: ADR-002 (FastAPI + React Stack)

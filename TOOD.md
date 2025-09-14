# Interface Contracts for FastAPI + React Stack

For your **FastAPI backend** and **React frontend** setup, there are several excellent approaches to enforce contracts that guarantee compatibility between your components when tested separately.

## 1. **OpenAPI + TypeScript SDK Generation (Recommended)**

This is the most seamless approach for FastAPI + React, leveraging FastAPI's automatic OpenAPI generation:[1][2][3]

### Backend Setup (FastAPI)

FastAPI automatically generates OpenAPI schemas from your Pydantic models:

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="User API", version="1.0.0")

class User(BaseModel):
    id: int = Field(..., gt=0, description="User ID")
    name: str = Field(..., min_length=1, description="User name")
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$', description="User email")
    status: str = Field(..., regex="^(active|inactive)$", description="User status")
    tags: Optional[List[str]] = Field(default=[], description="User tags")

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str
    tags: Optional[List[str]] = []

class UserResponse(BaseModel):
    message: str
    user: User

@app.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user(user_id: int):
    """Get user by ID"""
    return User(id=user_id, name="John Doe", email="john@example.com", status="active")

@app.post("/users/", response_model=UserResponse, tags=["users"])
async def create_user(user: UserCreate):
    """Create a new user"""
    new_user = User(id=123, **user.dict())
    return UserResponse(message="User created", user=new_user)

@app.get("/users/", response_model=List[User], tags=["users"])
async def get_users():
    """Get all users"""
    return [User(id=1, name="John", email="john@example.com", status="active")]
```

### Frontend TypeScript SDK Generation

Use **hey-api** (formerly openapi-ts) for optimal TypeScript client generation:[4][5]

```bash
# Install hey-api
npm install -D @hey-api/openapi-ts

# Generate TypeScript client
npx openapi-ts generate -i http://localhost:8000/openapi.json -o ./src/api
```

This generates fully-typed TypeScript interfaces and client functions:

```typescript
// Generated types and client
import { client, UserService } from './api';

// Configure the client
client.setConfig({
  baseUrl: 'http://localhost:8000',
});

// Type-safe API calls in React
const UserComponent: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const { data } = await UserService.getUsers();
      setUsers(data); // Fully typed as User[]
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const createUser = async (userData: UserCreate) => {
    try {
      const { data } = await UserService.createUser({ 
        requestBody: userData 
      });
      console.log(data.message); // TypeScript knows this is a string
      return data.user; // TypeScript knows this is a User
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  // Component JSX...
};
```

### Contract Testing with Generated Types

```python
# Backend contract tests
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_get_user_contract():
    """Test that API responds with correct schema"""
    response = client.get("/users/123")
    assert response.status_code == 200
    
    user_data = response.json()
    
    # Validate contract structure
    assert "id" in user_data
    assert "name" in user_data
    assert "email" in user_data
    assert "status" in user_data
    assert "tags" in user_data
    
    # Validate types and constraints
    assert isinstance(user_data["id"], int)
    assert user_data["id"] > 0
    assert isinstance(user_data["name"], str)
    assert len(user_data["name"]) > 0
    assert "@" in user_data["email"]
    assert user_data["status"] in ["active", "inactive"]

def test_create_user_contract():
    """Test create user endpoint contract"""
    user_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "tags": ["admin", "user"]
    }
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    
    response_data = response.json()
    assert "message" in response_data
    assert "user" in response_data
    assert response_data["user"]["name"] == user_data["name"]
```

```typescript
// Frontend contract tests (Jest + React Testing Library)
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserService } from '../api';
import UserComponent from '../UserComponent';

// Mock the API client
jest.mock('../api');
const mockUserService = UserService as jest.Mocked<typeof UserService>;

describe('User Component Contract Tests', () => {
  test('should handle user fetching with correct types', async () => {
    const mockUsers: User[] = [
      { id: 1, name: 'John', email: 'john@example.com', status: 'active', tags: [] }
    ];
    
    mockUserService.getUsers.mockResolvedValue({ 
      data: mockUsers,
      error: undefined 
    });

    render(<UserComponent />);
    
    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
    });
    
    // TypeScript ensures we can't access properties that don't exist
    expect(mockUsers[0].id).toBe(1); // ✅ TypeScript knows id exists
    // expect(mockUsers[0].nonExistent).toBe(1); // ❌ TypeScript error
  });

  test('should handle user creation with correct request format', async () => {
    const newUser: UserCreate = {
      name: 'Jane Doe',
      email: 'jane@example.com',
      tags: ['admin']
    };
    
    const mockResponse: UserResponse = {
      message: 'User created',
      user: { id: 2, ...newUser, status: 'active' }
    };
    
    mockUserService.createUser.mockResolvedValue({
      data: mockResponse,
      error: undefined
    });

    // Test component that creates users...
    // TypeScript ensures correct request format
  });
});
```

## 2. **Consumer-Driven Contract Testing with Pact**

For more rigorous contract testing between React and FastAPI:[6][7][8][9]

### Frontend Consumer Tests (React + Pact)

```javascript
// Install: npm install --save-dev @pact-foundation/pact
import { Pact, Matchers } from '@pact-foundation/pact';
import { UserService } from '../services/UserService';

const { like, eachLike, term } = Matchers;

describe('User Service Pact', () => {
  const provider = new Pact({
    consumer: 'ReactUserApp',
    provider: 'FastAPIUserService',
    port: 8888,
    log: './logs/pact.log',
    dir: './pacts',
    logLevel: 'INFO'
  });

  beforeAll(() => provider.setup());
  afterEach(() => provider.verify());
  afterAll(() => provider.finalize());

  describe('when getting a user', () => {
    beforeEach(() => {
      const userInteraction = {
        state: 'user with id 123 exists',
        uponReceiving: 'a request for user 123',
        withRequest: {
          method: 'GET',
          path: '/users/123',
          headers: {
            'Accept': 'application/json'
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: like(123),
            name: like('John Doe'),
            email: term({
              matcher: '^[^@]+@[^@]+\\.[^@]+$',
              generate: 'john@example.com'
            }),
            status: term({
              matcher: '^(active|inactive)$', 
              generate: 'active'
            }),
            tags: eachLike('admin')
          }
        }
      };

      return provider.addInteraction(userInteraction);
    });

    test('should return user data', async () => {
      const userService = new UserService(`http://localhost:${provider.mockService.port}`);
      const user = await userService.getUser(123);
      
      expect(user.id).toBe(123);
      expect(user.email).toMatch(/^[^@]+@[^@]+\.[^@]+$/);
      expect(['active', 'inactive']).toContain(user.status);
    });
  });
});
```

### Backend Provider Tests (FastAPI + Pact)

```python
# Install: pip install pact-python
import pytest
from pact import Verifier
from fastapi.testclient import TestClient
from main import app

def test_user_service_pact():
    verifier = Verifier(provider='FastAPIUserService', provider_base_url='http://localhost:8000')
    
    # Provider state setup
    def setup_user_exists():
        # Setup test data - user with id 123 exists
        pass
    
    def setup_no_user():
        # Setup test data - no user exists
        pass
    
    provider_states = {
        'user with id 123 exists': setup_user_exists,
        'no user exists': setup_no_user
    }
    
    # Verify contracts
    success, logs = verifier.verify_pacts(
        './pacts/reactuserapp-fastapiguserservice.json',
        provider_states=provider_states,
        verbose=True
    )
    
    assert success, f"Pact verification failed: {logs}"
```

## 3. **Runtime Schema Validation**

Add runtime validation to catch contract violations:[10][11]

```python
# Backend - Enhanced validation
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import jsonschema

app = FastAPI()

# Define JSON Schema for additional validation
USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "email": {"type": "string", "pattern": "^[^@]+@[^@]+\\.[^@]+$"},
        "status": {"type": "string", "enum": ["active", "inactive"]},
        "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["id", "name", "email", "status"]
}

@app.middleware("http")
async def validate_response_schema(request: Request, call_next):
    response = await call_next(request)
    
    if request.url.path.startswith('/users') and response.status_code == 200:
        # Add response validation in development/testing
        pass
    
    return response
```

```typescript
// Frontend - Runtime validation with Zod
import { z } from 'zod';

const UserSchema = z.object({
  id: z.number().positive(),
  name: z.string().min(1),
  email: z.string().email(),
  status: z.enum(['active', 'inactive']),
  tags: z.array(z.string()).default([])
});

type User = z.infer<typeof UserSchema>;

// Runtime validation wrapper
async function fetchUserWithValidation(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data = await response.json();
  
  try {
    return UserSchema.parse(data); // Throws if invalid
  } catch (error) {
    console.error('Contract violation detected:', error);
    throw new Error('Backend response does not match expected schema');
  }
}
```

## 4. **Automated Contract Testing Pipeline**

Set up CI/CD integration for continuous contract validation:[12][13][2]

```yaml
# .github/workflows/contract-testing.yml
name: Contract Testing

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Python dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest httpx
      
      - name: Install Node.js dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Start FastAPI backend
        run: |
          uvicorn main:app --host 0.0.0.0 --port 8000 &
          sleep 5
      
      - name: Generate TypeScript client
        run: |
          cd frontend
          npx openapi-ts generate -i http://localhost:8000/openapi.json -o ./src/api
      
      - name: Run backend contract tests
        run: pytest tests/test_contracts.py -v
      
      - name: Run frontend contract tests
        run: |
          cd frontend
          npm run test -- --coverage --watchAll=false
      
      - name: Publish Pact contracts (if using Pact)
        if: github.ref == 'refs/heads/main'
        run: |
          cd frontend
          npm run pact:publish
```

## Best Practices for FastAPI + React Contracts

### 1. **Version Your APIs**
```python
from fastapi import FastAPI

app = FastAPI(title="User API", version="2.0.0")

@app.get("/v1/users/{user_id}", deprecated=True)
async def get_user_v1(user_id: int):
    """Deprecated - use v2"""
    pass

@app.get("/v2/users/{user_id}")
async def get_user_v2(user_id: int):
    """Current version"""
    pass
```

### 2. **Use Environment-Specific Configs**
```typescript
// config.ts
const config = {
  development: {
    apiUrl: 'http://localhost:8000',
    validateResponses: true
  },
  production: {
    apiUrl: 'https://api.yourapp.com',
    validateResponses: false
  }
};

export default config[process.env.NODE_ENV || 'development'];
```

### 3. **Implement Graceful Degradation**
```typescript
// Handle contract changes gracefully
interface UserV1 {
  id: number;
  name: string;
  email: string;
}

interface UserV2 extends UserV1 {
  status: 'active' | 'inactive';
  tags: string[];
}

function adaptUserResponse(data: any): UserV2 {
  return {
    id: data.id,
    name: data.name,
    email: data.email,
    status: data.status || 'active', // Default for backward compatibility
    tags: data.tags || [] // Default for backward compatibility
  };
}
```

The **OpenAPI + TypeScript SDK generation** approach is most recommended for FastAPI + React because it leverages FastAPI's built-in capabilities, provides excellent developer experience with full type safety, and integrates seamlessly with modern React development workflows. Combined with runtime validation and automated testing, this approach ensures robust contract enforcement while maintaining development velocity.[13][2][14][3][12][1][4]

[1](https://fastapi.tiangolo.com/advanced/generate-clients/)
[2](https://abhayramesh.com/blog/type-safe-fullstack)
[3](https://www.speakeasy.com/openapi/frameworks/fastapi)
[4](https://github.com/hey-api/openapi-ts)
[5](https://github.com/debkanchan/sdking)
[6](https://www.codecentric.de/en/knowledge-hub/blog/consumer-driven-contract-testing-with-pact)
[7](https://reflectoring.io/pact-react-consumer/)
[8](https://github.com/paucls/pact-consumer-contract-react-example)
[9](https://github.com/pactflow/example-provider-python)
[10](https://zuplo.com/learning-center/how-api-schema-validation-boosts-effective-contract-testing)
[11](https://www.linkedin.com/pulse/difference-between-schema-contract-validation-api-testing-dandapat-fxx6f)
[12](https://testdriven.io/blog/fastapi-react/)
[13](https://dev.to/yagnesh97/building-a-modern-web-app-fastapi-react-typescript-template-5d88)
[14](https://www.joshfinnie.com/blog/fastapi-and-react-in-2025/)
[15](https://www.youtube.com/watch?v=0zb2kohYZIM)
[16](https://fastapi.tiangolo.com/tutorial/testing/)
[17](https://stackoverflow.com/questions/62928450/how-to-put-backend-and-frontend-together-returning-react-frontend-from-fastapi)
[18](https://fastapi.tiangolo.com/advanced/async-tests/)
[19](https://www.reddit.com/r/FastAPI/comments/1c0ppuh/update_fastapi_gen_cli_v1_generate_fastapi/)
[20](https://ajac-zero.com/posts/building-react-fastapi-app-with-nginx-unit/)
[21](https://fastapiexpert.com/blog/2022/11/03/contract-testing-with-httpx/)
[22](https://www.reddit.com/r/FastAPI/comments/1dqhvtv/fastapi_react/)
[23](https://fastapi.tiangolo.com/de/advanced/generate-clients/)
[24](https://www.packtpub.com/en-in/product/full-stack-fastapi-react-and-mongodb-9781835886762?type=print)
[25](https://www.reddit.com/r/FastAPI/comments/16x3d6z/mastering_integration_testing_with_fastapi/)
[26](https://www.youtube.com/watch?v=13tMEW8r6C0)
[27](https://www.youtube.com/watch?v=aSdVU9-SxH4)
[28](https://fastapi.tiangolo.com/project-generation/)
[29](https://fastapi.xiniushu.com/sv/advanced/generate-clients/)
[30](https://github.com/fastapi/full-stack-fastapi-template)
[31](https://www.speakeasy.com/blog/pact-vs-openapi)
[32](https://docs.pact.io/implementation_guides/python/examples)
[33](https://github.com/OpenAPITools/openapi-generator)
[34](https://www.reddit.com/r/FastAPI/comments/1h0kcd6/fastapi_react_full_stack/)
[35](https://www.sigs.de/artikel/consumer-driven-contracts-mit-pact/)
[36](https://www.reddit.com/r/FastAPI/comments/1f1tn8w/fastapi_typescript_codegen/)
# Testing Best Practices

This document outlines the recommended approaches and best practices for writing tests in the LangPlug project.

## Async Test Patterns

### Standard Async Test Structure

All new tests should follow the async test pattern using the `anyio` marker:

```python
import pytest

@pytest.mark.anyio
async def test_example(async_client, url_builder):
    # Test implementation using async_client
    response = await async_client.get("/api/endpoint")
    assert response.status_code == 200
```

### Available Fixtures

#### Core Fixtures
- `async_client` - HTTPX async client for making API requests
- `url_builder` - Utility for generating URLs from route names
- `db_session` - Database session for direct database operations

#### Authentication Fixtures
- `auth_header` - Pre-authenticated header for simple tests
- `AuthTestHelperAsync` - Class with static methods for complex auth flows

## Authentication Testing

### Using Pre-built Auth Headers

For simple tests that need authentication:

```python
@pytest.mark.anyio
async def test_protected_endpoint(async_client, auth_header, url_builder):
    url = url_builder.url_for("profile_get")
    response = await async_client.get(url, headers=auth_header)
    assert response.status_code == 200
```

### Custom Authentication Flows

For tests requiring specific user data or multiple auth steps:

```python
@pytest.mark.anyio
async def test_custom_auth_flow(async_client, url_builder):
    # Perform custom registration
    register_url = url_builder.url_for("register:register")
    reg_response = await async_client.post(register_url, json={
        "username": "testuser",
        "email": "test@example.com", 
        "password": "TestPass123!"
    })
    assert reg_response.status_code == 201
    
    # Perform login
    login_url = url_builder.url_for("auth:jwt-bearer.login")
    login_response = await async_client.post(login_url, data={
        "username": "test@example.com",
        "password": "TestPass123!"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert login_response.status_code in [200, 204]
    
    # Extract auth token/cookies and use for subsequent requests
```

### Using AuthTestHelperAsync

For standardized authentication patterns:

```python
from tests.auth_helpers import AuthTestHelperAsync

@pytest.mark.anyio
async def test_with_helper(async_client, url_builder):
    # Get auth headers with default user data
    auth_headers = await AuthTestHelperAsync.get_auth_headers(async_client, url_builder)
    
    # Or with custom user data
    custom_user_data = {
        "username": "customuser",
        "email": "custom@example.com",
        "password": "CustomPass123!"
    }
    auth_headers = await AuthTestHelperAsync.get_auth_headers(
        async_client, url_builder, custom_user_data
    )
    
    # Use the auth headers in requests
    profile_url = url_builder.url_for("profile_get")
    response = await async_client.get(profile_url, headers=auth_headers)
    assert response.status_code == 200
```

## URL Generation Best Practices

### Always Use URL Builder

Never hardcode URL paths in tests:

```python
# ❌ Bad - hardcoded paths break when routes change
response = await async_client.get("/api/profile")

# ✅ Good - named routes are robust to changes
url = url_builder.url_for("profile_get")
response = await async_client.get(url)
```

### Dynamic Route Parameters

For routes with path parameters:

```python
# ✅ Good - URL builder handles parameter substitution
url = url_builder.url_for("get_video_status", video_id="test_video.mp4")
response = await async_client.get(url)

# ✅ Good - Works with complex parameter structures
stream_url = url_builder.url_for("stream_video", series="TestSeries", episode="S01E01")
response = await async_client.get(stream_url)
```

## Database Testing

### Using Database Sessions

For tests requiring direct database access:

```python
@pytest.mark.anyio
async def test_database_operation(db_session, async_client, url_builder):
    # Create test data directly in database
    from database.models import User
    user = User(email="test@example.com", username="testuser")
    db_session.add(user)
    await db_session.commit()
    
    # Test API interaction with the database state
    url = url_builder.url_for("get_user", user_id=str(user.id))
    response = await async_client.get(url)
    assert response.status_code == 200
```

### Transaction Rollback for Isolation

Each test runs in a transaction that is rolled back, ensuring perfect test isolation:

```python
@pytest.mark.anyio
async def test_data_isolation(db_session):
    # Changes made in this test are automatically rolled back
    # and won't affect other tests
    pass
```

## Test Organization

### File Naming Convention

- Contract tests: `test_*_contract_improved.py`
- Integration tests: `test_*_integration.py` 
- Unit tests: `test_*_unit.py`
- Negative/scenario tests: `test_*_negative.py` or `test_*_scenarios.py`

### Test Class Structure

Group related tests in classes:

```python
@pytest.mark.anyio
@pytest.mark.api
class TestUserProfileContract:
    """Contract tests for user profile API endpoints"""
    
    async def test_get_profile_success(self, async_client, auth_header, url_builder):
        # Test implementation
    
    async def test_update_profile_validation(self, async_client, auth_header, url_builder):
        # Test implementation
```

## Response Validation

### Structured Response Checking

Always validate response structure, not just status codes:

```python
@pytest.mark.anyio
async def test_user_profile_structure(async_client, auth_header, url_builder):
    url = url_builder.url_for("profile_get")
    response = await async_client.get(url, headers=auth_header)
    
    assert response.status_code == 200
    data = response.json()
    
    # Validate required fields exist
    assert "id" in data
    assert "username" in data
    assert "email" in data
    
    # Validate data types
    assert isinstance(data["id"], (int, str))
    assert isinstance(data["username"], str)
    assert isinstance(data["email"], str)
```

### Error Response Validation

Test error cases thoroughly:

```python
@pytest.mark.anyio
async def test_invalid_input_returns_422(async_client, auth_header, url_builder):
    url = url_builder.url_for("profile_update_languages")
    response = await async_client.put(url, json={
        "native_language": "invalid_code",  # Invalid language code
        "target_language": "de"
    }, headers=auth_header)
    
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
    assert isinstance(error_data["detail"], list)  # FastAPI validation errors are lists
```

## Mocking and Stubbing

### When to Mock

Only mock external services or complex dependencies:

```python
from unittest.mock import patch, Mock

@pytest.mark.anyio
async def test_external_service_failure(async_client, auth_header, url_builder):
    with patch('services.external_api.call_service') as mock_service:
        mock_service.side_effect = Exception("Service unavailable")
        
        url = url_builder.url_for("external_endpoint")
        response = await async_client.post(url, headers=auth_header)
        
        assert response.status_code == 503  # Service unavailable
```

### Avoid Over-Mocking

Don't mock the database or core application services in contract tests - test the real integration.

## Performance Considerations

### Test Database Optimization

Tests use in-memory SQLite databases for speed and isolation. Avoid heavy database setup in individual tests.

### Parallel Test Execution

Tests are designed to run in parallel. Ensure test isolation and avoid shared state between tests.

## Security Testing

### Authentication Required Tests

Always test that protected endpoints require authentication:

```python
@pytest.mark.anyio
async def test_protected_endpoint_requires_auth(async_client, url_builder):
    url = url_builder.url_for("protected_resource")
    response = await async_client.get(url)  # No auth headers
    assert response.status_code == 401  # Unauthorized
```

### Input Validation Tests

Test that endpoints properly validate input:

```python
@pytest.mark.anyio
async def test_input_validation(async_client, auth_header, url_builder):
    url = url_builder.url_for("update_resource")
    response = await async_client.put(url, json={
        "required_field": None  # Invalid value
    }, headers=auth_header)
    
    assert response.status_code == 422  # Validation error
```

## Debugging Tips

### Verbose Test Output

Run tests with verbose output to see detailed information:

```bash
python -m pytest tests/api/test_example.py::test_name -v -s
```

### Selective Test Execution

Run only asyncio backend tests to avoid trio compatibility issues:

```bash
python -m pytest tests/ -k "asyncio" -v
```

### Test Database Inspection

For debugging database-related issues, you can inspect the test database state:

```python
@pytest.mark.anyio
async def test_database_debug(db_session):
    # Query database directly
    result = await db_session.execute(select(User).where(User.username == "test"))
    user = result.scalar_one_or_none()
    
    # Print debug information
    print(f"Found user: {user}")
```

Following these best practices will ensure your tests are robust, maintainable, and provide reliable validation of the LangPlug API functionality.
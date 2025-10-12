# Security and Transaction Management

This document describes the security hardening and transaction management improvements implemented in LangPlug.

## Table of Contents

1. [Security Modules](#security-modules)
   - [File Security Validation](#file-security-validation)
   - [Password Validation](#password-validation)
   - [Token Service](#token-service)
2. [Transaction Management](#transaction-management)
   - [Transactional Decorator](#transactional-decorator)
   - [Transaction Context](#transaction-context)
   - [Best Practices](#best-practices)
3. [Migration Guide](#migration-guide)

---

## Security Modules

### File Security Validation

**Location**: `Backend/core/file_security.py`

The `FileSecurityValidator` class provides comprehensive file upload security validation to prevent common attacks:

#### Features

1. **Path Traversal Prevention**
   - Blocks `../`, absolute paths, and directory separators
   - Validates paths are within allowed directories
   - Sanitizes filenames by removing dangerous characters

2. **File Type Validation**
   - Whitelist-based extension validation
   - Case-insensitive extension matching
   - Supports videos, subtitles, images, and documents

3. **File Size Limits**
   - Enforces 500MB maximum file size
   - Prevents empty file uploads
   - Memory-efficient validation using file seek

#### Usage

```python
from core.file_security import FileSecurityValidator
from fastapi import UploadFile

# Validate file upload
allowed_extensions = {".mp4", ".avi", ".mkv"}
try:
    safe_path = await FileSecurityValidator.validate_file_upload(
        video_file,
        allowed_extensions
    )
except ValueError as e:
    # Handle validation error
    raise HTTPException(status_code=400, detail=str(e))

# Sanitize filename
safe_name = FileSecurityValidator.sanitize_filename("../../../etc/passwd")
# Returns: "etcpasswd"

# Validate file path
try:
    validated_path = FileSecurityValidator.validate_file_path(user_input_path)
except ValueError as e:
    # Path traversal or outside allowed directory
    raise HTTPException(status_code=400, detail=str(e))
```

#### Configuration

Set the allowed upload directory via environment variable:

```bash
export UPLOAD_DIR="/app/uploads"
```

Default: `/app/uploads`

---

### Password Validation

**Location**: `Backend/services/authservice/password_validator.py`

The `PasswordValidator` enforces strong password policies using Argon2 hashing (more secure than bcrypt).

#### Password Requirements

- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&\*...)
- Not in common passwords list

#### Usage

```python
from services.authservice.password_validator import PasswordValidator

# Validate password strength
is_valid, error_msg = PasswordValidator.validate("SecurePass123!")
if not is_valid:
    raise ValueError(error_msg)

# Hash password
hashed = PasswordValidator.hash_password("SecurePass123!")

# Verify password
is_correct = PasswordValidator.verify_password("SecurePass123!", hashed)

# Check if hash needs update
if PasswordValidator.needs_rehash(hashed):
    # Rehash with current settings
    new_hash = PasswordValidator.hash_password(plain_password)
```

#### Migration from bcrypt

The system automatically migrates from bcrypt to Argon2. When a user logs in:

1. Password is verified against existing hash (bcrypt or Argon2)
2. If hash needs update, password is rehashed with Argon2
3. Updated hash is stored in database

---

### Token Service

**Location**: `Backend/services/authservice/token_service.py`

The `TokenService` implements JWT-based authentication with access and refresh tokens.

#### Token Types

| Token Type    | Lifetime | Purpose                    |
| ------------- | -------- | -------------------------- |
| Access Token  | 1 hour   | API authorization          |
| Refresh Token | 30 days  | Generate new access tokens |

#### Usage

```python
from services.authservice.token_service import TokenService

# Create token pair
tokens = TokenService.create_token_pair(user_id=123)
# Returns: {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer",
#   "expires_in": 3600
# }

# Verify access token
user_id = TokenService.verify_access_token(access_token)

# Refresh access token
new_access_token = TokenService.refresh_access_token(refresh_token)

# Check token expiration
is_expired = TokenService.is_token_expired(token)
```

#### Security Features

1. **Token Type Validation**: Prevents using access token for refresh and vice versa
2. **Short-Lived Access Tokens**: Reduced from 24h to 1h for security
3. **Refresh Token Rotation**: Can implement token rotation for enhanced security
4. **Constant-Time Comparison**: Uses cryptographically secure token validation

#### API Endpoint

**POST** `/auth/token/refresh`

Exchanges refresh token (from HTTP-only cookie) for new access token.

```bash
curl -X POST /auth/token/refresh \
  -H "Cookie: refresh_token=eyJ..."
```

Response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## Transaction Management

### Transactional Decorator

**Location**: `Backend/core/transaction.py`

The `@transactional` decorator provides automatic transaction management for database operations.

#### How It Works

1. Automatically detects `AsyncSession` parameter
2. Wraps function in `begin_nested()` (savepoint)
3. Commits on success
4. Rolls back on exception
5. Re-raises exception for proper error handling

#### Usage

```python
from core.transaction import transactional
from sqlalchemy.ext.asyncio import AsyncSession

@transactional
async def create_user_with_profile(session: AsyncSession, username: str):
    # Multiple DB operations in single transaction
    user = User(username=username)
    session.add(user)
    await session.flush()

    profile = UserProfile(user_id=user.id)
    session.add(profile)

    # Both operations committed together
    return user

# Transaction automatically managed
user = await create_user_with_profile(db_session, "johndoe")
```

#### When to Use

**Use `@transactional` when:**

- Function receives session as parameter
- Multiple related DB operations need atomicity
- Operations are short-lived (< 1 second)

**Don't use `@transactional` when:**

- Session is instance variable (use manual transaction)
- Operations include long-running tasks (ML inference, file I/O)
- Function doesn't perform database operations

---

### Transaction Context

For explicit transaction control, use `TransactionContext`:

```python
from core.transaction import TransactionContext

async def complex_operation(session: AsyncSession):
    async with TransactionContext(session):
        # Multiple operations
        await repo.create_user(user_data)
        await repo.send_welcome_email(user_data.email)
        # Commits on exit, rolls back on exception
```

---

### Best Practices

#### 1. Keep Transactions Short

**Bad**: Long-running transaction holds locks

```python
@transactional
async def process_video(session: AsyncSession, video_path: str):
    # Extract audio (30 seconds)
    audio = await extract_audio(video_path)
    # Transcribe (60 seconds)
    text = await transcribe(audio)
    # Store in DB
    session.add(Transcription(text=text))
```

**Good**: Only wrap database operations

```python
async def process_video(session: AsyncSession, video_path: str):
    # Long-running operations outside transaction
    audio = await extract_audio(video_path)
    text = await transcribe(audio)

    # Only DB operation in transaction
    @transactional
    async def store_result(session: AsyncSession, text: str):
        session.add(Transcription(text=text))

    await store_result(session, text)
```

#### 2. Use Specific Exceptions

**Bad**: Catching all exceptions

```python
try:
    result = TokenService.refresh_access_token(token)
except Exception as e:  # Too broad
    return None
```

**Good**: Catch specific exceptions

```python
from core.exceptions import AuthenticationError

try:
    result = TokenService.refresh_access_token(token)
except AuthenticationError as e:  # Specific
    raise HTTPException(status_code=401, detail="Invalid token")
```

#### 3. Manual Transactions for Instance Variables

When session is an instance variable, use manual transaction management:

```python
class ChunkProcessor:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def process_chunk(self, ...):
        # Manual transaction because session is self.db_session
        async with self.db_session.begin_nested():
            try:
                # Database operations
                await self._filter_vocabulary(...)
            except Exception as e:
                # Rollback automatic
                raise
```

#### 4. Nested Transactions (Savepoints)

`begin_nested()` creates savepoints, not true nested transactions:

```python
async with session.begin():  # Outer transaction
    user = User(...)
    session.add(user)

    try:
        async with session.begin_nested():  # Savepoint
            # This can fail independently
            risky_operation()
    except Exception:
        # Savepoint rolled back, outer transaction continues
        pass

    # Outer transaction commits
```

---

## Migration Guide

### Upgrading Authentication

#### Step 1: Update Password Validation

Old code:

```python
if len(password) < 8:
    raise ValueError("Password too short")
```

New code:

```python
from services.authservice.password_validator import PasswordValidator

is_valid, error = PasswordValidator.validate(password)
if not is_valid:
    raise ValueError(error)
```

#### Step 2: Implement Token Refresh

Add refresh token endpoint to your authentication flow:

```python
from services.authservice.token_service import TokenService

@router.post("/token/refresh")
async def refresh_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(401, "Refresh token required")

    try:
        new_token = TokenService.refresh_access_token(refresh_token)
        return {"access_token": new_token, "token_type": "bearer"}
    except AuthenticationError:
        raise HTTPException(401, "Invalid refresh token")
```

#### Step 3: Update Frontend

Implement automatic token refresh:

```typescript
// Refresh token when access token expires
async function refreshAccessToken() {
  const response = await fetch("/auth/token/refresh", {
    method: "POST",
    credentials: "include", // Send refresh token cookie
  });

  const data = await response.json();
  localStorage.setItem("access_token", data.access_token);
  return data.access_token;
}

// Intercept 401 errors
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response.status === 401) {
      const newToken = await refreshAccessToken();
      // Retry original request
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return axios.request(error.config);
    }
    throw error;
  },
);
```

---

### Adding File Upload Security

Update file upload routes:

Old code:

```python
@router.post("/upload")
async def upload(file: UploadFile):
    # No validation
    with open(f"/uploads/{file.filename}", "wb") as f:
        f.write(await file.read())
```

New code:

```python
from core.file_security import FileSecurityValidator

@router.post("/upload")
async def upload(file: UploadFile):
    # Validate security
    try:
        safe_path = await FileSecurityValidator.validate_file_upload(
            file,
            allowed_extensions={".mp4", ".avi"}
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Write to validated path
    with open(safe_path, "wb") as f:
        f.write(await file.read())
```

---

### Converting to Transactional Decorator

Old code:

```python
async def create_user(session: AsyncSession, data: dict):
    try:
        user = User(**data)
        session.add(user)
        await session.commit()
        return user
    except Exception:
        await session.rollback()
        raise
```

New code:

```python
from core.transaction import transactional

@transactional
async def create_user(session: AsyncSession, data: dict):
    user = User(**data)
    session.add(user)
    # Commit/rollback handled automatically
    return user
```

---

## Testing

All security modules have comprehensive unit tests:

```bash
# Test file security
pytest Backend/tests/unit/core/test_file_security.py

# Test password validation
pytest Backend/tests/unit/services/authservice/test_password_validator.py

# Test token service
pytest Backend/tests/unit/services/authservice/test_token_service.py

# Test transaction management
pytest Backend/tests/unit/core/test_transaction.py
```

---

## Security Checklist

Before deploying:

- [ ] All file uploads use `FileSecurityValidator`
- [ ] Password validation enforces 12+ character requirement
- [ ] JWT tokens use 1-hour expiration for access tokens
- [ ] Refresh tokens stored in HTTP-only cookies
- [ ] Database operations use `@transactional` or manual transactions
- [ ] Error handlers catch specific exceptions, not `Exception`
- [ ] File paths validated to prevent traversal attacks
- [ ] Unit tests pass for all security modules

---

## Further Reading

- [OWASP File Upload Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [Argon2 Password Hashing](https://github.com/p-h-c/phc-winner-argon2)
- [SQLAlchemy Transactions](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)

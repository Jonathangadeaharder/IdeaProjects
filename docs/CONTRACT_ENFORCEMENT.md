# Contract Enforcement Guide

This guide explains the comprehensive contract enforcement system implemented for LangPlug to ensure API compatibility between frontend and backend.

## Overview

The contract enforcement system provides multiple layers of validation:

1. **Server-side validation** - FastAPI middleware validates requests/responses
2. **Client-side validation** - TypeScript schemas validate API calls
3. **Development workflow** - Automated checks and regeneration
4. **Pre-commit hooks** - Prevents contract violations from being committed

## Components

### 1. Server-Side Contract Validation

**File**: `Backend/core/contract_middleware.py`

The middleware automatically validates:
- Request paths exist in OpenAPI spec
- HTTP methods are defined for endpoints
- Response status codes match the contract
- Logs contract violations for debugging

**Configuration** (in `Backend/core/app.py`):
```python
if settings.debug:
    setup_contract_validation(
        app,
        validate_requests=True,
        validate_responses=True,
        log_violations=True
    )
```

### 2. Client-Side Contract Validation

**Files**:
- `Frontend/src/utils/contract-validation.ts` - Zod schemas and validation helpers
- `Frontend/src/client/services.gen.ts` - Generated SDK from OpenAPI spec

**Features**:
- Runtime type guards for high-risk flows
- Centralised error handling via `services/api.ts`
- Direct usage of generated request functions (no custom wrappers)
- Type-safe API calls through the OpenAPI-generated types

### 3. Development Workflow Integration

**Contract Validation Script**: `scripts/validate-contract.ts`

Automatically checks:
- OpenAPI spec exists and is valid
- Generated client files are up-to-date
- Contract schemas are properly defined
- Server middleware is configured

**NPM Scripts** (in `Frontend/package.json`):
```json
{
  "validate-contract": "cd .. && npx ts-node scripts/validate-contract.ts",
  "dev:full": "npm run generate-client && npm run validate-contract && npm run dev",
  "update-openapi": "cd ../Backend && python export_openapi.py && cd ../Frontend && npm run generate-client",
  "prebuild": "npm run generate-client && npm run validate-contract"
}
```

### 4. Pre-Commit Hook

**Setup Script**: `scripts/setup-pre-commit-hook.sh`

The hook automatically:
- Detects API-related file changes
- Updates OpenAPI spec when backend changes
- Validates contract compatibility
- Prevents commits if validation fails

## Workflow Guide

### Daily Development

1. **Start development with contract validation**:
   ```bash
   cd Frontend
   npm run dev:full
   ```

2. **When modifying backend APIs**:
   ```bash
   # After making backend changes
   cd Frontend
   npm run update-openapi
   npm run validate-contract
   ```

3. **When adding new API endpoints**:
   - Update backend code with proper FastAPI annotations
   - Run `npm run update-openapi` to regenerate spec
   - Add or update Zod schemas in `contract-validation.ts` where runtime validation is needed
   - Call the generated function from `services.gen.ts`
   - Run `npm run validate-contract` to verify

### Setting Up Contract Enforcement

1. **Install pre-commit hook**:
   ```bash
   ./scripts/setup-pre-commit-hook.sh
   ```

2. **Validate current setup**:
   ```bash
   cd Frontend
   npm run validate-contract
   ```

### Troubleshooting

#### Common Issues

**"OpenAPI spec not found"**
```bash
cd Backend
python export_openapi.py
```

**"Generated client files outdated"**
```bash
cd Frontend
npm run generate-client
```

**"Contract validation failed"**
1. Check server is running: `npm run dev` (Backend)
2. Verify OpenAPI spec is current: `npm run update-openapi`
3. Check for schema mismatches in validation output

#### Error Types

- **ContractValidationError**: API response doesn't match expected schema
- **ApiValidationError**: Request validation failed
- **ApiRequestError**: Network or HTTP error

### Best Practices

1. **Always validate contracts before pushing**:
   ```bash
   npm run validate-contract
   ```

2. **Use the generated SDK for API calls**:
   ```typescript
   import { getVideosApiVideosGet } from '@/client/services.gen'

   const videos = await getVideosApiVideosGet()
   ```

3. **Keep schemas synchronized**:
   - Backend changes → regenerate OpenAPI → update frontend schemas
   - Use TypeScript types from contract schemas
   - Document schema changes in commit messages

4. **Monitor contract violations in development**:
   - Check browser console for validation errors
   - Review server logs for middleware warnings
   - Fix violations before they reach production

## Contract Evolution

When evolving APIs:

1. **Backwards-compatible changes** (safe):
   - Adding optional fields
   - Adding new endpoints
   - Adding new response codes

2. **Breaking changes** (requires coordination):
   - Removing fields
   - Changing field types
   - Modifying required fields
   - Removing endpoints

For breaking changes:
1. Plan the migration strategy
2. Update backend with versioning if needed
3. Update frontend schemas and client
4. Test compatibility thoroughly
5. Deploy in coordinated manner

## Monitoring and Debugging

### Development

- Contract violations logged to console
- Middleware adds headers: `X-Contract-Validated`, `X-Request-Validation`
- Detailed error messages with endpoint context

### Production

- Server-side validation disabled by default
- Client-side validation remains active
- Monitor for ContractValidationError in error tracking

## Benefits

1. **Early Detection**: Catch API mismatches during development
2. **Type Safety**: Full TypeScript support with runtime validation
3. **Automated Workflow**: No manual steps to maintain compatibility
4. **Documentation**: Self-documenting API contracts
5. **Confidence**: Deploy knowing frontend/backend are compatible

This contract enforcement system ensures robust API compatibility and reduces integration issues between frontend and backend teams.

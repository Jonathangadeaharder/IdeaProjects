"""
Contract validation middleware for FastAPI
Provides server-side validation of requests and responses against OpenAPI schema
"""
import json
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class ContractValidationError(Exception):
    """Exception raised when contract validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ContractValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate requests and responses against OpenAPI contract"""

    def __init__(
        self,
        app: ASGIApp,
        validate_requests: bool = True,
        validate_responses: bool = True,
        log_violations: bool = True
    ):
        super().__init__(app)
        self.validate_requests = validate_requests
        self.validate_responses = validate_responses
        self.log_violations = log_violations
        self._openapi_schema: Optional[Dict[str, Any]] = None

    def get_openapi_schema(self, app: FastAPI) -> Dict[str, Any]:
        """Get cached OpenAPI schema from the FastAPI app"""
        if self._openapi_schema is None:
            self._openapi_schema = app.openapi()
        return self._openapi_schema

    def validate_request_path(self, method: str, path: str, schema: Dict[str, Any]) -> bool:
        """Validate if the request path and method exist in the OpenAPI schema"""
        paths = schema.get("paths", {})

        # Check for exact path match
        if path in paths and method.lower() in paths[path]:
            return True

        # Check for path parameters (simple pattern matching)
        for schema_path in paths:
            if self._path_matches_pattern(path, schema_path):
                if method.lower() in paths[schema_path]:
                    return True

        return False

    def _path_matches_pattern(self, actual_path: str, schema_path: str) -> bool:
        """Check if actual path matches OpenAPI path pattern with parameters"""
        actual_parts = actual_path.strip("/").split("/")
        schema_parts = schema_path.strip("/").split("/")

        if len(actual_parts) != len(schema_parts):
            return False

        for actual_part, schema_part in zip(actual_parts, schema_parts):
            # Check if schema part is a parameter (enclosed in {})
            if schema_part.startswith("{") and schema_part.endswith("}"):
                continue  # Parameter matches any value
            elif actual_part != schema_part:
                return False

        return True

    def validate_response_status(self, path: str, method: str, status_code: int, schema: Dict[str, Any]) -> bool:
        """Validate if the response status code is defined in the OpenAPI schema"""
        paths = schema.get("paths", {})

        # Find matching path
        matching_path = None
        if path in paths:
            matching_path = path
        else:
            for schema_path in paths:
                if self._path_matches_pattern(path, schema_path):
                    matching_path = schema_path
                    break

        if not matching_path:
            return False

        path_spec = paths[matching_path]
        method_spec = path_spec.get(method.lower(), {})
        responses = method_spec.get("responses", {})

        # Check if status code is defined (exact match or 'default')
        return str(status_code) in responses or "default" in responses

    async def dispatch(self, request: Request, call_next):
        """Process the request and validate contract compliance"""
        method = request.method
        path = str(request.url.path)

        # Skip OPTIONS requests (CORS preflight)
        if method == "OPTIONS":
            response = await call_next(request)
            return response

        # Skip subtitle serving endpoint (uses dynamic paths)
        if path.startswith("/api/videos/subtitles/"):
            response = await call_next(request)
            return response

        # Get the FastAPI app instance to access OpenAPI schema
        app = request.app

        try:
            # Validate request if enabled
            if self.validate_requests:
                schema = self.get_openapi_schema(app)
                if not self.validate_request_path(method, path, schema):
                    if self.log_violations:
                        logger.warning(f"Contract violation: Undefined endpoint {method} {path}")

                    # Return 404 for undefined endpoints
                    return JSONResponse(
                        status_code=404,
                        content={
                            "detail": "Endpoint not found in API contract",
                            "path": path,
                            "method": method
                        }
                    )

            # Process the request
            response = await call_next(request)

            # Validate response if enabled
            if self.validate_responses:
                schema = self.get_openapi_schema(app)
                if not self.validate_response_status(path, method, response.status_code, schema):
                    if self.log_violations:
                        logger.warning(
                            f"Contract violation: Undefined response status {response.status_code} "
                            f"for {method} {path}"
                        )

            # Add contract validation headers
            response.headers["X-Contract-Validated"] = "true"
            response.headers["X-Request-Validation"] = str(self.validate_requests).lower()
            response.headers["X-Response-Validation"] = str(self.validate_responses).lower()

            return response

        except RequestValidationError as e:
            # Handle FastAPI validation errors
            if self.log_violations:
                logger.error(f"Request validation error for {method} {path}: {e}")

            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Request validation failed",
                    "errors": e.errors(),
                    "path": path,
                    "method": method
                }
            )

        except Exception as e:
            # Handle unexpected errors
            if self.log_violations:
                logger.error(f"Contract validation error for {method} {path}: {e}", exc_info=True)

            # Let the original error propagate for proper error handling
            raise


def setup_contract_validation(
    app: FastAPI,
    validate_requests: bool = True,
    validate_responses: bool = True,
    log_violations: bool = True
) -> None:
    """Setup contract validation middleware for the FastAPI app"""
    middleware = ContractValidationMiddleware(
        app=app,
        validate_requests=validate_requests,
        validate_responses=validate_responses,
        log_violations=log_violations
    )

    app.add_middleware(
        ContractValidationMiddleware,
        validate_requests=validate_requests,
        validate_responses=validate_responses,
        log_violations=log_violations
    )

    logger.info(
        f"Contract validation middleware enabled: "
        f"requests={validate_requests}, responses={validate_responses}, logging={log_violations}"
    )
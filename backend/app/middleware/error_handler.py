from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import google.genai.errors
from typing import Callable
from .error_utils import (
    handle_validation_error,
    handle_http_exception,
    handle_gemini_error,
    handle_unexpected_error
)

# Set up logging
logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling.

    This middleware catches exceptions raised during request processing,
    logs them appropriately, and returns standardized error responses.
    It uses the same error handling functions as the exception handlers
    to ensure consistent responses.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            # Process the request
            return await call_next(request)
        except Exception as exc:
            # Log the exception with traceback for server-side debugging
            logger.error(
                f"Error processing request {request.method} {request.url.path}",
                exc_info=True
            )

            # Handle different types of exceptions
            if isinstance(exc, RequestValidationError):
                # Handle validation errors (e.g., invalid request body)
                return handle_validation_error(exc)
            elif isinstance(exc, StarletteHTTPException):
                # Handle HTTP exceptions (e.g., 404, 403)
                return handle_http_exception(exc)
            elif isinstance(exc, google.genai.errors.APIError):
                # Handle Gemini API errors
                return handle_gemini_error(exc)
            else:
                # Handle unexpected errors
                return handle_unexpected_error(exc)
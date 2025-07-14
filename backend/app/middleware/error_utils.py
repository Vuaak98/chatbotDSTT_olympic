"""
Shared error handling utilities for both middleware and exception handlers.

This module contains functions for handling different types of errors
in a consistent way, ensuring the same responses regardless of whether
an error is caught by middleware or by FastAPI's exception handling.
"""

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import google.genai.errors

# Set up logging
logger = logging.getLogger(__name__)

def handle_validation_error(exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors from request data."""
    # Extract error details in a user-friendly format
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", "Validation error"),
            "type": error.get("type", "")
        })

    # Log the validation error
    logger.warning(f"Validation error: {error_details}")

    # Return a 422 Unprocessable Entity response
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": "The request data is invalid.",
            "validation_errors": error_details
        }
    )

def handle_http_exception(exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    # Log the HTTP exception
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")

    # Return a response with the appropriate status code
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP Error {exc.status_code}",
            "detail": exc.detail
        }
    )

def handle_gemini_error(exc: google.genai.errors.APIError) -> JSONResponse:
    """Handle Gemini API errors."""
    # Map Gemini API error codes to HTTP status codes
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_type = "AI Model Error"
    user_message = "There was an error processing your request with the AI model."

    # Extract error details from the Gemini API error
    error_code = getattr(exc, 'code', None)
    error_message = getattr(exc, 'message', str(exc))

    # Map specific Gemini error codes to user-friendly messages
    if error_code == 'INVALID_ARGUMENT':
        status_code = status.HTTP_400_BAD_REQUEST
        user_message = "The request to the AI model was invalid."
    elif error_code == 'PERMISSION_DENIED':
        status_code = status.HTTP_403_FORBIDDEN
        user_message = "Access to the AI model was denied."
    elif error_code == 'RESOURCE_EXHAUSTED':
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
        user_message = "The AI model's quota has been exceeded. Please try again later."
    elif error_code == 'UNAVAILABLE':
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        user_message = "The AI model is currently unavailable. Please try again later."
    elif error_code == 'DEADLINE_EXCEEDED':
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
        user_message = "The request to the AI model timed out. Please try with a simpler query."
    elif error_code == 'CANCELLED':
        status_code = status.HTTP_499_CLIENT_CLOSED_REQUEST
        user_message = "The request to the AI model was cancelled."
    elif 'content filtered' in error_message.lower() or 'safety' in error_message.lower():
        status_code = status.HTTP_400_BAD_REQUEST
        user_message = "Your request was filtered due to safety concerns. Please rephrase your question."

    # Log the Gemini API error
    logger.error(f"Gemini API error: {error_code} - {error_message}")

    # Return a response with the appropriate status code
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "detail": user_message,
            "code": error_code
        }
    )

def handle_unexpected_error(exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    import traceback
    
    # Log the unexpected error with full traceback
    logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")

    # Return a 500 Internal Server Error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later."
        }
    ) 
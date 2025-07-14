from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import google.genai.errors
from .error_utils import (
    handle_validation_error,
    handle_http_exception,
    handle_gemini_error
)

# Set up logging
logger = logging.getLogger(__name__)

def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    FastAPI exception handler for validation errors.
    
    This is registered with FastAPI to handle validation errors that occur
    during request processing.
    """
    # Use shared utility function for handling validation errors
    return handle_validation_error(exc)

def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    FastAPI exception handler for HTTP exceptions.
    
    This is registered with FastAPI to handle HTTP exceptions like 404, 403, etc.
    """
    # Use shared utility function for handling HTTP exceptions
    return handle_http_exception(exc)

def gemini_api_exception_handler(request: Request, exc: google.genai.errors.APIError):
    """
    FastAPI exception handler for Gemini API errors.
    
    This is registered with FastAPI to handle errors from the Gemini API.
    """
    # Use shared utility function for handling Gemini API errors
    return handle_gemini_error(exc)
from fastapi import Request, status
from fastapi.responses import JSONResponse
import time
from typing import Dict, List, Tuple, Optional
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Set up logging
logger = logging.getLogger(__name__)

class RateLimiter(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests.
    
    This middleware tracks requests by IP address and endpoint,
    and limits the number of requests that can be made within a time window.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Store request timestamps: {ip: {endpoint: [timestamps]}}
        self.request_records: Dict[str, Dict[str, List[float]]] = {}
        # Configure rate limits: {endpoint_prefix: (requests_per_window, window_seconds)}
        self.rate_limits = {
            "/chat/stream": (20, 60),  # 20 requests per minute for streaming
            "/upload-file": (30, 60),  # 30 requests per minute for file uploads
            "/": (100, 60)             # 100 requests per minute for all other endpoints
        }
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP address
        client_ip = self._get_client_ip(request)
        
        # Get the endpoint being accessed
        endpoint = request.url.path
        
        # Check if the request exceeds rate limits
        rate_limit_info = self._get_rate_limit_info(endpoint)
        if rate_limit_info and self._is_rate_limited(client_ip, endpoint, rate_limit_info):
            # If rate limited, return a 429 Too Many Requests response
            logger.warning(f"Rate limit exceeded for IP {client_ip} on endpoint {endpoint}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate Limit Exceeded",
                    "detail": "You have made too many requests. Please try again later."
                }
            )
        
        # Process the request
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract the client IP address from the request."""
        # Try to get the real IP from X-Forwarded-For header (if behind a proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs; the client IP is the first one
            return forwarded_for.split(",")[0].strip()
        
        # Fall back to the direct client IP
        return request.client.host if request.client else "unknown"
    
    def _get_rate_limit_info(self, endpoint: str) -> Optional[Tuple[int, int]]:
        """Get the rate limit info for the given endpoint."""
        # Check for exact match
        if endpoint in self.rate_limits:
            return self.rate_limits[endpoint]
        
        # Check for prefix match
        for prefix, limit_info in self.rate_limits.items():
            if endpoint.startswith(prefix):
                return limit_info
        
        # Default rate limit
        return self.rate_limits.get("/")
    
    def _is_rate_limited(self, client_ip: str, endpoint: str, rate_limit_info: Tuple[int, int]) -> bool:
        """Check if the request exceeds rate limits."""
        max_requests, window_seconds = rate_limit_info
        current_time = time.time()
        
        # Initialize records for this IP if not exists
        if client_ip not in self.request_records:
            self.request_records[client_ip] = {}
        
        # Initialize records for this endpoint if not exists
        if endpoint not in self.request_records[client_ip]:
            self.request_records[client_ip][endpoint] = []
        
        # Get timestamps for this IP and endpoint
        timestamps = self.request_records[client_ip][endpoint]
        
        # Remove timestamps outside the window
        window_start = current_time - window_seconds
        timestamps = [ts for ts in timestamps if ts >= window_start]
        
        # Update timestamps
        self.request_records[client_ip][endpoint] = timestamps
        
        # Check if rate limit is exceeded
        if len(timestamps) >= max_requests:
            return True
        
        # Add current timestamp
        timestamps.append(current_time)
        
        return False
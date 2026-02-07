"""
Request correlation middleware.

Adds X-Request-ID header to all requests for tracing logs across services.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid

from app.utils.logging import set_request_id


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Add request ID to all logs for a request.

    Usage in main.py:
        app.add_middleware(CorrelationMiddleware)
    """

    async def dispatch(self, request: Request, call_next):
        # Get or create request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        set_request_id(request_id)

        # Process request
        response = await call_next(request)

        # Add request ID to response
        response.headers['X-Request-ID'] = request_id
        return response

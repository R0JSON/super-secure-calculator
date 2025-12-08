import time
from collections import defaultdict

from starlette.middleware.base import (  # Corrected import
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, limit_per_minute: int = 60):
        super().__init__(app)
        self.limit_per_minute = limit_per_minute
        self.requests_by_ip: defaultdict[str, list[float]] = defaultdict(list)
        # No explicit cleanup interval needed if we filter on every request
        # For simplicity, cleanup can happen implicitly by filtering in dispatch

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean up old requests for this IP
        # Keep only requests within the last minute
        self.requests_by_ip[client_ip] = [
            t for t in self.requests_by_ip[client_ip] if t > current_time - 60
        ]

        if len(self.requests_by_ip[client_ip]) >= self.limit_per_minute:
            # Rate limit exceeded
            return JSONResponse(
                {"detail": "Too many requests."},
                status_code=429,
                headers={"Retry-After": "60"},
            )

        self.requests_by_ip[client_ip].append(current_time)
        response = await call_next(request)
        return response

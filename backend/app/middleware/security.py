"""Security middleware for request filtering and protection."""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.services.security_shield import security_shield


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware that applies security checks to all requests."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"

        # Check if IP is blocked
        if security_shield.is_ip_blocked(client_ip):
            return Response(
                content='{"error": "Access denied", "code": "IP_BLOCKED"}',
                status_code=403,
                media_type="application/json",
            )

        # Check rate limit
        rate_limit_key = f"ip:{client_ip}"
        if security_shield.check_rate_limit(rate_limit_key, tier="free"):
            remaining = security_shield.get_rate_limit_remaining(rate_limit_key, tier="free")
            return Response(
                content='{"error": "Rate limit exceeded", "code": "RATE_LIMITED"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Remaining": str(remaining),
                    "Retry-After": "60",
                },
            )

        # Add security headers
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        response.headers["X-Process-Time"] = str(round(process_time, 4))
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"

        return response

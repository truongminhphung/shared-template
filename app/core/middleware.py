import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders
import contextvars

# Context variable to store request_id across the request lifecycle
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates a unique Request ID for each request.

    This enables traceability across logs by:
    1. Generating a unique UUID for each request
    2. Storing it in request state for access in handlers/services
    3. Adding it to response headers for client-side debugging
    4. Setting it in a context variable for thread-safe access

    Usage in code:
        from app.core.middleware import request_id_var
        request_id = request_id_var.get()
    """

    async def dispatch(self, request: Request, call_next):
        # 1. Generate a unique ID (or use one from load balancer)
        request_id = str(uuid.uuid4())

        # 2. Store it in the request state so routers can use it
        request.state.request_id = request_id

        # 3. Set it in context variable for access in services/handlers
        token = request_id_var.set(request_id)

        try:
            # 4. Process the request
            response = await call_next(request)

            # 5. Return it in the header (helpful for frontend debugging)
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            # Clean up the context variable
            request_id_var.reset(token)

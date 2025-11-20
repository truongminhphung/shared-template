# The Global Exception Handler
from fastapi import Request, HTTPException, FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions import ResourceNotFound, DuplicateResource


async def resource_not_found_handler(request: Request, exc: ResourceNotFound):
    # standardize to HTTP 404 response
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource Not Found",
            "entity": exc.entity_name, # help frontend know WHAT was missing
            "message": exc.message
        }
    )


async def duplicate_resource_handler(request: Request, exc: DuplicateResource):
    # standardize to HTTP 409 Conflict response
    return JSONResponse(
        status_code=409,
        content={
            "error": "Duplicate Resource",
            "entity": exc.entity_name, # help frontend know WHAT was duplicate
            "message": exc.message
        }
    )


# Registry of exception handlers
EXCEPTION_HANDLERS = {
    ResourceNotFound: resource_not_found_handler,
    DuplicateResource: duplicate_resource_handler,
}


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers to the FastAPI app"""
    for exception_class, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, handler)
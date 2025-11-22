# The Global Exception Handler
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions import ResourceNotFound, DuplicateResource, ValidationError
import logging

logger = logging.getLogger(__name__)


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
    logger.error(f"Duplicate resource error: {exc.message}")
    return JSONResponse(
        status_code=409,
        content={
            "error": "Duplicate Resource",
            "entity": exc.entity_name, # help frontend know WHAT was duplicate
            "message": exc.message
        }
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    # standardize to HTTP 400 Bad Request response
    logger.warning(f"Validation error on field '{exc.field}': {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "field": exc.field,
            "message": exc.message
        }
    )


# Registry of exception handlers
EXCEPTION_HANDLERS = {
    ResourceNotFound: resource_not_found_handler,
    DuplicateResource: duplicate_resource_handler,
    ValidationError: validation_error_handler,
}


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers to the FastAPI app"""
    for exception_class, handler in EXCEPTION_HANDLERS.items():
        app.add_exception_handler(exception_class, handler)
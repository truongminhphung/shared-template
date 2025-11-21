from fastapi import FastAPI

from app.api.v1 import user, health
from app.core.config import config
from app.core.logging import setup_logging
from app.core.handlers import register_exception_handlers
from app.db.base import Base

PREFIX = "/api/v1"

setup_logging()

app = FastAPI(title=config.app_name)

# Register exception handlers
register_exception_handlers(app)

# Register routes
app.include_router(health.router, prefix=PREFIX)
app.include_router(user.router, prefix=PREFIX)
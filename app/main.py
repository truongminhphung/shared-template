from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1 import user, health
from app.core.config import config
from app.core.log_config import setup_logging
from app.core.handlers import register_exception_handlers
from app.db.migration import run_migrations

PREFIX = "/api/v1"

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    This function runs automatically when the application starts and stops:

    1. STARTUP (before yield):
       - Runs when the application is starting up
       - Executes database migrations to ensure schema is up-to-date
       - Only runs pending migrations (safe to run multiple times)
       - If migrations fail, the application won't start

    2. SHUTDOWN (after yield):
       - Runs when the application is shutting down
       - Use for cleanup tasks (closing connections, releasing resources, etc.)

    Flow:
        Application Start → Run migrations → Start accepting requests
        Application Stop → Run cleanup → Exit

    The 'yield' separates startup logic (before) from shutdown logic (after).
    """
    # Startup: Run migrations before accepting any requests
    run_migrations()
    print("Database migrations completed successfully.")

    yield  # Application runs here and accepts requests


app = FastAPI(title=config.app_name, lifespan=lifespan)

# Register exception handlers
register_exception_handlers(app)

# Register routes
app.include_router(health.router, prefix=PREFIX)
app.include_router(user.router, prefix=PREFIX)
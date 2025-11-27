"""Database migration utilities for running Alembic migrations programmatically."""

import logging
from alembic import command
from alembic.config import Config
from pathlib import Path

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """
    Run Alembic migrations programmatically on application startup.

    This function:
    1. Locates the alembic.ini file in the project root
    2. Configures Alembic to use it
    3. Runs all pending migrations (equivalent to 'alembic upgrade head')

    This ensures the database schema is always up-to-date without manual intervention.

    Raises:
        Exception: If migrations fail to run
    """
    try:
        # Get the path to alembic.ini (should be in project root)
        project_root = Path(__file__).parent.parent.parent
        alembic_ini_path = project_root / "alembic.ini"

        if not alembic_ini_path.exists():
            raise FileNotFoundError(
                f"alembic.ini not found at {alembic_ini_path}. "
                "Ensure Alembic is properly initialized."
            )

        logger.info("Running database migrations...")

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini_path))

        # Run migrations to the latest version
        command.upgrade(alembic_cfg, "head")

        logger.info("Database migrations completed successfully")

    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise

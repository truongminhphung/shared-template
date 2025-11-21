import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", tags=["health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for load balancers and orchestration platforms.
    
    Returns:
        - 200 OK: Service is healthy and database is connected
        - 500 Internal Server Error: Database connection failed
    
    Used by:
        - AWS ALB (Application Load Balancer)
        - Kubernetes liveness/readiness probes
        - Docker health checks
    """
    try:
        # Verify database connectivity with a simple query
        await db.execute(text("SELECT 1"))
        logger.info("Health check passed: database connection OK")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )


@router.get("/status", tags=["health"])
async def status_check(db: AsyncSession = Depends(get_db)):
    """
    Alias endpoint for /health. Some systems prefer /status instead of /health.
    
    Returns:
        - 200 OK: Service is healthy and database is connected
        - 500 Internal Server Error: Database connection failed
    """
    try:
        await db.execute(text("SELECT 1"))
        logger.info("Status check passed: database connection OK")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database connection failed"
        )

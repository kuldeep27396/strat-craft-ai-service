"""
Health check endpoints for monitoring and orchestration.

Provides /health, /health/ready, and /health/live endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(tags=["health"])


class HealthStatus:
    """Health check status collector."""

    def __init__(self):
        self.checks = {}

    def add_check(self, name: str, status: bool, message: str = ""):
        """Add a health check result."""
        self.checks[name] = {
            "status": "healthy" if status else "unhealthy",
            "message": message
        }

    def is_healthy(self) -> bool:
        """Check if all checks passed."""
        return all(c["status"] == "healthy" for c in self.checks.values())


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check."""
    status = HealthStatus()

    # Database check
    try:
        db.execute("SELECT 1")
        status.add_check("database", True)
    except Exception as e:
        status.add_check("database", False, str(e))

    # LLM provider check (basic - just checks config)
    try:
        from app.config import settings
        has_api_key = bool(getattr(settings, 'GROQ_API_KEY', None))
        status.add_check("llm_provider", has_api_key)
        if not has_api_key:
            status.add_check("llm_provider", False, "GROQ_API_KEY not configured")
    except Exception as e:
        status.add_check("llm_provider", False, str(e))

    return {
        "status": "healthy" if status.is_healthy() else "unhealthy",
        "checks": status.checks
    }


@router.get("/health/ready")
async def readiness_check():
    """Readiness check - can the service accept traffic?"""
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check():
    """Liveness check - is the service alive?"""
    return {"status": "alive"}

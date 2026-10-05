import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.db import get_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/healthz")
def liveness() -> dict[str, str]:
    """Liveness: the process is up. Never touches dependencies, so a database
    outage does not make Kubernetes restart healthy pods."""
    return {"status": "ok"}


@router.get("/readyz")
def readiness(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    """Readiness: the API can serve traffic, i.e. the database answers."""
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("Readiness check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database unavailable"
        ) from exc
    return {"status": "ready"}

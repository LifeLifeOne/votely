from fastapi import FastAPI

from app.api import health
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="Votely API", version="0.1.0")
    app.include_router(health.router)
    return app


app = create_app()

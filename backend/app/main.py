from fastapi import FastAPI

from app.api import auth, health, polls
from app.api.errors import register_error_handlers
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="Votely API", version="0.1.0")
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(polls.router)
    register_error_handlers(app)
    return app


app = create_app()

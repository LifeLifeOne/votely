import uuid
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.security import decode_access_token
from app.domain.users import UserService
from app.repositories.models import User
from app.repositories.users import SqlUserRepository

SESSION_COOKIE = "votely_session"

DbSession = Annotated[Session, Depends(get_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_user_service(session: DbSession) -> UserService:
    return UserService(SqlUserRepository(session))


Users = Annotated[UserService, Depends(get_user_service)]


def get_optional_user(
    users: Users,
    settings: AppSettings,
    votely_session: Annotated[str | None, Cookie()] = None,
) -> User | None:
    if votely_session is None:
        return None
    subject = decode_access_token(votely_session, settings.jwt_secret.get_secret_value())
    if subject is None:
        return None
    try:
        return users.get_user(uuid.UUID(subject))
    except ValueError:
        return None


def get_current_user(user: Annotated[User | None, Depends(get_optional_user)]) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
    return user


OptionalUser = Annotated[User | None, Depends(get_optional_user)]
CurrentUser = Annotated[User, Depends(get_current_user)]

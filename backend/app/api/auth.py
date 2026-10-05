from datetime import timedelta

from fastapi import APIRouter, Response, status

from app.api.deps import SESSION_COOKIE, AppSettings, CurrentUser, Users
from app.api.schemas import Credentials, UserCreate, UserRead
from app.core.security import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, users: Users) -> UserRead:
    return UserRead.model_validate(users.register(payload.email, payload.password))


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(payload: Credentials, users: Users, settings: AppSettings, response: Response) -> None:
    user = users.authenticate(payload.email, payload.password)
    ttl = timedelta(minutes=settings.access_token_ttl_minutes)
    token = create_access_token(str(user.id), settings.jwt_secret.get_secret_value(), ttl)
    # httpOnly: unreachable from JavaScript (XSS). SameSite=Lax: not sent on cross-site POST (CSRF).
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(ttl.total_seconds()),
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)


@router.get("/me")
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)

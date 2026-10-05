import uuid
from functools import lru_cache
from typing import Protocol

from app.core.security import hash_password, verify_password
from app.domain.errors import InvalidCredentialsError
from app.repositories.models import User


class UserRepository(Protocol):
    def add(self, user: User) -> User: ...
    def get(self, user_id: uuid.UUID) -> User | None: ...
    def get_by_email(self, email: str) -> User | None: ...


@lru_cache
def _dummy_hash() -> str:
    return hash_password("dummy-password-for-unknown-users")


def normalize_email(email: str) -> str:
    return email.strip().lower()


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def register(self, email: str, password: str) -> User:
        user = User(email=normalize_email(email), password_hash=hash_password(password))
        return self._repository.add(user)

    def authenticate(self, email: str, password: str) -> User:
        user = self._repository.get_by_email(normalize_email(email))
        if user is None:
            # Hash anyway so response time does not reveal whether the account exists.
            verify_password(password, _dummy_hash())
            raise InvalidCredentialsError()
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return user

    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self._repository.get(user_id)

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errors import EmailAlreadyRegisteredError
from app.repositories.models import User


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        self._session.add(user)
        try:
            self._session.commit()
        except IntegrityError as exc:
            # The unique constraint on email is the source of truth, even under concurrency.
            self._session.rollback()
            raise EmailAlreadyRegisteredError() from exc
        self._session.refresh(user)
        return user

    def get(self, user_id: uuid.UUID) -> User | None:
        return self._session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalar(select(User).where(User.email == email))

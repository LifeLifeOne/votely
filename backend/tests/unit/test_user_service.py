import pytest

from app.domain.errors import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.domain.users import UserService
from tests.unit.fakes import InMemoryUserRepository

PASSWORD = "correct horse battery"


@pytest.fixture
def service() -> UserService:
    return UserService(InMemoryUserRepository())


def test_register_normalizes_email_and_hashes_password(service):
    user = service.register("  Alice@Example.COM ", PASSWORD)

    assert user.email == "alice@example.com"
    assert user.password_hash != PASSWORD
    assert user.password_hash.startswith("$argon2id$")


def test_register_same_email_twice_is_rejected(service):
    service.register("alice@example.com", PASSWORD)

    with pytest.raises(EmailAlreadyRegisteredError):
        service.register("ALICE@example.com", PASSWORD)


def test_authenticate_with_valid_credentials(service):
    registered = service.register("alice@example.com", PASSWORD)

    assert service.authenticate("Alice@example.com", PASSWORD) is registered


def test_authenticate_with_wrong_password(service):
    service.register("alice@example.com", PASSWORD)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate("alice@example.com", "wrong password!!")


def test_authenticate_unknown_email(service):
    with pytest.raises(InvalidCredentialsError):
        service.authenticate("nobody@example.com", PASSWORD)

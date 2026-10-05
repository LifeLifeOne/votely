class DomainError(Exception):
    """Base class for business rule violations, mapped to HTTP errors by the API layer."""


class PollNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("poll not found")


class OptionNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("option does not belong to this poll")


class PollClosedError(DomainError):
    def __init__(self) -> None:
        super().__init__("poll is closed")


class InvalidClosingDateError(DomainError):
    def __init__(self) -> None:
        super().__init__("closing date must be in the future")


class EmailAlreadyRegisteredError(DomainError):
    def __init__(self) -> None:
        super().__init__("email already registered")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("invalid email or password")

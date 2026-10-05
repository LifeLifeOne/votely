from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.errors import (
    AlreadyVotedError,
    DomainError,
    EmailAlreadyRegisteredError,
    InvalidClosingDateError,
    InvalidCredentialsError,
    OptionNotFoundError,
    PollClosedError,
    PollNotFoundError,
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    PollNotFoundError: status.HTTP_404_NOT_FOUND,
    OptionNotFoundError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    InvalidClosingDateError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    PollClosedError: status.HTTP_409_CONFLICT,
    AlreadyVotedError: status.HTTP_409_CONFLICT,
    EmailAlreadyRegisteredError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
}


async def domain_error_handler(_: Request, exc: Exception) -> JSONResponse:
    status_code = STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)

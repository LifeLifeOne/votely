import uuid
from datetime import datetime
from typing import Annotated

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
)

Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]
OptionLabel = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    created_at: datetime


class PollCreate(BaseModel):
    question: Question
    options: list[OptionLabel] = Field(min_length=2, max_length=10)
    closes_at: AwareDatetime | None = None

    @field_validator("options")
    @classmethod
    def options_must_be_unique(cls, options: list[str]) -> list[str]:
        if len({option.casefold() for option in options}) != len(options):
            raise ValueError("options must be unique")
        return options


class OptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label: str


class PollRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_id: uuid.UUID | None
    question: str
    closes_at: datetime | None
    created_at: datetime
    is_closed: bool
    # Whether the current user already voted (always false for anonymous users).
    has_voted: bool
    options: list[OptionRead]


class VoteCreate(BaseModel):
    option_id: uuid.UUID


class OptionResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    option_id: uuid.UUID
    label: str
    votes: int
    percentage: float


class PollResultsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    poll_id: uuid.UUID
    total_votes: int
    options: list[OptionResultRead]

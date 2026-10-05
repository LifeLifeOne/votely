import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.schemas import PollCreate, PollRead, PollResultsRead, VoteCreate
from app.core.db import get_session
from app.domain.polls import PollService, is_closed, utc_now
from app.repositories.models import Poll
from app.repositories.polls import SqlPollRepository

router = APIRouter(prefix="/api/v1/polls", tags=["polls"])


def get_poll_service(session: Annotated[Session, Depends(get_session)]) -> PollService:
    return PollService(SqlPollRepository(session))


Service = Annotated[PollService, Depends(get_poll_service)]


def to_read(poll: Poll) -> PollRead:
    return PollRead.model_validate(
        {
            "id": poll.id,
            "question": poll.question,
            "closes_at": poll.closes_at,
            "created_at": poll.created_at,
            "is_closed": is_closed(poll, utc_now()),
            "options": poll.options,
        }
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_poll(payload: PollCreate, service: Service) -> PollRead:
    poll = service.create_poll(payload.question, payload.options, payload.closes_at)
    return to_read(poll)


@router.get("")
def list_polls(
    service: Service,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[PollRead]:
    return [to_read(poll) for poll in service.list_polls(limit=limit, offset=offset)]


@router.get("/{poll_id}")
def get_poll(poll_id: uuid.UUID, service: Service) -> PollRead:
    return to_read(service.get_poll(poll_id))


@router.post("/{poll_id}/votes", status_code=status.HTTP_204_NO_CONTENT)
def vote(poll_id: uuid.UUID, payload: VoteCreate, service: Service) -> None:
    service.vote(poll_id, payload.option_id)


@router.get("/{poll_id}/results")
def get_results(poll_id: uuid.UUID, service: Service) -> PollResultsRead:
    return PollResultsRead.model_validate(service.get_results(poll_id))

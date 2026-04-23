from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.job import JobRead


class ApplicationRead(BaseModel):
    id: UUID
    user_id: UUID
    job: JobRead
    status: str
    applied_via: str
    cover_letter: str | None
    notes: str | None
    follow_up_count: int
    interview_date: datetime | None
    offer_amount: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    job_id: UUID
    cover_letter: str | None = None
    notes: str | None = None


class ApplicationStatusUpdate(BaseModel):
    status: str


class ApplicationNotesUpdate(BaseModel):
    notes: str


class KanbanBoard(BaseModel):
    applied: list[ApplicationRead]
    viewed: list[ApplicationRead]
    interviewing: list[ApplicationRead]
    offer: list[ApplicationRead]
    hired: list[ApplicationRead]
    rejected: list[ApplicationRead]
    ghosted: list[ApplicationRead]

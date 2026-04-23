from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ResumeRead(BaseModel):
    id: UUID
    user_id: UUID
    file_url: str | None
    file_name: str | None
    parsed_json: dict[str, Any] | None
    career_dna: dict[str, Any] | None
    is_primary: bool
    version: int
    tailored_for_job_id: UUID | None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeParseResult(BaseModel):
    resume: ResumeRead
    skills: list[str]
    readiness_score: int
    career_dna: dict[str, Any]


class TailorRequest(BaseModel):
    job_id: UUID

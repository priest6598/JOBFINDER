from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobRead(BaseModel):
    id: UUID
    title: str
    company: str
    company_logo_url: str | None
    location: str | None
    job_type: str | None
    salary_min: int | None
    salary_max: int | None
    description: str | None
    requirements: str | None
    apply_url: str | None
    source: str | None
    posted_at: datetime | None
    ghost_score: int
    company_health_score: int
    is_fresh: bool
    tags: list[str] | None

    class Config:
        from_attributes = True


class JobMatchRead(BaseModel):
    id: UUID
    job: JobRead
    match_score: int
    matching_skills: list[str] | None
    missing_skills: list[str] | None
    match_reasons: list[str] | None
    concerns: list[str] | None
    is_dismissed: bool
    is_saved: bool
    created_at: datetime

    class Config:
        from_attributes = True

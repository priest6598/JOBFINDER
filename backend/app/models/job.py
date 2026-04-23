from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Job(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    external_id: Mapped[str | None] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False, index=True)
    company_logo_url: Mapped[str | None] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String)
    job_type: Mapped[str | None] = mapped_column(String)
    salary_min: Mapped[int | None] = mapped_column(BigInteger)
    salary_max: Mapped[int | None] = mapped_column(BigInteger)
    description: Mapped[str | None] = mapped_column(Text)
    requirements: Mapped[str | None] = mapped_column(Text)
    apply_url: Mapped[str | None] = mapped_column(String)
    source: Mapped[str | None] = mapped_column(String)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ghost_score: Mapped[int] = mapped_column(Integer, default=50)
    company_health_score: Mapped[int] = mapped_column(Integer, default=50)
    is_fresh: Mapped[bool] = mapped_column(Boolean, default=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class JobMatch(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "job_matches"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_job_match"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    matching_skills: Mapped[list[str] | None] = mapped_column(JSON)
    missing_skills: Mapped[list[str] | None] = mapped_column(JSON)
    match_reasons: Mapped[list[str] | None] = mapped_column(JSON)
    concerns: Mapped[list[str] | None] = mapped_column(JSON)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="job_matches")  # noqa: F821
    job: Mapped["Job"] = relationship()

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Application(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String, default="applied", index=True)
    applied_via: Mapped[str] = mapped_column(String, default="manual")
    tailored_resume_id: Mapped[UUID | None] = mapped_column(ForeignKey("resumes.id"))
    cover_letter: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0)
    last_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    interview_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    offer_amount: Mapped[int | None] = mapped_column(BigInteger)

    user: Mapped["User"] = relationship(back_populates="applications")  # noqa: F821
    job: Mapped["Job"] = relationship()  # noqa: F821

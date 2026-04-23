from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String)

    linkedin_url: Mapped[str | None] = mapped_column(String)
    github_url: Mapped[str | None] = mapped_column(String)
    portfolio_url: Mapped[str | None] = mapped_column(String)
    avatar_url: Mapped[str | None] = mapped_column(String)

    career_readiness_score: Mapped[int] = mapped_column(Integer, default=0)

    subscription_tier: Mapped[str] = mapped_column(String, default=SubscriptionTier.FREE.value)
    subscription_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    credits_balance: Mapped[int] = mapped_column(Integer, default=0)

    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)

    target_roles: Mapped[str | None] = mapped_column(String)
    preferred_locations: Mapped[str | None] = mapped_column(String)
    min_salary_lpa: Mapped[int | None] = mapped_column(Integer)

    resumes: Mapped[list["Resume"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    job_matches: Mapped[list["JobMatch"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    credit_entries: Mapped[list["CreditLedger"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )

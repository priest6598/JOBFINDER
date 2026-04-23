from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    phone: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserRead"


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None
    phone: str | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
    avatar_url: str | None
    career_readiness_score: int
    subscription_tier: str
    subscription_expires_at: datetime | None
    credits_balance: int
    onboarded: bool
    target_roles: str | None
    preferred_locations: str | None
    min_salary_lpa: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class OnboardingUpdate(BaseModel):
    target_roles: str | None = None
    preferred_locations: str | None = None
    min_salary_lpa: int | None = None


TokenResponse.model_rebuild()

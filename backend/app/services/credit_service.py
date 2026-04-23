"""Credit accounting + free-tier gating.

Feature costs (in credits). Aligned with the free/boost tier split:
- tailor_resume: 3
- cover_letter: 1
- voice_mock: 5
- company_prep_pack: 8
- salary_coach: 4
- linkedin_rewrite: 6
- super_apply: 3
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Application, CreditLedger, CreditTransactionType, SubscriptionTier, User
from app.models.interview import MockInterview
from app.models.resume import Resume
from app.schemas.credit import CreditPack

FEATURE_COSTS: dict[str, int] = {
    "tailor_resume": 3,
    "cover_letter": 1,
    "voice_mock": 5,
    "company_prep_pack": 8,
    "salary_coach": 4,
    "linkedin_rewrite": 6,
    "super_apply": 3,
}

CREDIT_PACKS: list[CreditPack] = [
    CreditPack(id="starter", credits=5, price_inr=49, label="Starter"),
    CreditPack(id="popular", credits=25, price_inr=199, label="Most popular", bonus_pct=20),
    CreditPack(id="power", credits=70, price_inr=499, label="Power pack", bonus_pct=40),
]


@dataclass
class FreeUsage:
    tailors_this_month: int
    cover_letters_this_month: int
    mocks_this_week: int


def _month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _week_start() -> datetime:
    now = datetime.now(timezone.utc)
    return (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


async def get_free_usage(session: AsyncSession, user_id: UUID) -> FreeUsage:
    month = _month_start()
    week = _week_start()

    tailors = await session.scalar(
        select(func.count())
        .select_from(Resume)
        .where(and_(Resume.user_id == user_id, Resume.tailored_for_job_id.is_not(None), Resume.created_at >= month))
    )
    covers = await session.scalar(
        select(func.count())
        .select_from(Application)
        .where(and_(Application.user_id == user_id, Application.cover_letter.is_not(None), Application.created_at >= month))
    )
    mocks = await session.scalar(
        select(func.count())
        .select_from(MockInterview)
        .where(and_(MockInterview.user_id == user_id, MockInterview.created_at >= week))
    )
    return FreeUsage(
        tailors_this_month=tailors or 0,
        cover_letters_this_month=covers or 0,
        mocks_this_week=mocks or 0,
    )


def is_pro_active(user: User) -> bool:
    if user.subscription_tier != SubscriptionTier.PRO.value:
        return False
    if user.subscription_expires_at is None:
        return True
    return user.subscription_expires_at > datetime.now(timezone.utc)


async def _record(
    session: AsyncSession,
    user: User,
    transaction_type: CreditTransactionType,
    amount: int,
    reason: str,
    reference_id: str | None = None,
) -> CreditLedger:
    user.credits_balance += amount
    entry = CreditLedger(
        user_id=user.id,
        transaction_type=transaction_type.value,
        amount=amount,
        reason=reason,
        reference_id=reference_id,
        balance_after=user.credits_balance,
    )
    session.add(entry)
    return entry


async def grant_starter_credits(session: AsyncSession, user: User) -> None:
    if settings.STARTER_CREDITS <= 0:
        return
    await _record(
        session, user, CreditTransactionType.GRANT, settings.STARTER_CREDITS, reason="welcome_bonus"
    )


async def add_purchased_credits(session: AsyncSession, user: User, credits: int, pack_id: str) -> CreditLedger:
    return await _record(
        session, user, CreditTransactionType.PURCHASE, credits, reason="pack_purchase", reference_id=pack_id
    )


async def spend_or_raise(
    session: AsyncSession, user: User, feature: str, allow_free: bool = True
) -> tuple[bool, int]:
    """Returns (used_free_quota, credits_charged). Raises 402 on insufficient credits."""
    if is_pro_active(user):
        return (False, 0)

    if allow_free:
        usage = await get_free_usage(session, user.id)
        if feature == "tailor_resume" and usage.tailors_this_month < settings.FREE_TAILORED_RESUMES_PER_MONTH:
            return (True, 0)
        if feature == "cover_letter" and usage.cover_letters_this_month < settings.FREE_COVER_LETTERS_PER_MONTH:
            return (True, 0)
        if feature == "text_mock" and usage.mocks_this_week < settings.FREE_MOCK_INTERVIEWS_PER_WEEK:
            return (True, 0)

    cost = FEATURE_COSTS.get(feature)
    if cost is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Unknown feature '{feature}'")

    if user.credits_balance < cost:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "insufficient_credits",
                "feature": feature,
                "required": cost,
                "balance": user.credits_balance,
                "packs": [p.model_dump() for p in CREDIT_PACKS],
            },
        )

    await _record(
        session, user, CreditTransactionType.SPEND, -cost, reason=f"spend:{feature}"
    )
    return (False, cost)

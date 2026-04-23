from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_session
from app.models import Job, JobMatch, User
from app.schemas.job import JobMatchRead, JobRead
from app.services import ai_service
from app.services.credit_service import is_pro_active

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
async def list_jobs(
    limit: int = Query(default=30, le=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user),
) -> list[JobRead]:
    rows = (await session.scalars(select(Job).order_by(desc(Job.posted_at)).limit(limit))).all()
    return [JobRead.model_validate(j) for j in rows]


@router.get("/matches", response_model=list[JobMatchRead])
async def list_matches(
    min_score: int = Query(default=0),
    include_dismissed: bool = Query(default=False),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[JobMatchRead]:
    stmt = (
        select(JobMatch)
        .options(selectinload(JobMatch.job))
        .where(JobMatch.user_id == user.id, JobMatch.match_score >= min_score)
        .order_by(desc(JobMatch.match_score))
    )
    if not include_dismissed:
        stmt = stmt.where(JobMatch.is_dismissed.is_(False))

    if not is_pro_active(user):
        stmt = stmt.limit(settings.FREE_DAILY_MATCH_LIMIT)

    rows = (await session.scalars(stmt)).all()
    return [JobMatchRead.model_validate(m) for m in rows]


@router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_session), _: User = Depends(get_current_user)) -> JobRead:
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return JobRead.model_validate(job)


@router.post("/{job_id}/save", response_model=JobMatchRead)
async def save_job(
    job_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JobMatchRead:
    match = await _get_or_create_match(session, user.id, job_id)
    match.is_saved = True
    match.is_dismissed = False
    await session.commit()
    await session.refresh(match, ["job"])
    return JobMatchRead.model_validate(match)


@router.post("/{job_id}/dismiss", response_model=JobMatchRead)
async def dismiss_job(
    job_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JobMatchRead:
    match = await _get_or_create_match(session, user.id, job_id)
    match.is_dismissed = True
    await session.commit()
    await session.refresh(match, ["job"])
    return JobMatchRead.model_validate(match)


async def _get_or_create_match(session: AsyncSession, user_id: UUID, job_id: UUID) -> JobMatch:
    match = await session.scalar(
        select(JobMatch).options(selectinload(JobMatch.job)).where(
            JobMatch.user_id == user_id, JobMatch.job_id == job_id
        )
    )
    if match:
        return match
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    match = JobMatch(user_id=user_id, job_id=job_id, match_score=0)
    session.add(match)
    await session.flush()
    await session.refresh(match, ["job"])
    return match

"""Job matching + ghost-score heuristics."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, JobMatch, Resume
from app.services import ai_service


def score_ghost(job: Job) -> int:
    """Heuristic legitimacy 0-100. Higher = more legitimate."""
    score = 70
    if job.posted_at:
        age_days = (datetime.now(timezone.utc) - job.posted_at).days
        if age_days > 45:
            score -= 25
        elif age_days > 21:
            score -= 10
    if job.apply_url and "linkedin.com" in (job.apply_url or ""):
        score -= 5
    if job.salary_min and job.salary_max:
        score += 10
    if job.description and len(job.description) > 400:
        score += 5
    return max(0, min(100, score))


async def create_match_for_user(
    session: AsyncSession, user_id: UUID, job: Job, resume: Resume
) -> JobMatch:
    existing = await session.scalar(
        select(JobMatch).where(JobMatch.user_id == user_id, JobMatch.job_id == job.id)
    )
    if existing:
        return existing

    result = ai_service.match_job_to_resume(
        resume.parsed_json or {},
        {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "requirements": job.requirements,
            "tags": job.tags,
        },
    )

    match = JobMatch(
        user_id=user_id,
        job_id=job.id,
        match_score=int(result.get("score", 0)),
        matching_skills=result.get("matching_skills") or [],
        missing_skills=result.get("missing_skills") or [],
        match_reasons=result.get("match_reasons") or [],
        concerns=result.get("concerns") or [],
    )
    session.add(match)
    return match


async def match_all_jobs_for_resume(
    session: AsyncSession, user_id: UUID, resume: Resume, limit: int = 20
) -> list[JobMatch]:
    jobs = (await session.scalars(select(Job).limit(limit))).all()
    matches: list[JobMatch] = []
    for job in jobs:
        match = await create_match_for_user(session, user_id, job, resume)
        matches.append(match)
    return matches

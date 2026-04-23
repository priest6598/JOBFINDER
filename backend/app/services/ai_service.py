"""Claude-backed AI service. Every function returns structured data."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import anthropic

from app.core.config import settings

log = logging.getLogger(__name__)

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def _extract_json(text: str) -> dict[str, Any]:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fence.group(1) if fence else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output: {text[:200]}")
    return json.loads(candidate[start : end + 1])


def _call_claude_json(system: str, user: str, max_tokens: int = 2048) -> dict[str, Any]:
    client = _get_client()
    resp = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return _extract_json(text)


def _call_claude_text(system: str, user: str, max_tokens: int = 1024) -> str:
    client = _get_client()
    resp = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


PARSE_SYSTEM = """You are a resume parser that extracts clean structured data.
Always return a single JSON object with keys: skills, experience, education, projects, career_dna, readiness_score.

- skills: array of {name, proficiency (beginner|intermediate|expert), years_experience (float)}
- experience: array of {company, title, location, start, end, bullets (array of strings), months}
- education: array of {institution, degree, field, year}
- projects: array of {name, description, tech_stack (array)}
- career_dna: {top_strengths (array of 3-5 strings), keywords (array of 10-15 terms recruiters search),
   seniority_level (intern|junior|mid|senior|staff|principal), domains (array), persona (one sentence)}
- readiness_score: integer 0-100 (calibration: 0-40 rough, 40-70 decent, 70-90 strong, 90+ exceptional)

No prose, no markdown, only JSON."""


def parse_resume(raw_text: str) -> dict[str, Any]:
    return _call_claude_json(PARSE_SYSTEM, f"RESUME TEXT:\n\n{raw_text}", max_tokens=3000)


MATCH_SYSTEM = """You evaluate how well a candidate matches a job.
Return JSON with: score (0-100 integer), matching_skills (array), missing_skills (array),
match_reasons (array of short strings, max 4), concerns (array, max 3).
Be honest — penalize missing must-haves. Reward domain overlap. No prose, only JSON."""


def match_job_to_resume(resume_json: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    user = (
        "CANDIDATE:\n"
        f"{json.dumps(resume_json, default=str)[:6000]}\n\n"
        "JOB:\n"
        f"Title: {job.get('title')}\n"
        f"Company: {job.get('company')}\n"
        f"Location: {job.get('location')}\n"
        f"Description: {job.get('description') or ''}\n"
        f"Requirements: {job.get('requirements') or ''}\n"
        f"Tags: {job.get('tags') or []}\n"
    )
    return _call_claude_json(MATCH_SYSTEM, user, max_tokens=800)


TAILOR_SYSTEM = """You rewrite resume content to match a specific job — WITHOUT fabricating.
Only reframe existing experience using stronger action verbs, measurable outcomes, and keywords from the JD.
Return JSON matching the input structure: {summary, experience (with rewritten bullets), skills (reordered by relevance)}.
Never invent new roles, companies, or metrics. No prose, only JSON."""


def tailor_resume(resume_json: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    user = (
        f"ORIGINAL RESUME:\n{json.dumps(resume_json, default=str)[:6000]}\n\n"
        f"TARGET JOB: {job.get('title')} at {job.get('company')}\n"
        f"Description: {job.get('description') or ''}\n"
        f"Requirements: {job.get('requirements') or ''}\n"
    )
    return _call_claude_json(TAILOR_SYSTEM, user, max_tokens=3000)


COVER_SYSTEM = """You write cover letters that sound like the candidate, not a template.
Rules:
- Max 280 words
- Never open with "I am writing to apply" or "I hope this finds you well"
- Reference something specific about the company's product or recent direction
- Lead with the strongest relevant credential
- End with a specific question or next step
Return plain text, no JSON, no markdown, no signature."""


def generate_cover_letter(resume_json: dict[str, Any], job: dict[str, Any]) -> str:
    user = (
        f"CANDIDATE: {json.dumps(resume_json, default=str)[:4000]}\n\n"
        f"JOB: {job.get('title')} at {job.get('company')}\n"
        f"{job.get('description') or ''}"
    )
    return _call_claude_text(COVER_SYSTEM, user, max_tokens=800)


OUTREACH_SYSTEM = """You write recruiter outreach messages that aren't generic.
Rules per message_type:
- connection_request: <= 300 chars, no greeting fluff, one concrete reason this person is worth talking to
- linkedin_message: <= 1000 chars, conversational, one clear ask
- email: <= 150 words, include subject line as first line "Subject: ..."
Never "I hope this message finds you well." Never "passionate about." Return plain text."""


def generate_recruiter_outreach(
    user_profile: dict[str, Any],
    recipient: dict[str, Any],
    job: dict[str, Any] | None,
    message_type: str,
) -> str:
    user = (
        f"MESSAGE TYPE: {message_type}\n"
        f"CANDIDATE: {json.dumps(user_profile, default=str)[:2000]}\n"
        f"RECIPIENT: {json.dumps(recipient, default=str)[:500]}\n"
        f"JOB CONTEXT: {json.dumps(job or {}, default=str)[:1000]}\n"
    )
    return _call_claude_text(OUTREACH_SYSTEM, user, max_tokens=500)


INTERVIEW_PREP_SYSTEM = """Generate an interview prep deck.
Return JSON: {
  company_snapshot: string (2-3 sentences),
  why_role_exists: string,
  likely_questions: [{question, type (behavioral|technical|system_design|role_specific), tips, sample_answer}],
  star_stories: [{situation, task, action, result, applicable_for (array of question types)}],
  questions_to_ask: [string],
  key_things_to_highlight: [string]
}
At least 8 likely_questions, 4 star_stories, 8 questions_to_ask. No prose, only JSON."""


def generate_interview_prep_deck(
    company: str, role: str, jd: str, user_resume: dict[str, Any], intel: list[dict[str, Any]]
) -> dict[str, Any]:
    user = (
        f"COMPANY: {company}\nROLE: {role}\n\nJD:\n{jd[:3000]}\n\n"
        f"CANDIDATE: {json.dumps(user_resume, default=str)[:4000]}\n\n"
        f"CROWDSOURCED INTEL: {json.dumps(intel, default=str)[:2000]}"
    )
    return _call_claude_json(INTERVIEW_PREP_SYSTEM, user, max_tokens=4000)


MOCK_SCORE_SYSTEM = """Score a mock interview answer.
Return JSON: {score: 1-5 integer, feedback: string (2-3 sentences),
what_was_good: array of strings, improve: array of strings, follow_up_question: string}.
Be specific and actionable. No prose, only JSON."""


def score_interview_answer(question: str, answer: str, role: str) -> dict[str, Any]:
    user = f"ROLE: {role}\nQUESTION: {question}\n\nANSWER:\n{answer}"
    return _call_claude_json(MOCK_SCORE_SYSTEM, user, max_tokens=600)

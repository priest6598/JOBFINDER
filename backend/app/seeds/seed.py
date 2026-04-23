"""Seed the DB with demo jobs + interview intel. Idempotent (skips if jobs already exist)."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.session import SessionLocal, init_db
from app.models import Job
from app.models.interview import InterviewIntel
from app.services.job_matching import score_ghost


def _now_minus(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


JOBS = [
    {
        "title": "Senior Data Engineer",
        "company": "Razorpay",
        "company_logo_url": "https://logo.clearbit.com/razorpay.com",
        "location": "Bangalore",
        "job_type": "full-time",
        "salary_min": 3000000,
        "salary_max": 4500000,
        "description": "Own the data platform at Razorpay. Build streaming pipelines over Kafka, batch over Spark, and serve 500M+ events/day to downstream ML and analytics.",
        "requirements": "5+ years backend/data. Deep Python. Spark, Kafka, Airflow in production. Strong SQL. Bonus: Iceberg, dbt.",
        "apply_url": "https://razorpay.com/jobs/senior-data-engineer",
        "source": "company_page",
        "posted_at": _now_minus(1),
        "tags": ["Python", "Spark", "Kafka", "Airflow", "SQL"],
        "company_health_score": 82,
    },
    {
        "title": "Staff Data Engineer",
        "company": "PhonePe",
        "company_logo_url": "https://logo.clearbit.com/phonepe.com",
        "location": "Bangalore / Remote",
        "job_type": "full-time",
        "salary_min": 4000000,
        "salary_max": 6000000,
        "description": "Lead data architecture for payment rails. Scale beyond 2B events/day. Design the lakehouse on Iceberg.",
        "requirements": "8+ years. Data modeling at scale. Spark + Iceberg + dbt + Scala or Python. Led teams.",
        "apply_url": "https://phonepe.com/careers",
        "source": "company_page",
        "posted_at": _now_minus(2),
        "tags": ["Spark", "Iceberg", "Scala", "dbt", "Python"],
        "company_health_score": 79,
    },
    {
        "title": "Full-Stack Engineer (React + Node)",
        "company": "CRED",
        "company_logo_url": "https://logo.clearbit.com/cred.club",
        "location": "Bangalore",
        "job_type": "full-time",
        "salary_min": 2500000,
        "salary_max": 4000000,
        "description": "Ship premium consumer experiences. React, Node, TypeScript end-to-end. Obsess over frame rate and polish.",
        "requirements": "3+ years. React, TypeScript, Node. Eye for design. Shipped consumer products at scale.",
        "apply_url": "https://cred.club/careers",
        "source": "company_page",
        "posted_at": _now_minus(0),
        "tags": ["React", "TypeScript", "Node.js", "GraphQL"],
        "company_health_score": 81,
    },
    {
        "title": "Backend Engineer — Payments",
        "company": "Zerodha",
        "company_logo_url": "https://logo.clearbit.com/zerodha.com",
        "location": "Bangalore",
        "job_type": "full-time",
        "salary_min": 2000000,
        "salary_max": 3500000,
        "description": "Core backend for Kite. Go services, Postgres, Kafka. Low-latency trading flows.",
        "requirements": "3+ years Go or Python. Postgres at scale. Strong systems fundamentals.",
        "apply_url": "https://zerodha.com/careers",
        "source": "company_page",
        "posted_at": _now_minus(5),
        "tags": ["Go", "Postgres", "Kafka", "Redis"],
        "company_health_score": 90,
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Flipkart",
        "company_logo_url": "https://logo.clearbit.com/flipkart.com",
        "location": "Bangalore",
        "job_type": "full-time",
        "salary_min": 2800000,
        "salary_max": 4200000,
        "description": "Ranking + recommendation systems at Flipkart scale. Own production ML pipelines.",
        "requirements": "4+ years ML in production. Python, PyTorch or TF. Feature stores. Online serving.",
        "apply_url": "https://flipkartcareers.com",
        "source": "company_page",
        "posted_at": _now_minus(3),
        "tags": ["Python", "PyTorch", "MLOps", "Ranking"],
        "company_health_score": 74,
    },
    {
        "title": "Frontend Engineer — Platform",
        "company": "Postman",
        "company_logo_url": "https://logo.clearbit.com/postman.com",
        "location": "Bangalore / Remote",
        "job_type": "full-time",
        "salary_min": 2200000,
        "salary_max": 3800000,
        "description": "Build the editor and sidebar used by millions of API developers daily. React, Monaco editor, performance-critical UX.",
        "requirements": "3+ years React. Deep TypeScript. Performance profiling. Attention to pixel details.",
        "apply_url": "https://postman.com/company/careers",
        "source": "company_page",
        "posted_at": _now_minus(0),
        "tags": ["React", "TypeScript", "Monaco", "Performance"],
        "company_health_score": 83,
    },
    {
        "title": "DevOps / SRE Engineer",
        "company": "Meesho",
        "company_logo_url": "https://logo.clearbit.com/meesho.com",
        "location": "Bangalore",
        "job_type": "full-time",
        "salary_min": 2400000,
        "salary_max": 3600000,
        "description": "Own reliability of Meesho's infrastructure. Kubernetes across multi-region, observability, incident response.",
        "requirements": "4+ years DevOps/SRE. Kubernetes, Terraform, Prometheus/Grafana. On-call experience.",
        "apply_url": "https://meesho.io/careers",
        "source": "company_page",
        "posted_at": _now_minus(4),
        "tags": ["Kubernetes", "Terraform", "AWS", "Prometheus"],
        "company_health_score": 68,
    },
    {
        "title": "Senior Product Designer",
        "company": "Swiggy",
        "company_logo_url": "https://logo.clearbit.com/swiggy.com",
        "location": "Bangalore",
        "job_type": "full-time",
        "salary_min": 2500000,
        "salary_max": 4000000,
        "description": "Design the next generation of the Swiggy restaurant partner experience. End-to-end from research to polished specs.",
        "requirements": "5+ years product design. Strong portfolio. Figma expert. Shipped consumer products.",
        "apply_url": "https://careers.swiggy.com",
        "source": "company_page",
        "posted_at": _now_minus(6),
        "tags": ["Figma", "User Research", "Design Systems", "Mobile"],
        "company_health_score": 76,
    },
    {
        "title": "iOS Engineer",
        "company": "Zomato",
        "company_logo_url": "https://logo.clearbit.com/zomato.com",
        "location": "Gurgaon / Remote",
        "job_type": "full-time",
        "salary_min": 2000000,
        "salary_max": 3500000,
        "description": "Build the Zomato iOS app used by 100M+ diners. Swift, SwiftUI, rigorous performance work.",
        "requirements": "3+ years iOS. Swift expert. SwiftUI production experience. Deep understanding of app lifecycle.",
        "apply_url": "https://zomato.com/careers",
        "source": "company_page",
        "posted_at": _now_minus(1),
        "tags": ["Swift", "SwiftUI", "iOS", "Combine"],
        "company_health_score": 72,
    },
    {
        "title": "Senior AI Engineer",
        "company": "Sarvam AI",
        "company_logo_url": "https://logo.clearbit.com/sarvam.ai",
        "location": "Bangalore",
        "job_type": "full-time",
        "salary_min": 3500000,
        "salary_max": 5500000,
        "description": "Build foundational Indic language models. Train, evaluate, deploy at scale. Work directly on model architecture.",
        "requirements": "3+ years deep learning. PyTorch. Transformer internals. Published work or strong open-source contributions.",
        "apply_url": "https://sarvam.ai/careers",
        "source": "company_page",
        "posted_at": _now_minus(0),
        "tags": ["PyTorch", "Transformers", "CUDA", "LLMs"],
        "company_health_score": 85,
    },
]

INTEL = [
    {
        "company": "Razorpay",
        "role_level": "senior",
        "interview_type": "technical",
        "questions": [
            {"question": "Design a rate limiter for payment APIs", "frequency": "high", "tips": "Lead with clarifying questions, then token bucket vs sliding window"},
            {"question": "How would you model refunds in Postgres?", "frequency": "high", "tips": "Discuss idempotency keys, partial refunds, audit trail"},
            {"question": "Walk through debugging a prod pipeline lag", "frequency": "medium", "tips": "Show a structured approach — metrics first"},
        ],
        "process_description": "3 rounds: DSA + system design + culture fit. Usually wrapped in 2 weeks.",
        "difficulty": 4,
    },
    {
        "company": "CRED",
        "role_level": "mid",
        "interview_type": "technical",
        "questions": [
            {"question": "Build an infinite scroll list with pixel-perfect animations", "frequency": "high", "tips": "Virtualization, memo, animation frame budgeting"},
            {"question": "How would you design a reward graph?", "frequency": "medium", "tips": "Graph schema + traversal cost trade-offs"},
        ],
        "process_description": "Take-home → 2 technical rounds → design + values round. 3-4 weeks end to end.",
        "difficulty": 4,
    },
]


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        existing = await session.scalar(select(Job).limit(1))
        if existing:
            print("Seed skipped — jobs already present.")
            return

        job_objects: list[Job] = []
        for data in JOBS:
            job = Job(**data, is_fresh=True)
            job.ghost_score = score_ghost(job)
            session.add(job)
            job_objects.append(job)

        for data in INTEL:
            session.add(InterviewIntel(**data, verified=True))

        await session.commit()
        print(f"Seeded {len(JOBS)} jobs and {len(INTEL)} intel entries.")


if __name__ == "__main__":
    asyncio.run(main())

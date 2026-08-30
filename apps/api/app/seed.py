"""
Seeds realistic demo data so VIRA can be explored end-to-end without manual
setup: two companies with published jobs, a candidate with a parsed-looking
skill set, and an assessment. Run with: `python -m app.seed`
"""
import asyncio
import json

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models.assessments import Assessment, Question
from app.models.jobs import Job, JobSkill
from app.models.skills import CandidateSkill, Skill
from app.models.user import CandidateProfile, Company, RecruiterProfile, User

DEMO_SKILLS = [
    "Python", "SQL", "Machine Learning", "React", "Next.js", "FastAPI",
    "Power BI", "Data Analysis", "Communication", "Project Management",
    "JavaScript", "Docker",
]


async def get_or_create_skill(db, name: str) -> Skill:
    result = await db.execute(select(Skill).where(Skill.name == name))
    skill = result.scalar_one_or_none()
    if not skill:
        skill = Skill(name=name, category="general")
        db.add(skill)
        await db.flush()
    return skill


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == "priya.candidate@viradmo.dev"))
        if existing.scalar_one_or_none():
            print("Demo data already seeded. Skipping.")
            return

        for name in DEMO_SKILLS:
            await get_or_create_skill(db, name)
        await db.commit()

        # --- Demo candidate ---
        candidate_user = User(
            email="priya.candidate@viradmo.dev",
            password_hash=hash_password("DemoPass123!"),
            full_name="Priya Ramanathan",
            role="candidate",
        )
        db.add(candidate_user)
        await db.flush()

        candidate_profile = CandidateProfile(
            user_id=candidate_user.id,
            headline="Aspiring Backend Engineer | Python & ML",
            location="Coimbatore, India",
            profile_completion=70,
        )
        db.add(candidate_profile)
        await db.flush()

        for skill_name, proficiency in [
            ("Python", 0.8), ("SQL", 0.75), ("Machine Learning", 0.6),
            ("JavaScript", 0.5), ("Communication", 0.7),
        ]:
            skill = await get_or_create_skill(db, skill_name)
            db.add(CandidateSkill(candidate_id=candidate_profile.id, skill_id=skill.id, source="resume", proficiency=proficiency))

        # --- Demo company + recruiter ---
        company = Company(name="Northwind Analytics", industry="Data & AI Services", verified_status="verified")
        db.add(company)
        await db.flush()

        recruiter_user = User(
            email="arjun.recruiter@northwindanalytics.dev",
            password_hash=hash_password("DemoPass123!"),
            full_name="Arjun Mehta",
            role="recruiter",
        )
        db.add(recruiter_user)
        await db.flush()

        db.add(RecruiterProfile(user_id=recruiter_user.id, company_id=company.id, title="Talent Acquisition Lead"))

        # --- Demo jobs ---
        job1 = Job(
            company_id=company.id,
            title="Junior Data Analyst",
            description="Support the analytics team by turning raw data into clear, actionable reports for stakeholders.",
            responsibilities="Build dashboards, write SQL queries, present findings to non-technical teams.",
            location="Coimbatore, India (Hybrid)",
            employment_type="Full-time",
            status="published",
        )
        db.add(job1)
        await db.flush()
        for skill_name, req_type in [("SQL", "must_have"), ("Data Analysis", "must_have"), ("Power BI", "preferred"), ("Communication", "preferred")]:
            skill = await get_or_create_skill(db, skill_name)
            db.add(JobSkill(job_id=job1.id, skill_id=skill.id, requirement_type=req_type))

        job2 = Job(
            company_id=company.id,
            title="Software Developer (Backend)",
            description="Build and maintain backend services powering our analytics platform.",
            responsibilities="Design APIs, write clean Python code, collaborate with the ML team on model integration.",
            location="Remote",
            employment_type="Full-time",
            status="published",
        )
        db.add(job2)
        await db.flush()
        for skill_name, req_type in [("Python", "must_have"), ("SQL", "must_have"), ("FastAPI", "preferred"), ("Docker", "preferred")]:
            skill = await get_or_create_skill(db, skill_name)
            db.add(JobSkill(job_id=job2.id, skill_id=skill.id, requirement_type=req_type))

        # --- Demo assessment for job1 ---
        assessment = Assessment(job_id=job1.id, round_type="aptitude", title="Aptitude Round", duration_minutes=20)
        db.add(assessment)
        await db.flush()
        db.add(
            Question(
                assessment_id=assessment.id,
                question_type="multiple_choice",
                prompt="Which SQL clause filters aggregated results?",
                options_json=json.dumps(["WHERE", "HAVING", "ORDER BY", "LIMIT"]),
                correct_option="HAVING",
            )
        )

        await db.commit()

        print("Seed complete.")
        print("Candidate login -> priya.candidate@viradmo.dev / DemoPass123!")
        print("Recruiter login -> arjun.recruiter@northwindanalytics.dev / DemoPass123!")


if __name__ == "__main__":
    asyncio.run(seed())

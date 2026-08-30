"""
Seeds realistic demo data so VIRA can be explored end-to-end without manual
setup. Includes multiple companies and job opportunities.
Run with: python -m app.seed
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
"Python",
"SQL",
"Machine Learning",
"React",
"Next.js",
"FastAPI",
"Power BI",
"Data Analysis",
"Communication",
"Project Management",
"JavaScript",
"Docker",
"Java",
"HTML",
"CSS",
"Node.js",
"TypeScript",
"Git",
"AWS",
"Azure",
"Figma",
"UI/UX Design",
"Selenium",
"Testing",
"Linux",
"Excel",
"Data Visualization",
"Digital Marketing",
"SEO",
"HR Management",
"Sales",
"Business Analysis",
]

COMPANIES = [
{
"name": "Northwind Analytics",
"industry": "Data & AI Services",
},
{
"name": "TechNova Solutions",
"industry": "Software Development",
},
{
"name": "PixelCraft Digital",
"industry": "Digital Design & Marketing",
},
{
"name": "CloudSphere Technologies",
"industry": "Cloud Computing",
},
{
"name": "InsightWorks",
"industry": "Business Intelligence",
},
{
"name": "InnovateLabs",
"industry": "Technology & Innovation",
},
]

JOBS = [
{
"company": "Northwind Analytics",
"title": "Junior Data Analyst",
"description": (
"Support the analytics team by turning raw data into clear, "
"actionable reports for stakeholders."
),
"responsibilities": (
"Build dashboards, write SQL queries, analyze datasets, "
"and present findings to business teams."
),
"location": "Coimbatore, India (Hybrid)",
"employment_type": "Full-time",
"skills": [
("SQL", "must_have"),
("Data Analysis", "must_have"),
("Power BI", "preferred"),
("Communication", "preferred"),
],
},
{
"company": "Northwind Analytics",
"title": "Data Scientist Intern",
"description": (
"Work with the data science team to build predictive models "
"and analyze business datasets."
),
"responsibilities": (
"Clean data, train basic ML models, prepare reports, "
"and support experimentation."
),
"location": "Chennai, India (Hybrid)",
"employment_type": "Internship",
"skills": [
("Python", "must_have"),
("Machine Learning", "preferred"),
("SQL", "preferred"),
("Data Analysis", "must_have"),
],
},
{
"company": "Northwind Analytics",
"title": "Power BI Developer",
"description": (
"Create interactive dashboards and business intelligence "
"solutions for enterprise clients."
),
"responsibilities": (
"Develop Power BI reports, transform datasets, and work "
"with stakeholders to understand reporting requirements."
),
"location": "Bangalore, India (Hybrid)",
"employment_type": "Full-time",
"skills": [
("Power BI", "must_have"),
("SQL", "must_have"),
("Data Visualization", "preferred"),
("Excel", "preferred"),
],
},
{
"company": "TechNova Solutions",
"title": "Software Developer (Backend)",
"description": (
"Build and maintain backend services powering modern "
"web applications."
),
"responsibilities": (
"Design APIs, write clean Python code, manage databases, "
"and collaborate with frontend teams."
),
"location": "Remote",
"employment_type": "Full-time",
"skills": [
("Python", "must_have"),
("SQL", "must_have"),
("FastAPI", "preferred"),
("Docker", "preferred"),
],
},
{
"company": "TechNova Solutions",
"title": "Frontend Developer",
"description": (
"Build responsive and modern user interfaces for web applications."
),
"responsibilities": (
"Develop UI components, integrate APIs, optimize performance, "
"and collaborate with designers."
),
"location": "Chennai, India",
"employment_type": "Full-time",
"skills": [
("JavaScript", "must_have"),
("React", "must_have"),
("HTML", "must_have"),
("CSS", "must_have"),
("Next.js", "preferred"),
],
},
{
"company": "TechNova Solutions",
"title": "Full Stack Developer",
"description": (
"Develop complete web applications across frontend and backend."
),
"responsibilities": (
"Build APIs, develop UI components, work with databases, "
"and deploy applications."
),
"location": "Bangalore, India",
"employment_type": "Full-time",
"skills": [
("JavaScript", "must_have"),
("React", "must_have"),
("Node.js", "preferred"),
("SQL", "must_have"),
("Git", "preferred"),
],
},
{
"company": "TechNova Solutions",
"title": "Java Developer",
"description": (
"Develop reliable enterprise applications using Java technologies."
),
"responsibilities": (
"Write clean Java code, build backend services, "
"and collaborate with development teams."
),
"location": "Hyderabad, India",
"employment_type": "Full-time",
"skills": [
("Java", "must_have"),
("SQL", "preferred"),
("Git", "preferred"),
],
},
{
"company": "PixelCraft Digital",
"title": "UI/UX Designer",
"description": (
"Design intuitive and visually appealing digital experiences."
),
"responsibilities": (
"Create wireframes, prototypes, user flows, and collaborate "
"with developers and product teams."
),
"location": "Remote",
"employment_type": "Full-time",
"skills": [
("Figma", "must_have"),
("UI/UX Design", "must_have"),
("Communication", "preferred"),
],
},
{
"company": "PixelCraft Digital",
"title": "Digital Marketing Executive",
"description": (
"Plan and execute digital marketing campaigns across "
"multiple online channels."
),
"responsibilities": (
"Manage campaigns, analyze performance, improve SEO, "
"and prepare marketing reports."
),
"location": "Coimbatore, India",
"employment_type": "Full-time",
"skills": [
("Digital Marketing", "must_have"),
("SEO", "preferred"),
("Communication", "must_have"),
],
},
{
"company": "CloudSphere Technologies",
"title": "DevOps Engineer",
"description": (
"Help automate deployments and maintain reliable cloud infrastructure."
),
"responsibilities": (
"Manage CI/CD pipelines, containerized applications, "
"cloud services, and monitoring tools."
),
"location": "Remote",
"employment_type": "Full-time",
"skills": [
("Docker", "must_have"),
("Linux", "must_have"),
("AWS", "preferred"),
("Git", "preferred"),
],
},
{
"company": "CloudSphere Technologies",
"title": "Cloud Support Engineer",
"description": (
"Provide technical support for cloud-based applications and services."
),
"responsibilities": (
"Troubleshoot infrastructure issues, monitor systems, "
"and assist customers with technical problems."
),
"location": "Bangalore, India",
"employment_type": "Full-time",
"skills": [
("Linux", "must_have"),
("AWS", "preferred"),
("Azure", "preferred"),
("Communication", "must_have"),
],
},
{
"company": "InsightWorks",
"title": "Business Analyst",
"description": (
"Analyze business requirements and help teams make "
"data-driven decisions."
),
"responsibilities": (
"Gather requirements, document processes, analyze data, "
"and communicate insights to stakeholders."
),
"location": "Chennai, India (Hybrid)",
"employment_type": "Full-time",
"skills": [
("Business Analysis", "must_have"),
("Communication", "must_have"),
("Excel", "preferred"),
("SQL", "preferred"),
],
},
{
"company": "InsightWorks",
"title": "QA Engineer",
"description": (
"Ensure software quality through manual and automated testing."
),
"responsibilities": (
"Create test cases, identify bugs, perform regression testing, "
"and collaborate with developers."
),
"location": "Coimbatore, India",
"employment_type": "Full-time",
"skills": [
("Testing", "must_have"),
("Selenium", "preferred"),
("JavaScript", "preferred"),
],
},
{
"company": "InsightWorks",
"title": "Machine Learning Engineer",
"description": (
"Build and deploy machine learning solutions for real-world problems."
),
"responsibilities": (
"Develop ML pipelines, train models, evaluate performance, "
"and integrate models into applications."
),
"location": "Remote",
"employment_type": "Full-time",
"skills": [
("Python", "must_have"),
("Machine Learning", "must_have"),
("SQL", "preferred"),
("Docker", "preferred"),
],
},
{
"company": "InnovateLabs",
"title": "Python Developer",
"description": (
"Develop scalable applications and automation solutions using Python."
),
"responsibilities": (
"Write clean code, build APIs, work with databases, "
"and maintain existing services."
),
"location": "Pune, India",
"employment_type": "Full-time",
"skills": [
("Python", "must_have"),
("SQL", "preferred"),
("FastAPI", "preferred"),
("Git", "preferred"),
],
},
{
"company": "InnovateLabs",
"title": "HR Executive",
"description": (
"Support recruitment, employee engagement, and HR operations."
),
"responsibilities": (
"Coordinate hiring activities, maintain employee records, "
"and support onboarding processes."
),
"location": "Coimbatore, India",
"employment_type": "Full-time",
"skills": [
("HR Management", "must_have"),
("Communication", "must_have"),
],
},
{
"company": "InnovateLabs",
"title": "Sales Executive",
"description": (
"Build customer relationships and help drive business growth."
),
"responsibilities": (
"Identify leads, communicate with customers, "
"prepare proposals, and achieve sales targets."
),
"location": "Chennai, India",
"employment_type": "Full-time",
"skills": [
("Sales", "must_have"),
("Communication", "must_have"),
],
},
{
"company": "InnovateLabs",
"title": "Software Engineering Intern",
"description": (
"Gain hands-on experience building modern software applications."
),
"responsibilities": (
"Assist developers, fix bugs, write features, "
"and learn professional development practices."
),
"location": "Remote",
"employment_type": "Internship",
"skills": [
("Python", "preferred"),
("JavaScript", "preferred"),
("Git", "must_have"),
],
},
]

async def get_or_create_skill(db, name: str) -> Skill:
result = await db.execute(select(Skill).where(Skill.name == name))
skill = result.scalar_one_or_none()

```
if not skill:
    skill = Skill(name=name, category="general")
    db.add(skill)
    await db.flush()

return skill
```

async def get_or_create_company(db, name: str, industry: str) -> Company:
result = await db.execute(select(Company).where(Company.name == name))
company = result.scalar_one_or_none()

```
if not company:
    company = Company(
        name=name,
        industry=industry,
        verified_status="verified",
    )
    db.add(company)
    await db.flush()

return company
```

async def get_or_create_job(db, company: Company, job_data: dict) -> Job:
result = await db.execute(
select(Job).where(
Job.company_id == company.id,
Job.title == job_data["title"],
)
)
job = result.scalar_one_or_none()

```
if not job:
    job = Job(
        company_id=company.id,
        title=job_data["title"],
        description=job_data["description"],
        responsibilities=job_data["responsibilities"],
        location=job_data["location"],
        employment_type=job_data["employment_type"],
        status="published",
    )
    db.add(job)
    await db.flush()

    for skill_name, req_type in job_data["skills"]:
        skill = await get_or_create_skill(db, skill_name)

        db.add(
            JobSkill(
                job_id=job.id,
                skill_id=skill.id,
                requirement_type=req_type,
            )
        )

return job
```

async def seed_candidate(db):
result = await db.execute(
select(User).where(User.email == "[priya.candidate@viradmo.dev](mailto:priya.candidate@viradmo.dev)")
)
candidate_user = result.scalar_one_or_none()

```
if candidate_user:
    result = await db.execute(
        select(CandidateProfile).where(
            CandidateProfile.user_id == candidate_user.id
        )
    )
    candidate_profile = result.scalar_one_or_none()

    if candidate_profile:
        return candidate_user, candidate_profile

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

candidate_skills = [
    ("Python", 0.8),
    ("SQL", 0.75),
    ("Machine Learning", 0.6),
    ("JavaScript", 0.5),
    ("Communication", 0.7),
    ("Git", 0.6),
]

for skill_name, proficiency in candidate_skills:
    skill = await get_or_create_skill(db, skill_name)

    db.add(
        CandidateSkill(
            candidate_id=candidate_profile.id,
            skill_id=skill.id,
            source="resume",
            proficiency=proficiency,
        )
    )

return candidate_user, candidate_profile
```

async def seed_recruiter(db, company: Company):
result = await db.execute(
select(User).where(User.email == "[arjun.recruiter@northwindanalytics.dev](mailto:arjun.recruiter@northwindanalytics.dev)")
)
recruiter_user = result.scalar_one_or_none()

```
if recruiter_user:
    return recruiter_user

recruiter_user = User(
    email="arjun.recruiter@northwindanalytics.dev",
    password_hash=hash_password("DemoPass123!"),
    full_name="Arjun Mehta",
    role="recruiter",
)
db.add(recruiter_user)
await db.flush()

db.add(
    RecruiterProfile(
        user_id=recruiter_user.id,
        company_id=company.id,
        title="Talent Acquisition Lead",
    )
)

return recruiter_user
```

async def seed_assessment(db, job: Job):
result = await db.execute(
select(Assessment).where(
Assessment.job_id == job.id,
Assessment.title == "Aptitude Round",
)
)
existing = result.scalar_one_or_none()

```
if existing:
    return

assessment = Assessment(
    job_id=job.id,
    round_type="aptitude",
    title="Aptitude Round",
    duration_minutes=20,
)
db.add(assessment)
await db.flush()

db.add(
    Question(
        assessment_id=assessment.id,
        question_type="multiple_choice",
        prompt="Which SQL clause filters aggregated results?",
        options_json=json.dumps(
            ["WHERE", "HAVING", "ORDER BY", "LIMIT"]
        ),
        correct_option="HAVING",
    )
)
```

async def seed():
await init_db()

```
async with AsyncSessionLocal() as db:

    # Create all skills first
    for name in DEMO_SKILLS:
        await get_or_create_skill(db, name)

    await db.commit()

    # Create companies
    companies = {}

    for company_data in COMPANIES:
        company = await get_or_create_company(
            db,
            company_data["name"],
            company_data["industry"],
        )
        companies[company_data["name"]] = company

    await db.flush()

    # Create candidate
    await seed_candidate(db)

    # Create recruiter for Northwind Analytics
    await seed_recruiter(
        db,
        companies["Northwind Analytics"],
    )

    # Create all jobs
    created_jobs = {}

    for job_data in JOBS:
        company = companies[job_data["company"]]

        job = await get_or_create_job(
            db,
            company,
            job_data,
        )

        created_jobs[job_data["title"]] = job

    # Add assessment to Junior Data Analyst job
    if "Junior Data Analyst" in created_jobs:
        await seed_assessment(
            db,
            created_jobs["Junior Data Analyst"],
        )

    await db.commit()

    print("Seed complete.")
    print(f"Companies available -> {len(COMPANIES)}")
    print(f"Jobs available -> {len(JOBS)}")
    print(
        "Candidate login -> "
        "priya.candidate@viradmo.dev / DemoPass123!"
    )
    print(
        "Recruiter login -> "
        "arjun.recruiter@northwindanalytics.dev / DemoPass123!"
    )
```

if **name** == "**main**":
asyncio.run(seed())

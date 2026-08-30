import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_vira.db"

import pytest
from httpx import ASGITransport, AsyncClient

import app.models  # noqa: F401
from app.core.database import Base, engine
from app.main import app as fastapi_app


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.anyio
async def test_register_and_login_candidate(client):
    resp = await client.post(
        "/auth/register",
        json={
            "email": "test.candidate@example.com",
            "password": "TestPass123!",
            "full_name": "Test Candidate",
            "role": "candidate",
        },
    )
    assert resp.status_code == 201
    assert "access_token" in resp.json()

    resp = await client.post(
        "/auth/login", json={"email": "test.candidate@example.com", "password": "TestPass123!"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me_resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "candidate"


@pytest.mark.anyio
async def test_recruiter_requires_company_name(client):
    resp = await client.post(
        "/auth/register",
        json={
            "email": "test.recruiter@example.com",
            "password": "TestPass123!",
            "full_name": "Test Recruiter",
            "role": "recruiter",
        },
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_recruiter_can_create_and_publish_job(client):
    resp = await client.post(
        "/auth/register",
        json={
            "email": "recruiter2@example.com",
            "password": "TestPass123!",
            "full_name": "Recruiter Two",
            "role": "recruiter",
            "company_name": "Test Co",
        },
    )
    token = resp.json()["access_token"]

    job_resp = await client.post(
        "/jobs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Backend Engineer",
            "description": "Build APIs",
            "skills": [{"name": "Python", "requirement_type": "must_have"}],
            "status": "published",
        },
    )
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    list_resp = await client.get("/jobs")
    assert any(j["id"] == job_id for j in list_resp.json())


@pytest.mark.anyio
async def test_candidate_match_and_growth_path(client):
    reg_resp = await client.post(
        "/auth/register",
        json={
            "email": "candidate2@example.com",
            "password": "TestPass123!",
            "full_name": "Candidate Two",
            "role": "candidate",
        },
    )
    token = reg_resp.json()["access_token"]

    rec_resp = await client.post(
        "/auth/register",
        json={
            "email": "recruiter3@example.com",
            "password": "TestPass123!",
            "full_name": "Recruiter Three",
            "role": "recruiter",
            "company_name": "Match Co",
        },
    )
    rec_token = rec_resp.json()["access_token"]

    job_resp = await client.post(
        "/jobs",
        headers={"Authorization": f"Bearer {rec_token}"},
        json={
            "title": "Data Analyst",
            "description": "Analyze data",
            "skills": [
                {"name": "SQL", "requirement_type": "must_have"},
                {"name": "Power BI", "requirement_type": "preferred"},
            ],
            "status": "published",
        },
    )
    job_id = job_resp.json()["id"]

    match_resp = await client.post(
        f"/matching/analyze?job_id={job_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert match_resp.status_code == 200
    body = match_resp.json()
    assert "overall_score" in body
    assert "disclaimer" in body
    # No must-have skills demonstrated -> should be listed as missing, not silently dropped.
    assert "SQL" in body["missing_must_have"]

    growth_resp = await client.get(
        f"/matching/{job_id}/growth-path", headers={"Authorization": f"Bearer {token}"}
    )
    assert growth_resp.status_code == 200
    growth = growth_resp.json()
    assert len(growth["steps"]) > 0

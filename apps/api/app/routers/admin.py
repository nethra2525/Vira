import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.ai_and_system import AuditLog
from app.models.jobs import Application, Job
from app.models.user import Company, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/companies", dependencies=[Depends(require_role("admin"))])
async def list_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company))
    return result.scalars().all()


@router.patch("/companies/{company_id}/verify", dependencies=[Depends(require_role("admin"))])
async def verify_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found.")
    company.verified_status = "verified"
    await db.commit()
    return {"id": company.id, "verified_status": company.verified_status}


@router.get("/audit-logs", dependencies=[Depends(require_role("admin"))])
async def list_audit_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100))
    return result.scalars().all()


@router.get("/analytics", dependencies=[Depends(require_role("admin"))])
async def platform_analytics(db: AsyncSession = Depends(get_db)):
    job_count = (await db.execute(select(func.count(Job.id)))).scalar_one()
    application_count = (await db.execute(select(func.count(Application.id)))).scalar_one()
    company_count = (await db.execute(select(func.count(Company.id)))).scalar_one()
    user_count = (await db.execute(select(func.count(User.id)))).scalar_one()

    return {
        "total_jobs": job_count,
        "total_applications": application_count,
        "total_companies": company_count,
        "total_users": user_count,
    }

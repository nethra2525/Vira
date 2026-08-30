from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_token, hash_password, verify_password
from app.models.user import CandidateProfile, Company, RecruiterProfile, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    await db.flush()

    if payload.role == "candidate":
        db.add(CandidateProfile(user_id=user.id))
    else:
        if not payload.company_name:
            raise HTTPException(status_code=400, detail="company_name is required to register as a recruiter.")
        company = Company(name=payload.company_name)
        db.add(company)
        await db.flush()
        db.add(RecruiterProfile(user_id=user.id, company_id=company.id))

    await db.commit()

    access = create_token(str(user.id), user.role, "access")
    refresh = create_token(str(user.id), user.role, "refresh")
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated.")

    access = create_token(str(user.id), user.role, "access")
    refresh = create_token(str(user.id), user.role, "refresh")
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout():
    # Stateless JWT: logout is enforced client-side by discarding tokens.
    # A production build would maintain a refresh-token denylist.
    return {"detail": "Logged out."}

from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

async def register_user(db: AsyncSession, req: RegisterRequest) -> User:
    """Register a new user, checking for email uniqueness."""
    try:
        # Check if email exists
        stmt = select(User).where(User.email == req.email)
        res = await db.execute(stmt)
        existing_user = res.scalars().first()
    except HTTPException:
        raise
    except (SQLAlchemyError, DBAPIError, OSError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists"
        )
        
    hashed = hash_password(req.password)
    user = User(
        name=req.name,
        email=req.email,
        password_hash=hashed,
        role="analyst" # default role for new registrations
    )
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except (SQLAlchemyError, DBAPIError, OSError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    return user

async def authenticate_user(db: AsyncSession, req: LoginRequest) -> TokenResponse:
    """Authenticate credentials and generate JWT."""
    try:
        stmt = select(User).where(User.email == req.email)
        res = await db.execute(stmt)
        user = res.scalars().first()
    except HTTPException:
        raise
    except (SQLAlchemyError, DBAPIError, OSError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token = create_access_token(data={
        "sub": user.email,
        "role": user.role,
        "user_id": str(user.id),
        "name": user.name
    })
    
    return TokenResponse(access_token=access_token)

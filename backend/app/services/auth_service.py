from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


async def register_user(
    db: AsyncSession,
    req: RegisterRequest
) -> User:
    """
    Register a new user.

    Checks email uniqueness, hashes the password,
    creates the user and commits it to PostgreSQL.
    """

    # ---------------------------------------------------------
    # 1. Check whether the email already exists
    # ---------------------------------------------------------
    try:
        stmt = select(User).where(User.email == req.email)

        result = await db.execute(stmt)

        existing_user = result.scalars().first()

    except SQLAlchemyError as exc:
        await db.rollback()

        # Print the real database error in the backend terminal.
        print("DATABASE ERROR while checking existing user:")
        print(repr(exc))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )


    # ---------------------------------------------------------
    # 2. Prevent duplicate email registration
    # ---------------------------------------------------------
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists"
        )


    # ---------------------------------------------------------
    # 3. Hash password
    # ---------------------------------------------------------
    try:
        hashed_password = hash_password(req.password)

    except Exception as exc:
        print("PASSWORD HASHING ERROR:")
        print(repr(exc))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password processing error"
        )


    # ---------------------------------------------------------
    # 4. Create user
    # ---------------------------------------------------------
    user = User(
        name=req.name,
        email=req.email,
        password_hash=hashed_password,
        role="analyst",
    )


    # ---------------------------------------------------------
    # 5. Save user
    # ---------------------------------------------------------
    try:
        db.add(user)

        await db.commit()

        await db.refresh(user)

    except SQLAlchemyError as exc:
        await db.rollback()

        # VERY IMPORTANT:
        # This will show the actual PostgreSQL/SQLAlchemy
        # error in the terminal instead of hiding it.
        print("")
        print("=" * 70)
        print("DATABASE ERROR WHILE CREATING USER")
        print("=" * 70)
        print(repr(exc))
        print("=" * 70)
        print("")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

    return user


async def authenticate_user(
    db: AsyncSession,
    req: LoginRequest
) -> TokenResponse:
    """
    Authenticate a user and generate a JWT access token.
    """

    # ---------------------------------------------------------
    # 1. Find user by email
    # ---------------------------------------------------------
    try:
        stmt = select(User).where(User.email == req.email)

        result = await db.execute(stmt)

        user = result.scalars().first()

    except SQLAlchemyError as exc:
        await db.rollback()

        print("DATABASE ERROR while authenticating user:")
        print(repr(exc))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )


    # ---------------------------------------------------------
    # 2. Validate credentials
    # ---------------------------------------------------------
    if not user or not verify_password(
        req.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )


    # ---------------------------------------------------------
    # 3. Generate JWT
    # ---------------------------------------------------------
    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "user_id": str(user.id),
            "name": user.name,
        }
    )


    # ---------------------------------------------------------
    # 4. Return token
    # ---------------------------------------------------------
    return TokenResponse(
        access_token=access_token
    )
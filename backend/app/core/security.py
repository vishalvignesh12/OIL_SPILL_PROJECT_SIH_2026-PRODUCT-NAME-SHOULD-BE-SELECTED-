from datetime import datetime, timedelta, timezone
from typing import Optional, List

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings
from app.core.logging import user_id_var


# ============================================================
# Password hashing
# ============================================================

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
)


# ============================================================
# HTTP Bearer authentication
#
# IMPORTANT:
# HTTP Bearer authentication
# It only reads:
#
# Authorization: Bearer <JWT>
#
# Uses a standard HTTP Authorization header.
# ============================================================

bearer_scheme = HTTPBearer(
    auto_error=True
)


# ============================================================
# Password functions
# ============================================================

def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against an Argon2id hash."""

    try:
        return ph.verify(hashed_password, password)

    except VerifyMismatchError:
        return False

    except Exception:
        # Fallback for old bcrypt hashes, if any exist.
        try:
            from passlib.context import CryptContext

            pwd_context = CryptContext(
                schemes=["bcrypt"],
                deprecated="auto"
            )

            return pwd_context.verify(
                password,
                hashed_password
            )

        except Exception:
            return False


# ============================================================
# JWT creation
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a JWT access token."""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRATION_MINUTES
        )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


# ============================================================
# Current-user authentication
# ============================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
) -> dict:
    """
    Retrieve the current user from a JWT.

    Authentication uses a normal HTTP Bearer header:

        Authorization: Bearer <JWT>

    JWT authentication is handled through HTTP Bearer credentials.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        email: str = payload.get("sub")
        role: str = payload.get("role")
        user_id: str = payload.get("user_id")
        name: str = payload.get("name")

        if (
            email is None
            or role is None
            or user_id is None
        ):
            raise credentials_exception

        # Store user ID in request context for logging.
        user_id_var.set(user_id)

        return {
            "id": user_id,
            "email": email,
            "role": role,
            "name": name,
        }

    except JWTError:
        raise credentials_exception


# ============================================================
# Role-based access control
# ============================================================

class RoleChecker:
    """RBAC security checker to enforce user role levels."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: dict = Depends(get_current_user)
    ) -> dict:

        if current_user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your access level",
            )

        return current_user


# ============================================================
# Role dependencies
# ============================================================

require_analyst = RoleChecker([
    "analyst",
    "admin"
])

require_admin = RoleChecker([
    "admin"
])
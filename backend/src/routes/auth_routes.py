from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from typing import Optional
from sqlalchemy.orm import Session
from src.schemas.auth import LoginRequest, TokenResponse
from src.services.auth_service import AuthService
from src.db.postgres import get_db

# JWT configuration (should match auth_service.py)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Security scheme
security = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}}
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> dict:
    """
    Dependency to verify JWT token and return full user info.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Dict containing full user information: id, name, email, role

    Raises:
        HTTPException: If token is invalid or expired
    """
    # If no Authorization header provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user_id_int = int(user_id)
        
        # Fetch full user info based on role
        if role == "admin":
            return {
                "id": 1,
                "name": "Administrator",
                "email": "admin@admin.com",
                "role": "admin"
            }
        elif role == "student":
            # Fetch student from database
            from src.models.student import Student
            student = db.query(Student).filter(Student.id == user_id_int).first()
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            return {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "role": "student"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid role"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Authenticate user (admin or student) and return access token.

    For admin: Uses hardcoded credentials (admin@admin.com / admin)
    For student: If student exists, verify password; if not, create new student and login

    Args:
        login_data: Login request containing email, password, and role

    Returns:
        TokenResponse containing access token and user info

    Raises:
        HTTPException: If authentication fails
    """
    try:
        result = AuthService.login(db, login_data)
        return TokenResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(verify_token)):
    """
    Logout endpoint. In a stateless JWT system, logout is handled client-side
    by removing the token. This endpoint can be used for logging or cleanup.

    Args:
        current_user: Current authenticated user (from token)

    Returns:
        Success message
    """
    # In a stateless JWT system, logout is handled client-side
    # This endpoint could be used for server-side token blacklisting in the future
    return {"message": "Successfully logged out", "user": current_user}


@router.get("/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user (from token)

    Returns:
        Current user information
    """
    return current_user

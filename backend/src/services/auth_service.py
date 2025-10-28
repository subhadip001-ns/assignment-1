from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from jose import jwt
from datetime import datetime, timedelta

from src.models.student import Student
from src.schemas.auth import LoginRequest, StudentSignupRequest, UserResponse

# JWT configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Admin credentials
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "admin"


class AuthService:
    """
    Service class for handling authentication operations.

    Handles login, signup, and token generation for both admin and student users.
    """

    @staticmethod
    def authenticate_admin(email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate admin user.

        Args:
            email: Admin email
            password: Admin password

        Returns:
            User dict if authentication successful, None otherwise
        """
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            return {
                "id": 1,
                "name": "Administrator",
                "email": ADMIN_EMAIL,
                "role": "admin"
            }
        return None

    @staticmethod
    def authenticate_student(db: Session, email: str, password: str) -> Optional[Student]:
        """
        Authenticate student user.

        Args:
            db: Database session
            email: Student email
            password: Student password

        Returns:
            Student object if authentication successful, None otherwise
        """
        student = db.query(Student).filter(Student.email == email).first()
        if student and student.verify_password(password):
            return student
        return None

    @staticmethod
    def create_student(db: Session, signup_data: StudentSignupRequest) -> Student:
        """
        Create a new student account.

        Args:
            db: Database session
            signup_data: Student signup data

        Returns:
            Created Student object

        Raises:
            HTTPException: If student with email already exists
        """
        # Check if student already exists
        existing_student = db.query(Student).filter(Student.email == signup_data.email).first()
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this email already exists"
            )

        # Create new student
        student = Student(
            name=signup_data.name,
            email=signup_data.email
        )
        student.set_password(signup_data.password)

        try:
            db.add(student)
            db.commit()
            db.refresh(student)
            return student
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this email already exists"
            )

    @staticmethod
    def student_login_or_signup(db: Session, email: str, password: str) -> Student:
        """
        Handle student login/signup logic.
        If student exists, verify password and return student.
        If student doesn't exist, create new student and return.

        Args:
            db: Database session
            email: Student email
            password: Student password

        Returns:
            Student object (either existing or newly created)
        """
        # Try to authenticate existing student
        student = AuthService.authenticate_student(db, email, password)
        if student:
            return student

        # Student doesn't exist or password is wrong, try to create new student
        # For simplicity, we'll use the email as name (this could be improved)
        name = email.split('@')[0]  # Use part before @ as name

        signup_data = StudentSignupRequest(
            name=name,
            email=email,
            password=password
        )

        return AuthService.create_student(db, signup_data)

    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """
        Create JWT access token.

        Args:
            data: Data to encode in token

        Returns:
            JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> Dict[str, Any]:
        """
        Handle login for both admin and student users.

        Args:
            login_data: Login request data

        Returns:
            Dict containing token and user info

        Raises:
            HTTPException: If authentication fails
        """
        try:
            if login_data.role == "admin":
                user = AuthService.authenticate_admin(login_data.email, login_data.password)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid admin credentials"
                    )
            elif login_data.role == "student":
                student = AuthService.student_login_or_signup(db, login_data.email, login_data.password)
                user = {
                    "id": student.id,
                    "name": student.name,
                    "email": student.email,
                    "role": "student"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role"
                )

            # Create access token
            access_token = AuthService.create_access_token(
                data={"sub": str(user["id"]), "role": user["role"]}
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user
            }

        finally:
            db.close()

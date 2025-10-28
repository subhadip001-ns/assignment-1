from src.routes.student_routes import router as student_router
from src.routes.course_routes import router as course_router
from src.routes.enrollment_routes import router as enrollment_router
from src.routes.auth_routes import router as auth_router
from src.routes.ai_routes import router as ai_router

__all__ = ["student_router", "course_router", "enrollment_router", "auth_router", "ai_router"]


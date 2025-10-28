from src.routes.student_routes import router as student_router
from src.routes.course_routes import router as course_router
from src.routes.enrollment_routes import router as enrollment_router

__all__ = ["student_router", "course_router", "enrollment_router"]


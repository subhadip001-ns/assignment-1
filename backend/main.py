from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.postgres import init_db
from src.routes import student_router, course_router, enrollment_router, auth_router, ai_router, module_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database tables
    init_db()
    yield
    # Shutdown: Add any cleanup logic here if needed


app = FastAPI(
    title="Student Course Enrollment Portal API",
    description="A RESTful API for managing students, courses, and enrollments in an educational institution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(ai_router)
app.include_router(module_router)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - API welcome message
    """
    return {
        "message": "Welcome to the Student Course Enrollment Portal API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

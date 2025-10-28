# Student Course Enrollment Portal API

A RESTful API system built with FastAPI and PostgreSQL for managing student enrollments in an educational institution.

## Project Overview

The Student Course Enrollment Portal is a comprehensive backend API that facilitates:
- **Student Management**: Complete CRUD operations for student profiles
- **Course Management**: Full course catalog management with instructor information
- **Enrollment Management**: Many-to-many relationship handling between students and courses
- **Association Queries**: Retrieve students per course and courses per student


## Login Credentials

- Admin:
  - Email: admin@admin.com
  - Password: admin
- Student:
  - Email: student@student.com
  - Password: student

## Architecture

The project follows a clean, layered architecture:

```
src/
├── db/              # Database configuration and connection
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic schemas for validation
├── services/        # Business logic layer
└── routes/          # FastAPI route handlers (API endpoints)
```

## Core Features

### Student Management
- Create, read, update, and delete student profiles
- Unique email constraint
- View all courses a student is enrolled in

### Course Management
- CRUD operations for academic courses
- Course details including name, description, and instructor
- View all students enrolled in a course

### Enrollment Management
- Enroll students in courses (many-to-many relationship)
- Prevent duplicate enrollments
- Cascade deletion (removing a student/course removes their enrollments)

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Package Manager**: uv
- **Environment Management**: python-dotenv

## Database Schema

### Students Table
- `id` (Primary Key)
- `name` (String, required)
- `email` (String, unique, required)

### Courses Table
- `id` (Primary Key)
- `name` (String, required)
- `description` (Text, optional)
- `instructor` (String, required)

### Enrollments Table
- `id` (Primary Key)
- `student_id` (Foreign Key → students.id)
- `course_id` (Foreign Key → courses.id)
- Unique constraint on (student_id, course_id)

## Quick Start

### Prerequisites
- Python 3.14+
- PostgreSQL
- uv package manager (https://docs.astral.sh/uv/)

### Installation

1. **Clone the repository**
```bash
cd assignment-1
```

2. **Set up environment variables**

Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/enrollment_db
```

See [ENV_SETUP.md](ENV_SETUP.md) for detailed environment configuration.

3. **Install dependencies**
```bash
uv sync
```

4. **Run the DB from docker**
```bash
docker compose up -d
```
5. **Run the application**
```bash
python main.py
```

6. **Seed the database**
```bash
uv run seed.py
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Test the API

Use uv's module mode to run pytest:

- Run all tests (split across test/):
```bash
cd backend
uv run python -m pytest -v
```

- Run a specific suite:
```bash
uv run python -m pytest test/test_auth.py -v
uv run python -m pytest test/test_students.py -v
uv run python -m pytest test/test_courses.py -v
uv run python -m pytest test/test_enrollments.py -v
```

- Run a single test:
```bash
uv run python -m pytest test/test_auth.py::TestAuthEndpoints::test_admin_login_success -v
```

## 📚 API Endpoints

### Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/students/` | Create a new student |
| GET | `/students/{id}` | Get student details |
| GET | `/students/` | List all students (paginated) |
| PUT | `/students/{id}` | Update student information |
| DELETE | `/students/{id}` | Delete a student |
| GET | `/students/{id}/courses` | Get courses for a student |

### Courses

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/courses/` | Create a new course |
| GET | `/courses/{id}` | Get course details |
| GET | `/courses/` | List all courses (paginated) |
| PUT | `/courses/{id}` | Update course information |
| DELETE | `/courses/{id}` | Delete a course |
| GET | `/courses/{id}/students` | Get students in a course |

### Enrollments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/enrollments/` | Enroll a student in a course |
| GET | `/enrollments/{id}` | Get enrollment details |
| GET | `/enrollments/` | List all enrollments (paginated) |
| DELETE | `/enrollments/{id}` | Delete an enrollment |
| DELETE | `/enrollments/student/{student_id}/course/{course_id}` | Delete specific enrollment |

## 🧪 Example API Usage

### Create a Student
```bash
curl -X POST "http://localhost:8000/students/" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john.doe@example.com"}'
```

### Create a Course
```bash
curl -X POST "http://localhost:8000/courses/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Introduction to Computer Science",
    "description": "Basic CS concepts",
    "instructor": "Dr. Smith"
  }'
```

### Enroll a Student
```bash
curl -X POST "http://localhost:8000/enrollments/" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "course_id": 1}'
```

### Get Student's Courses
```bash
curl -X GET "http://localhost:8000/students/1/courses"
```

## Error Handling

The API provides comprehensive error handling:
- `400 Bad Request`: Validation errors, duplicate entries
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid data format
- `500 Internal Server Error`: Server errors

## Documentation

- **Interactive API Documentation**: Visit `/docs` for Swagger UI
- **Alternative Documentation**: Visit `/redoc` for ReDoc


## Project Structure

```
assignment-1/
├── main.py                 # Application entry point
├── pyproject.toml          # Project dependencies
├── README.md               # This file
├── ENV_SETUP.md           # Environment setup guide
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore rules
└── src/
    ├── __init__.py
    ├── db/
    │   ├── __init__.py
    │   └── postgres.py     # Database configuration
    ├── models/
    │   ├── __init__.py
    │   ├── student.py      # Student model
    │   ├── course.py       # Course model
    │   └── enrollment.py   # Enrollment model
    ├── schemas/
    │   ├── __init__.py
    │   ├── student.py      # Student schemas
    │   ├── course.py       # Course schemas
    │   └── enrollment.py   # Enrollment schemas
    ├── services/
    │   ├── __init__.py
    │   ├── student_service.py
    │   ├── course_service.py
    │   └── enrollment_service.py
    └── routes/
        ├── __init__.py
        ├── student_routes.py
        ├── course_routes.py
        └── enrollment_routes.py
```

## Health Check

Check if the API is running:
```bash
curl http://localhost:8000/health
```

## AI Integration

### RAG Service

The RAG service is used to search for course information. It uses the VoyageAI SDK to search for course information.

```bash
# To ingest the course documents
uv run python -m pytest test/test_courses.py -v
```

### AI Service

### Observability (Langfuse)

- Add to your `.env`:

### To run Langfuse use python 3.12

```
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```
uv run --python 3.12 python main.py

```
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

Instrumentation is added to `ai_routes.py` to trace `/ai/chat` and `/ai/chat/stream` requests and record generations.
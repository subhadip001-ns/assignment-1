# Student Course Enrollment Portal - Overview

A full-stack educational platform with AI assistance for managing student enrollments.

## 🏗️ Architecture

**Backend (FastAPI + PostgreSQL)**
- RESTful API for CRUD operations on students, courses, and enrollments
- Clean layered architecture with SQLAlchemy ORM and Pydantic validation
- JWT-based authentication with role-based access (admin/student)

**Frontend (React + TypeScript)**
- Modern SPA using TanStack Router, Tailwind CSS, and shadcn/ui
- Functional components with protected routes
- Dashboard, course browsing, and admin management interfaces

**AI Module (LangChain + Groq + RAG)**
- Intelligent chat assistant for course information and enrollment help
- RAG-powered semantic search using Voyage AI embeddings
- Tools for arithmetic, course lookup, and enrollment operations
- Streaming responses with Langfuse observability

## 🚀 Quick Start

1. **Setup Database**: `docker compose up -d`
2. **Backend**: `cd backend && uv sync && python main.py`
3. **Frontend**: `cd frontend && pnpm install && pnpm dev`
4. **Seed Data**: `uv run seed.py`

## 🔑 Key Features

- **Student Management**: Profile CRUD with unique email constraints
- **Course Catalog**: Full course management with instructor details
- **Enrollment System**: Many-to-many relationships with duplicate prevention
- **AI Assistant**: Context-aware chat with course search and enrollment help
- **Role-Based Access**: Admin vs student permissions
- **Real-time Streaming**: AI responses via Server-Sent Events

## 📡 API Endpoints

- `/students/*` - Student management
- `/courses/*` - Course catalog
- `/enrollments/*` - Enrollment operations
- `/ai/chat*` - AI assistant (regular + streaming)

## 🛠️ Tech Stack

- **Backend**: FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **AI**: LangChain, Groq LLM, Voyage AI embeddings, Langfuse

## 📖 Documentation

- [Backend API Docs](backend/README.md) - Full API reference
- [Frontend Guide](frontend/README.md) - React app setup
- [AI Module](backend/src/ai/README.md) - AI assistant details


## Login Credentials

- Admin:
  - Email: admin@admin.com
  - Password: admin
- Student:
  - Email: student@student.com
  - Password: student

## Jenkins Pipeline

- The Jenkins pipeline is configured to build the project, test the backend, and deploy the application.
- The pipeline is configured to run on the day-4 branch.
- The pipeline is configured to run on the Jenkins server.
- v1.0.3
import os
from sqlalchemy import create_engine, text
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    ""
)

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI routes.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models if they don't exist.
    """
    from src.models import student, course, enrollment, module
    
    print("Initializing database...")
    try:
        Base.metadata.create_all(bind=engine)

        # Lightweight migration: ensure students.password_hash exists
        inspector = sa_inspect(engine)
        if 'students' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('students')]
            if 'password_hash' not in cols:
                print("Adding missing column students.password_hash ...")
                with engine.begin() as conn:
                    conn.execute(
                        text("ALTER TABLE students ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''")
                    )
                print("Column students.password_hash added")

        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


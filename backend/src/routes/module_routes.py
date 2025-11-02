from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from src.db.postgres import get_db
from src.schemas.module import ModuleCreate, ModuleUpdate, ModuleResponse
from src.services.module_service import ModuleService

router = APIRouter(prefix="/modules", tags=["modules"])


@router.post("/", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(
    module_data: ModuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new module for a course
    
    - **course_id**: ID of the course (required)
    - **title**: Module title (required)
    - **description**: Module description (optional)
    - **content**: Module content/material (optional)
    - **order**: Sequence order within the course (default: 0)
    """
    return ModuleService.create_module(db, module_data)


@router.get("/{module_id}", response_model=ModuleResponse)
def get_module(
    module_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a module by ID
    
    - **module_id**: ID of the module to retrieve
    """
    return ModuleService.get_module(db, module_id)


@router.get("/course/{course_id}", response_model=List[ModuleResponse])
def get_course_modules(
    course_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all modules for a specific course
    
    - **course_id**: ID of the course
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    return ModuleService.get_modules_by_course(db, course_id, skip, limit)


@router.put("/{module_id}", response_model=ModuleResponse)
def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a module's information
    
    - **module_id**: ID of the module to update
    - **title**: Updated module title (optional)
    - **description**: Updated description (optional)
    - **content**: Updated content (optional)
    - **order**: Updated order (optional)
    """
    return ModuleService.update_module(db, module_id, module_data)


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    module_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a module
    
    - **module_id**: ID of the module to delete
    """
    ModuleService.delete_module(db, module_id)
    return None

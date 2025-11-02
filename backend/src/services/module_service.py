from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List

from src.models.module import Module
from src.models.course import Course
from src.schemas.module import ModuleCreate, ModuleUpdate


class ModuleService:
    @staticmethod
    def create_module(db: Session, module_data: ModuleCreate) -> Module:
        """
        Create a new module for a course
        
        Args:
            db: Database session
            module_data: Module creation data
            
        Returns:
            Created module instance
            
        Raises:
            HTTPException: If course not found
        """
        # Verify course exists
        course = db.query(Course).filter(Course.id == module_data.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {module_data.course_id} not found"
            )
        
        # Create module
        module = Module(**module_data.model_dump())
        try:
            db.add(module)
            db.commit()
            db.refresh(module)
            return module
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating module"
            )

    @staticmethod
    def get_module(db: Session, module_id: int) -> Module:
        """
        Get a module by ID
        
        Args:
            db: Database session
            module_id: Module ID
            
        Returns:
            Module instance
            
        Raises:
            HTTPException: If module not found
        """
        module = db.query(Module).filter(Module.id == module_id).first()
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module with id {module_id} not found"
            )
        return module

    @staticmethod
    def get_modules_by_course(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[Module]:
        """
        Get all modules for a course, ordered by order field
        
        Args:
            db: Database session
            course_id: Course ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of module instances
        """
        return (
            db.query(Module)
            .filter(Module.course_id == course_id)
            .order_by(Module.order.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_module(db: Session, module_id: int, module_data: ModuleUpdate) -> Module:
        """
        Update a module's information
        
        Args:
            db: Database session
            module_id: Module ID
            module_data: Module update data
            
        Returns:
            Updated module instance
            
        Raises:
            HTTPException: If module not found
        """
        module = ModuleService.get_module(db, module_id)
        
        # Update only provided fields
        update_data = module_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(module, field, value)
        
        try:
            db.commit()
            db.refresh(module)
            return module
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating module"
            )

    @staticmethod
    def delete_module(db: Session, module_id: int) -> None:
        """
        Delete a module
        
        Args:
            db: Database session
            module_id: Module ID
            
        Raises:
            HTTPException: If module not found
        """
        module = ModuleService.get_module(db, module_id)
        db.delete(module)
        db.commit()

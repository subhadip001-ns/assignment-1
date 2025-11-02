from pydantic import BaseModel, Field
from typing import Optional


class ModuleBase(BaseModel):
    """Base schema for Module with common attributes"""
    title: str = Field(..., min_length=1, max_length=200, description="Module title")
    description: Optional[str] = Field(None, description="Module description")
    content: Optional[str] = Field(None, description="Module content/material")
    order: int = Field(0, ge=0, description="Sequence order within the course")


class ModuleCreate(ModuleBase):
    """Schema for creating a new module"""
    course_id: int = Field(..., description="ID of the course this module belongs to")


class ModuleUpdate(BaseModel):
    """Schema for updating a module (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)


class ModuleResponse(ModuleBase):
    """Schema for module response"""
    id: int
    course_id: int

    model_config = {"from_attributes": True}

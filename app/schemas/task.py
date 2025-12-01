from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime

# Schema for creating a task
class TaskCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    skills_required: Optional[List[str]] = None

# Schema for reading task data
class TaskRead(BaseModel):
    id: UUID
    title: str
    description: str
    location: Optional[str]
    skills_required: Optional[List[str]]
    posted_by_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
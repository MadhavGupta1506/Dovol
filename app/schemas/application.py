from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from ..models.applications import ApplicationStatus

# Schema for creating an application
class ApplicationCreate(BaseModel):
    task_id: UUID
    volunteer_id: UUID

# Schema for reading application
class ApplicationRead(BaseModel):
    id: UUID
    task_id: UUID
    volunteer_id: UUID
    status: ApplicationStatus
    applied_at: datetime

    class Config:
        orm_mode = True
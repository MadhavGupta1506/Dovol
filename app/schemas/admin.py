from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from ..models.user import Roles
from ..models.applications import ApplicationStatus

# Dashboard Statistics
class DashboardStats(BaseModel):
    total_users: int
    total_volunteers: int
    total_ngos: int
    total_admins: int
    total_tasks: int
    active_tasks: int
    total_applications: int
    pending_applications: int
    accepted_applications: int
    rejected_applications: int

# User Management Schemas
class UserListItem(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: Roles
    location: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

class UserDetailAdmin(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: Roles
    location: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserRoleUpdate(BaseModel):
    role: Roles

# Task Management Schemas
class TaskListAdmin(BaseModel):
    id: UUID
    title: str
    description: str
    location: Optional[str]
    skills_required: Optional[List[str]]
    posted_by_id: UUID
    is_active: bool
    created_at: datetime
    application_count: int = 0

    class Config:
        orm_mode = True

class TaskStatusUpdate(BaseModel):
    is_active: bool

# Application Management Schemas
class ApplicationListAdmin(BaseModel):
    id: UUID
    task_id: UUID
    task_title: str
    volunteer_id: UUID
    volunteer_name: str
    volunteer_email: str
    status: ApplicationStatus
    applied_at: datetime

    class Config:
        orm_mode = True

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus

# Activity Log Schema
class ActivityLog(BaseModel):
    user_email: str
    action: str
    timestamp: datetime
    details: Optional[str] = None

# System Health Schema
class SystemHealth(BaseModel):
    database_connected: bool
    total_records: int
    uptime: str

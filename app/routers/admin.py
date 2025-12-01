from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from ..database import get_db
from ..auth.dependencies import require_admin
from ..models.user import User, Roles
from ..models.volunteer_task import VolunteerTask
from ..models.applications import Application, ApplicationStatus
from ..schemas.admin import (
    DashboardStats,
    UserListItem,
    UserDetailAdmin,
    UserStatusUpdate,
    UserRoleUpdate,
    TaskListAdmin,
    TaskStatusUpdate,
    ApplicationListAdmin,
    ApplicationStatusUpdate,
    SystemHealth
)

router = APIRouter(prefix="/admin", tags=["admin"])

# ==================== Dashboard Statistics ====================

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get comprehensive dashboard statistics for admin"""
    
    # Count total users
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    # Count users by role
    volunteers_result = await db.execute(
        select(func.count(User.id)).where(User.role == Roles.volunteer)
    )
    total_volunteers = volunteers_result.scalar()
    
    ngos_result = await db.execute(
        select(func.count(User.id)).where(User.role == Roles.ngo)
    )
    total_ngos = ngos_result.scalar()
    
    admins_result = await db.execute(
        select(func.count(User.id)).where(User.role == Roles.admin)
    )
    total_admins = admins_result.scalar()
    
    # Count tasks
    total_tasks_result = await db.execute(select(func.count(VolunteerTask.id)))
    total_tasks = total_tasks_result.scalar()
    
    active_tasks_result = await db.execute(
        select(func.count(VolunteerTask.id)).where(VolunteerTask.is_active == True)
    )
    active_tasks = active_tasks_result.scalar()
    
    # Count applications
    total_applications_result = await db.execute(select(func.count(Application.id)))
    total_applications = total_applications_result.scalar()
    
    pending_apps_result = await db.execute(
        select(func.count(Application.id)).where(Application.status == ApplicationStatus.pending)
    )
    pending_applications = pending_apps_result.scalar()
    
    accepted_apps_result = await db.execute(
        select(func.count(Application.id)).where(Application.status == ApplicationStatus.accepted)
    )
    accepted_applications = accepted_apps_result.scalar()
    
    rejected_apps_result = await db.execute(
        select(func.count(Application.id)).where(Application.status == ApplicationStatus.rejected)
    )
    rejected_applications = rejected_apps_result.scalar()
    
    return DashboardStats(
        total_users=total_users,
        total_volunteers=total_volunteers,
        total_ngos=total_ngos,
        total_admins=total_admins,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        total_applications=total_applications,
        pending_applications=pending_applications,
        accepted_applications=accepted_applications,
        rejected_applications=rejected_applications
    )

# ==================== User Management ====================

@router.get("/users", response_model=List[UserListItem])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users with optional filtering and pagination"""
    
    query = select(User)
    
    # Apply filters
    filters = []
    if role:
        try:
            role_enum = Roles[role]
            filters.append(User.role == role_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid role")
    
    if is_active is not None:
        filters.append(User.is_active == is_active)
    
    if search:
        search_filter = or_(
            User.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Apply pagination
    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users

@router.get("/users/{user_id}", response_model=UserDetailAdmin)
async def get_user_details(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get detailed information about a specific user"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.patch("/users/{user_id}/status", response_model=UserDetailAdmin)
async def update_user_status(
    user_id: UUID,
    status_update: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Activate or deactivate a user account"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own status")
    
    user.is_active = status_update.is_active
    await db.commit()
    await db.refresh(user)
    
    return user

@router.patch("/users/{user_id}/role", response_model=UserDetailAdmin)
async def update_user_role(
    user_id: UUID,
    role_update: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Change a user's role"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot modify your own role")
    
    user.role = role_update.role
    await db.commit()
    await db.refresh(user)
    
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user account (soft delete by deactivating)"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Soft delete by deactivating
    user.is_active = False
    await db.commit()
    
    return None

# ==================== Task Management ====================

@router.get("/tasks", response_model=List[TaskListAdmin])
async def get_all_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all volunteer tasks with optional filtering"""
    
    query = select(VolunteerTask)
    
    # Apply filters
    filters = []
    if is_active is not None:
        filters.append(VolunteerTask.is_active == is_active)
    
    if search:
        search_filter = or_(
            VolunteerTask.title.ilike(f"%{search}%"),
            VolunteerTask.description.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(desc(VolunteerTask.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Get application count for each task
    tasks_with_counts = []
    for task in tasks:
        app_count_result = await db.execute(
            select(func.count(Application.id)).where(Application.task_id == task.id)
        )
        app_count = app_count_result.scalar()
        
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "location": task.location,
            "skills_required": task.skills_required,
            "posted_by_id": task.posted_by_id,
            "is_active": task.is_active,
            "created_at": task.created_at,
            "application_count": app_count
        }
        tasks_with_counts.append(TaskListAdmin(**task_dict))
    
    return tasks_with_counts

@router.get("/tasks/{task_id}")
async def get_task_details(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get detailed information about a specific task"""
    
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get task poster details
    poster_result = await db.execute(select(User).where(User.id == task.posted_by_id))
    poster = poster_result.scalar_one_or_none()
    
    # Get applications for this task
    apps_result = await db.execute(
        select(Application).where(Application.task_id == task_id)
    )
    applications = apps_result.scalars().all()
    
    return {
        "task": task,
        "posted_by": poster,
        "total_applications": len(applications),
        "pending_applications": len([a for a in applications if a.status == ApplicationStatus.pending]),
        "accepted_applications": len([a for a in applications if a.status == ApplicationStatus.accepted]),
        "rejected_applications": len([a for a in applications if a.status == ApplicationStatus.rejected])
    }

@router.patch("/tasks/{task_id}/status", response_model=TaskStatusUpdate)
async def update_task_status(
    task_id: UUID,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Activate or deactivate a task"""
    
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.is_active = status_update.is_active
    await db.commit()
    
    return status_update

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a task (soft delete by deactivating)"""
    
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Soft delete
    task.is_active = False
    await db.commit()
    
    return None

# ==================== Application Management ====================

@router.get("/applications", response_model=List[ApplicationListAdmin])
async def get_all_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = None,
    task_id: Optional[UUID] = None,
    volunteer_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all applications with optional filtering"""
    
    query = select(Application, VolunteerTask.title, User.full_name, User.email).join(
        VolunteerTask, Application.task_id == VolunteerTask.id
    ).join(
        User, Application.volunteer_id == User.id
    )
    
    # Apply filters
    filters = []
    if status_filter:
        try:
            status_enum = ApplicationStatus[status_filter]
            filters.append(Application.status == status_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    if task_id:
        filters.append(Application.task_id == task_id)
    
    if volunteer_id:
        filters.append(Application.volunteer_id == volunteer_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(desc(Application.applied_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    applications = []
    for row in rows:
        app, task_title, volunteer_name, volunteer_email = row
        applications.append(ApplicationListAdmin(
            id=app.id,
            task_id=app.task_id,
            task_title=task_title,
            volunteer_id=app.volunteer_id,
            volunteer_name=volunteer_name,
            volunteer_email=volunteer_email,
            status=app.status,
            applied_at=app.applied_at
        ))
    
    return applications

@router.patch("/applications/{application_id}/status")
async def update_application_status(
    application_id: UUID,
    status_update: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update application status (approve/reject)"""
    
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.status = status_update.status
    await db.commit()
    await db.refresh(application)
    
    return {
        "message": "Application status updated successfully",
        "application_id": application.id,
        "new_status": application.status.value
    }

# ==================== System Health & Monitoring ====================

@router.get("/system/health", response_model=SystemHealth)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get system health status"""
    
    try:
        # Test database connection
        await db.execute(select(func.count(User.id)))
        database_connected = True
        
        # Count total records across all tables
        users_count = await db.execute(select(func.count(User.id)))
        tasks_count = await db.execute(select(func.count(VolunteerTask.id)))
        apps_count = await db.execute(select(func.count(Application.id)))
        
        total_records = (
            users_count.scalar() + 
            tasks_count.scalar() + 
            apps_count.scalar()
        )
        
    except Exception as e:
        database_connected = False
        total_records = 0
    
    return SystemHealth(
        database_connected=database_connected,
        total_records=total_records,
        uptime="System running"  # You can implement actual uptime tracking
    )

# ==================== Recent Activity ====================

@router.get("/activity/recent")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get recent platform activity"""
    
    # Get recent users
    recent_users = await db.execute(
        select(User).order_by(desc(User.created_at)).limit(5)
    )
    users = recent_users.scalars().all()
    
    # Get recent tasks
    recent_tasks = await db.execute(
        select(VolunteerTask).order_by(desc(VolunteerTask.created_at)).limit(5)
    )
    tasks = recent_tasks.scalars().all()
    
    # Get recent applications
    recent_apps = await db.execute(
        select(Application).order_by(desc(Application.applied_at)).limit(5)
    )
    applications = recent_apps.scalars().all()
    
    return {
        "recent_users": [
            {"email": u.email, "role": u.role.value, "created_at": u.created_at}
            for u in users
        ],
        "recent_tasks": [
            {"title": t.title, "posted_by_id": t.posted_by_id, "created_at": t.created_at}
            for t in tasks
        ],
        "recent_applications": [
            {"task_id": a.task_id, "volunteer_id": a.volunteer_id, "status": a.status.value, "applied_at": a.applied_at}
            for a in applications
        ]
    }

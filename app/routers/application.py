from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from ..schemas.application import ApplicationCreate, ApplicationRead
from ..models.applications import Application, ApplicationStatus
from ..models.volunteer_task import VolunteerTask
from ..database import get_db
from ..auth.dependencies import require_roles

router = APIRouter(prefix="/applications", tags=["applications"])


# Apply for a task (Volunteer only)
@router.post("/", response_model=ApplicationRead)
async def apply_for_task(
    application: ApplicationCreate,
    current_user=Depends(require_roles("volunteer")),
    db: AsyncSession = Depends(get_db)
):
    # Ensure volunteer_id is always the current user
    application.volunteer_id = current_user.id

    # Check if task exists
    task_result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == application.task_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if already applied
    existing_result = await db.execute(
        select(Application).where(
            Application.task_id == application.task_id,
            Application.volunteer_id == current_user.id
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied for this task")

    # Create new application
    new_application = Application(
        task_id=application.task_id,
        volunteer_id=current_user.id
    )
    db.add(new_application)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    await db.refresh(new_application)
    return new_application


# Get all applications for volunteer (Volunteer only)
@router.get("/me", response_model=list[ApplicationRead])
async def get_my_applications(
    current_user=Depends(require_roles("volunteer")),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Application).where(Application.volunteer_id == current_user.id))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# Get all applications for a task (NGO only)
@router.get("/task/{task_id}", response_model=list[ApplicationRead])
async def get_applications_for_task(
    task_id: UUID,
    current_user=Depends(require_roles("ngo")),
    db: AsyncSession = Depends(get_db)
):
    # Check if task exists
    task_result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        result = await db.execute(select(Application).where(Application.task_id == task_id))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# Update application status (NGO only)
@router.patch("/{application_id}/status", response_model=ApplicationRead)
async def update_application_status(
    application_id: UUID,
    status: ApplicationStatus,
    current_user=Depends(require_roles("ngo")),
    db: AsyncSession = Depends(get_db)
):
    # Check if application exists
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = status
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    await db.refresh(application)
    return application


@router.delete("/{application_id}", response_model=dict)
async def delete_application(
    application_id: UUID,
    current_user=Depends(require_roles("volunteer", "ngo")),
    db: AsyncSession = Depends(get_db)
):
    # Fetch the application
    result = await db.execute(select(Application).where(Application.id == application_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check permissions
    if current_user.role == "volunteer" and application.volunteer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this application")
    if current_user.role == "ngo":
        # Optional: check that NGO owns the task
        task_result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == application.task_id))
        task = task_result.scalar_one_or_none()
        if not task or task.posted_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this application")

    # Delete the application
    try:
        await db.delete(application)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {"detail": "Application deleted successfully"}
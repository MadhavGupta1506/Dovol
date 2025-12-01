from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.task import TaskCreate, TaskRead
from ..models.volunteer_task import VolunteerTask
from ..database import get_db
from sqlalchemy.future import select
from uuid import UUID
from ..auth.dependencies import require_roles,get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Create task (NGO only)
@router.post("/", response_model=TaskRead)
async def create_task(task: TaskCreate, current_user=Depends(require_roles("ngo")), db: AsyncSession = Depends(get_db)):
    new_task = VolunteerTask(
        title=task.title,
        description=task.description,
        location=task.location,
        skills_required=task.skills_required,
        posted_by_id=current_user.id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

# Get all active tasks (any authenticated user)
@router.get("/", response_model=list[TaskRead])
async def get_tasks(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.is_active == True))
    tasks = result.scalars().all()
    return tasks

# Get task by ID (any authenticated user)
@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update task (NGO owner or admin)
@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: UUID, task_update: TaskCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Permission: NGO who posted the task or admin can update
    if (getattr(current_user, "role", None) != "admin") and (task.posted_by_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this task")

    # Update allowed fields
    task.title = task_update.title # type: ignore
    task.description = task_update.description # type: ignore
    task.location = task_update.location # type: ignore
    task.skills_required = task_update.skills_required # type: ignore
    # if your TaskCreate includes start_date/end_date/status, update them too:
    if hasattr(task_update, "start_date"):
        task.start_date = getattr(task_update, "start_date", task.start_date)
    if hasattr(task_update, "end_date"):
        task.end_date = getattr(task_update, "end_date", task.end_date)
    if hasattr(task_update, "status"):
        task.status = getattr(task_update, "status", task.status)

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

# Delete task (soft delete by default) - NGO owner or admin
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Permission: NGO who posted the task or admin can delete
    if (getattr(current_user, "role", None) != "admin") and (task.posted_by_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this task")

    # Soft delete: mark as inactive
    task.is_active = False
    db.add(task)
    await db.commit()
    return None

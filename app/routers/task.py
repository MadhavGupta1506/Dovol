from fastapi import APIRouter, Depends, HTTPException
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
@router.get("/match", response_model=list[TaskRead])
async def match_tasks(current_user=Depends(require_roles("volunteer")), db: AsyncSession = Depends(get_db)):
    if not current_user.location:
        raise HTTPException(status_code=400, detail="Please set your skills first")

    query = select(VolunteerTask).where(VolunteerTask.is_active == True)
    result = await db.execute(query)
    tasks = result.scalars().all()

    matched_tasks = [task for task in tasks if task.skills_required and any(
        skill.lower() in (task.skills_required or "").lower()
        for skill in current_user.full_name.split()  # (placeholder: later store real skills)
    )]
    return matched_tasks

@router.get("/nearby", response_model=list[TaskRead])
async def get_nearby_tasks(location: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.location.ilike(f"%{location}%")))
    return result.scalars().all()

@router.get("/search", response_model=list[TaskRead])
async def search_tasks(q: str, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(VolunteerTask).where(
            VolunteerTask.title.ilike(f"%{q}%") | VolunteerTask.description.ilike(f"%{q}%")
        )
    )
    return result.scalars().all()

@router.patch("/{task_id}/close", response_model=TaskRead)
async def close_task(task_id: UUID, current_user=Depends(require_roles("ngo")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.is_active = False
    await db.commit()
    await db.refresh(task)
    return task

# Update task (NGO only)
@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    task_update: TaskCreate,  # reuse TaskCreate schema for simplicity
    current_user=Depends(require_roles("ngo")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    # Update fields
    task.title = task_update.title
    task.description = task_update.description
    task.location = task_update.location
    task.skills_required = task_update.skills_required
    
    await db.commit()
    await db.refresh(task)
    return task

# Delete task (soft delete)
@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(
    task_id: UUID,
    current_user=Depends(require_roles("ngo")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(VolunteerTask).where(VolunteerTask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.posted_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    task.is_active = False  # soft delete
    await db.commit()
    await db.refresh(task)
    return task

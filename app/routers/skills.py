# app/routers/skills.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import get_db
from ..models.user import User, Roles
from ..models.skill import Skill, VolunteerSkill
from ..schemas.skill import SkillList, SkillRead
from ..auth.dependencies import get_current_user  # JWT dependency

router = APIRouter(prefix="/skills", tags=["Skills"])

# CREATE (Add skills)
@router.post("/")
async def add_skills_to_user(skill_list: SkillList, 
                             db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    if current_user.role != Roles.volunteer:
        raise HTTPException(status_code=400, detail="Only volunteers can have skills")

    for skill_name in skill_list.skills:
        # check if skill exists
        skill_result = await db.execute(select(Skill).where(Skill.name == skill_name))
        skill = skill_result.scalars().first()
        if not skill:
            skill = Skill(name=skill_name)
            db.add(skill)
            await db.flush()

        # check if already linked
        vs_result = await db.execute(
            select(VolunteerSkill).where(
                VolunteerSkill.user_id == current_user.id,
                VolunteerSkill.skill_id == skill.id
            )
        )
        if not vs_result.scalars().first():
            db.add(VolunteerSkill(user_id=current_user.id, skill_id=skill.id))

    await db.commit()
    return {"message": "Skills added successfully"}

# READ (Get skills)
@router.get("/", response_model=list[SkillRead])
async def get_user_skills(db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Skill)
        .select_from(VolunteerSkill)
        .join(Skill, VolunteerSkill.skill_id == Skill.id)
        .where(VolunteerSkill.user_id == current_user.id)
    )
    skills = result.scalars().all()
    if not skills:
        raise HTTPException(status_code=404, detail="No skills found for this user")
    
    return skills


# UPDATE (Replace skills)
@router.put("/")
async def update_user_skills(skill_list: SkillList, 
                             db: AsyncSession = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    # delete old links
    await db.execute(
        f"DELETE FROM volunteer_skills WHERE user_id = '{current_user.id}'"
    )
    await db.commit()
    # add new ones
    return await add_skills_to_user(skill_list, db, current_user)

# DELETE (Remove single skill)
@router.delete("/{skill_id}")
async def delete_user_skill(skill_id: uuid.UUID, 
                            db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(VolunteerSkill).where(
            VolunteerSkill.user_id == current_user.id,
            VolunteerSkill.skill_id == skill_id
        )
    )
    mapping = result.scalars().first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Skill not found for this user")

    await db.delete(mapping)
    await db.commit()
    return {"message": "Skill removed successfully"}
# app/schemas/skill.py
from pydantic import BaseModel
from typing import List
import uuid

class SkillList(BaseModel):
    skills: List[str]

class SkillRead(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        orm_mode = True
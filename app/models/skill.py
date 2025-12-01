import uuid
from datetime import datetime,timezone
import pytz
from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base
ist = pytz.timezone("Asia/Kolkata")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(String, nullable=False, unique=True)   # e.g. "Teaching", "First Aid"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ist))

class VolunteerSkill(Base):
    __tablename__ = "volunteer_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)   # FK to users.id
    skill_id = Column(UUID(as_uuid=True), nullable=False)  # FK to skills.id
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ist))
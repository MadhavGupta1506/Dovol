import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class ApplicationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("volunteer_tasks.id"), nullable=False)
    volunteer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(ApplicationStatus, name="application_status"), default=ApplicationStatus.pending)
    applied_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    task = relationship("VolunteerTask")
    volunteer = relationship("User")
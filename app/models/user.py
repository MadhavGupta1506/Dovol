import uuid
from datetime import datetime,timezone
from sqlalchemy import Column, String, Boolean, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base
import enum
import pytz
ist = pytz.timezone("Asia/Kolkata")
# Define user roles
class Roles(enum.Enum):
    volunteer = "volunteer"
    ngo = "ngo"
    admin = "admin"

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Roles), nullable=False)
    location = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ist))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ist), onupdate=lambda: datetime.now(ist))
    
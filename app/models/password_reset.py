import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base
import enum

class OTPType(enum.Enum):
    signup = "signup"
    password_reset = "password_reset"

class PasswordResetOTP(Base):
    __tablename__ = 'password_reset_otps'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    otp_type = Column(Enum(OTPType), nullable=False, default=OTPType.password_reset)
    is_used = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)

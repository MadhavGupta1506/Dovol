from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import (
    UserCreate, UserRead, UserLogin, UserUpdate, 
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest,
    SignupOTPRequest, SignupVerifyOTP
)
from ..models.user import User
from ..models.password_reset import PasswordResetOTP, OTPType
from fastapi.security import OAuth2PasswordRequestForm
from ..database import get_db
from ..auth.auth import hash_password, verify_password
from ..auth.jwt_handler import create_access_token
from sqlalchemy.future import select
from ..auth.dependencies import get_current_user, require_roles
from ..services.email_service import generate_otp, get_otp_expiration, send_otp_email, send_signup_otp_email, is_otp_expired
from datetime import datetime, timezone
router = APIRouter(prefix="/users", tags=["users"])

# ==================== Signup with OTP ====================

@router.post("/signup/request-otp")
async def request_signup_otp(
    request: SignupOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 1: Request OTP for email verification during signup
    Sends a 6-digit OTP to the email address
    """
    # Check if email is already registered
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login or use forgot password."
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = get_otp_expiration(minutes=10)
    
    # Save OTP to database
    new_otp = PasswordResetOTP(
        email=request.email,
        otp_code=otp_code,
        otp_type=OTPType.signup,
        expires_at=expires_at
    )
    db.add(new_otp)
    await db.commit()
    
    # Send OTP email
    email_sent = await send_signup_otp_email(request.email, otp_code)
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email. Please try again later."
        )
    
    return {
        "message": "OTP has been sent to your email",
        "success": True,
        "email": request.email,
        "expires_in_minutes": 10
    }

@router.post("/signup/verify", response_model=UserRead)
async def verify_signup_otp(
    request: SignupVerifyOTP,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Verify OTP and complete signup
    Creates the user account after successful OTP verification
    """
    # Check if email is already registered
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Find the most recent unused signup OTP for this email
    otp_result = await db.execute(
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.email == request.email,
            PasswordResetOTP.otp_code == request.otp,
            PasswordResetOTP.otp_type == OTPType.signup,
            PasswordResetOTP.is_used == False
        )
        .order_by(PasswordResetOTP.created_at.desc())
    )
    otp_record = otp_result.scalar_one_or_none()
    
    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )
    
    # Check if OTP has expired
    if is_otp_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )
    
    # Create the user account
    new_user = User(
        full_name=request.full_name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        location=request.location
    )
    db.add(new_user)
    
    # Mark OTP as used
    otp_record.is_used = True
    otp_record.is_verified = True
    otp_record.used_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

# ==================== Authentication ====================

# Login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# Get current user profile
@router.get("/me", response_model=UserRead)
async def get_profile(current_user=Depends(get_current_user)):
    return current_user

# Update current user profile
@router.patch("/me", response_model=UserRead)
async def update_profile(
    user_update: UserUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Update only provided fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.location is not None:
        current_user.location = user_update.location
    
    await db.commit()
    await db.refresh(current_user)
    return current_user

# ==================== Password Reset Endpoints ====================

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 1: Request OTP for password reset
    Sends a 6-digit OTP to the user's registered email
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists or not for security
        return {
            "message": "If your email is registered, you will receive an OTP shortly",
            "success": True
        }
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = get_otp_expiration(minutes=10)
    
    # Save OTP to database
    new_otp = PasswordResetOTP(
        email=request.email,
        otp_code=otp_code,
        otp_type=OTPType.password_reset,
        expires_at=expires_at
    )
    db.add(new_otp)
    await db.commit()
    
    # Send OTP email
    email_sent = await send_otp_email(request.email, otp_code, user.full_name)
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email. Please try again later."
        )
    
    return {
        "message": "OTP has been sent to your email",
        "success": True,
        "expires_in_minutes": 10
    }

@router.post("/verify-otp")
async def verify_otp(
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Verify the OTP sent to email
    This endpoint validates the OTP without resetting the password
    """
    # Find the most recent unused password reset OTP for this email
    result = await db.execute(
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.email == request.email,
            PasswordResetOTP.otp_code == request.otp,
            PasswordResetOTP.otp_type == OTPType.password_reset,
            PasswordResetOTP.is_used == False
        )
        .order_by(PasswordResetOTP.created_at.desc())
    )
    otp_record = result.scalar_one_or_none()
    
    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )
    
    # Check if OTP has expired
    if is_otp_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )
    
    # Mark OTP as verified (but not used yet)
    otp_record.is_verified = True
    await db.commit()
    
    return {
        "message": "OTP verified successfully",
        "success": True,
        "verified": True
    }

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 3: Reset password using verified OTP
    User must provide email, OTP, and new password
    """
    # Find the most recent verified and unused password reset OTP
    result = await db.execute(
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.email == request.email,
            PasswordResetOTP.otp_code == request.otp,
            PasswordResetOTP.otp_type == OTPType.password_reset,
            PasswordResetOTP.is_verified == True,
            PasswordResetOTP.is_used == False
        )
        .order_by(PasswordResetOTP.created_at.desc())
    )
    otp_record = result.scalar_one_or_none()
    
    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or unverified OTP"
        )
    
    # Check if OTP has expired
    if is_otp_expired(otp_record.expires_at):
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )
    
    # Get user
    user_result = await db.execute(select(User).where(User.email == request.email))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Update user password
    user.password_hash = hash_password(request.new_password)
    
    # Mark OTP as used
    otp_record.is_used = True
    otp_record.used_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {
        "message": "Password has been reset successfully",
        "success": True
    }
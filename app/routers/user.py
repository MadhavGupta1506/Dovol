from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserCreate, UserRead, UserLogin
from ..models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from ..database import get_db
from ..auth.auth import hash_password, verify_password
from ..auth.jwt_handler import create_access_token
from sqlalchemy.future import select
from ..auth.dependencies import get_current_user, require_roles
router = APIRouter(prefix="/users", tags=["users"])

# Signup
@router.post("/signup", response_model=UserRead)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
        location=user.location
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

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
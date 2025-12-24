from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas import user as user_schemas
from app.services import user_service
from app.core.database import get_db
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=user_schemas.User)
async def read_user_me(current_user: user_schemas.User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=user_schemas.User)
async def create_user(user: user_schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Force role to be CLIENT for public signups
    user.role = user_schemas.UserRole.CLIENT
    return await user_service.create_user(db=db, user=user)

@router.get("/", response_model=List[user_schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await user_service.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=user_schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=user_schemas.User)
async def update_user(user_id: int, user_update: user_schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    updated_user = await user_service.update_user(db, user_id=user_id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=user_schemas.User)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    deleted_user = await user_service.delete_user(db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user

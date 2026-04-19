from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.schemas import UserResponse, UserCreate, UserRole
from app.core.database import get_db, get_service_db
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users():
    db = get_db()
    return db.table(settings.USERS_TABLE).select("*").execute().data

@router.post("/", response_model=UserResponse)
async def add_user(user: UserCreate):
    db = get_service_db()
    return db.table(settings.USERS_TABLE).insert(user.dict()).execute().data[0]

@router.patch("/{user_id}/role")
async def update_user_role(user_id: str, role: UserRole):
    db = get_service_db()
    db.table(settings.USERS_TABLE).update({"role": role}).eq("id", user_id).execute()
    return {"status": "updated"}

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    db = get_service_db()
    db.table(settings.USERS_TABLE).delete().eq("id", user_id).execute()
    return {"status": "deleted"}

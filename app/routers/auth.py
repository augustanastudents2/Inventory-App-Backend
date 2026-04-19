from fastapi import APIRouter, HTTPException
from app.models.schemas import UserResponse
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.post("/login")
async def login(credentials: dict):
    db = get_db()
    email = credentials.get("email")
    # In a real app, use Supabase Auth. For now, simulate based on users table.
    user = db.table(settings.USERS_TABLE).select("*").eq("email", email).single().execute()
    if not user.data:
        # Fallback for initial admin
        if email == "admin@asa.com":
            return {"email": email, "name": "ASA Admin", "role": "Admin", "token": "mock-token"}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {**user.data, "token": "mock-token"}

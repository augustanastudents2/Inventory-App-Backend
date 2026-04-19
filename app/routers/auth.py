from fastapi import APIRouter, HTTPException
from app.models.schemas import UserResponse
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.post("/login")
async def login(credentials: dict):
    db = get_db()
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    try:
        # Authenticate with Supabase Auth
        auth_response = db.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        # Get user details from our users table to get the role
        user_data = db.table(settings.USERS_TABLE).select("*").eq("email", email).single().execute()
        
        # If user exists in auth but not in our users table, they might be a new user or admin
        if not user_data.data:
            # Default for the first admin if not in table yet
            if email == "admin@asa.com":
                return {
                    "email": email,
                    "name": "ASA Admin",
                    "role": "Admin",
                    "token": auth_response.session.access_token
                }
            raise HTTPException(status_code=403, detail="User not authorized in inventory system")
            
        return {
            **user_data.data,
            "token": auth_response.session.access_token
        }
        
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        raise HTTPException(status_code=500, detail=f"Authentication error: {error_msg}")

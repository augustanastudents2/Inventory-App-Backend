from fastapi import APIRouter, HTTPException
from app.models.schemas import UserResponse, LoginRequest
from app.core.database import get_db
from app.core.config import settings
import traceback

router = APIRouter()

@router.post("/login")
async def login(credentials: LoginRequest):
    db = get_db()
    email = credentials.email.strip().lower()
    password = credentials.password
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    try:
        # 1. Authenticate with Supabase Auth
        try:
            auth_response = db.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
        except Exception as auth_err:
            auth_msg = str(auth_err)
            if "Invalid login credentials" in auth_msg:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            raise HTTPException(status_code=401, detail=f"Supabase Auth error: {auth_msg}")
        
        if not auth_response or not auth_response.user:
            raise HTTPException(status_code=401, detail="Authentication failed: No user returned")
            
        # 2. Get user details from our users table
        try:
            user_query = db.table(settings.USERS_TABLE).select("*").eq("email", email).execute()
        except Exception as db_err:
            raise HTTPException(status_code=500, detail=f"Database query error: {str(db_err)}")
        
        if not user_query.data:
            # Fallback for initial admin
            if email == "admin@asa.com":
                return {
                    "email": email,
                    "name": "ASA Admin",
                    "role": "Admin",
                    "token": auth_response.session.access_token
                }
            raise HTTPException(
                status_code=403, 
                detail=f"User {email} authenticated, but not found in '{settings.USERS_TABLE}' table. Please add this email to the table."
            )
            
        # 3. Return user data and token
        user_record = user_query.data[0]
        return {
            "id": str(user_record.get("id")),
            "email": user_record.get("email"),
            "name": user_record.get("name"),
            "role": user_record.get("role"),
            "token": auth_response.session.access_token
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        # Catch-all for unexpected errors with full trace in logs
        print(f"CRITICAL LOGIN ERROR: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

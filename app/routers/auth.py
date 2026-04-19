from fastapi import APIRouter, HTTPException
from app.models.schemas import UserResponse, LoginRequest
from app.core.database import get_db, get_service_db
from app.core.config import settings
import traceback

router = APIRouter()

@router.post("/login")
async def login(credentials: LoginRequest):
    # Use service_db to bypass RLS for the internal user lookup
    db = get_service_db()
    # Normalize input email
    email_input = credentials.email.strip().lower()
    password = credentials.password
    
    if not email_input or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    try:
        # 1. Authenticate with Supabase Auth
        try:
            auth_response = db.auth.sign_in_with_password({
                "email": email_input,
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
            user_query = db.table(settings.USERS_TABLE).select("*").ilike("email", email_input).execute()
        except Exception as db_err:
            raise HTTPException(status_code=500, detail=f"Database query error: {str(db_err)}")
        
        if not user_query.data:
            # Fallback for initial admin
            if email_input == "admin@asa.com":
                return {
                    "email": email_input,
                    "name": "ASA Admin",
                    "role": "Admin",
                    "token": auth_response.session.access_token
                }
            
            raise HTTPException(
                status_code=403, 
                detail=f"User '{email_input}' authenticated, but not found in '{settings.USERS_TABLE}' table."
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
        print(f"CRITICAL LOGIN ERROR: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

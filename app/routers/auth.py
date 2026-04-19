from fastapi import APIRouter, HTTPException
from app.models.schemas import UserResponse, LoginRequest
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.post("/login")
async def login(credentials: LoginRequest):
    db = get_db()
    email = credentials.email
    password = credentials.password
    
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
        # We use .execute() and check the data list instead of .single() 
        # to avoid the PGRST116 error if something is slightly off
        user_query = db.table(settings.USERS_TABLE).select("*").eq("email", email).execute()
        
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
                detail=f"User {email} is authenticated in Supabase Auth but not found in the '{settings.USERS_TABLE}' table. Please ensure the email matches exactly."
            )
            
        # Return the first matching user
        return {
            **user_query.data[0],
            "token": auth_response.session.access_token
        }
        
    except Exception as e:
        error_msg = str(e)
        # Handle the specific case where .single() might still be called by accident or other PGRST errors
        if "PGRST116" in error_msg:
             raise HTTPException(
                status_code=403, 
                detail=f"User {email} not found in the users table. Please check for typos or extra spaces in the email."
            )
        if "Invalid login credentials" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        raise HTTPException(status_code=500, detail=f"Authentication error: {error_msg}")

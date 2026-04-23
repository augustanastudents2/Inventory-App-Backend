from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.schemas import UserResponse, UserCreate, UserRole
from app.core.database import get_db, get_service_db
from app.core.config import settings
import httpx

router = APIRouter()

async def _create_supabase_auth_user(db, *, email: str, password: str, name: str | None, role: str) -> str:
    """
    Create a Supabase Auth user via admin API.
    Returns the auth user id (uuid).
    Works with either supabase-py admin helpers or raw HTTP fallback.
    """
    # Prefer supabase-py admin helper if available
    try:
        admin = getattr(getattr(db, "auth", None), "admin", None)
        if admin and hasattr(admin, "create_user"):
            resp = admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"name": name, "role": role},
            })
            uid = getattr(getattr(resp, "user", None), "id", None)
            if uid:
                return uid
    except Exception:
        # fall through to HTTP method
        pass

    # Raw HTTP fallback (GoTrue admin endpoint)
    url = settings.SUPABASE_URL.rstrip("/") + "/auth/v1/admin/users"
    headers = {
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {"name": name, "role": role},
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=f"Supabase Auth admin error: {r.text}")
        data = r.json()
        uid = data.get("id")
        if not uid:
            raise HTTPException(status_code=500, detail="Supabase Auth admin error: no user id returned")
        return uid

async def _delete_supabase_auth_user(db, user_id: str) -> None:
    try:
        admin = getattr(getattr(db, "auth", None), "admin", None)
        if admin and hasattr(admin, "delete_user"):
            admin.delete_user(user_id)
            return
    except Exception:
        pass

    url = settings.SUPABASE_URL.rstrip("/") + f"/auth/v1/admin/users/{user_id}"
    headers = {
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        await client.delete(url, headers=headers)

@router.get("/", response_model=List[UserResponse])
async def get_users():
    db = get_db()
    return db.table(settings.USERS_TABLE).select("*").execute().data

@router.post("/", response_model=UserResponse)
async def add_user(user: UserCreate):
    db = get_service_db()
    email = (user.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not user.password:
        raise HTTPException(status_code=400, detail="Password is required")

    # 1) Create user in Supabase Auth (required for login)
    try:
        auth_id = await _create_supabase_auth_user(
            db,
            email=email,
            password=user.password,
            name=user.name,
            role=str(user.role),
        )
    except HTTPException as he:
        # Supabase returns 400/422 with messages like "User already registered"
        detail = str(he.detail or "")
        if he.status_code in (400, 409, 422) and "already" in detail.lower():
            raise HTTPException(status_code=409, detail="A user with this email already exists")
        raise
    except Exception as exc:
        msg = str(exc) or repr(exc)
        if "already" in msg.lower() or "registered" in msg.lower():
            raise HTTPException(status_code=409, detail="A user with this email already exists")
        raise HTTPException(status_code=500, detail=f"Failed to create auth user: {msg}")

    # 2) Insert user profile row (no plaintext password)
    payload = user.dict(exclude={"password"})
    payload["email"] = email
    if auth_id:
        payload["id"] = auth_id

    try:
        return db.table(settings.USERS_TABLE).insert(payload).execute().data[0]
    except Exception as exc:
        # If profile insert fails, keep system consistent by deleting auth user.
        if auth_id:
            try:
                await _delete_supabase_auth_user(db, auth_id)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to create user record: {str(exc)}")

@router.patch("/{user_id}/role")
async def update_user_role(user_id: str, role: UserRole):
    db = get_service_db()
    db.table(settings.USERS_TABLE).update({"role": role}).eq("id", user_id).execute()
    return {"status": "updated"}

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    db = get_service_db()
    auth_err: str | None = None
    try:
        # Delete from Supabase Auth first (prevents orphan auth accounts).
        await _delete_supabase_auth_user(db, user_id)
    except Exception as exc:
        # Don't block profile cleanup, but surface the failure.
        auth_err = str(exc) or repr(exc)

    # Always delete the profile row
    db.table(settings.USERS_TABLE).delete().eq("id", user_id).execute()

    if auth_err:
        return {"status": "deleted_profile_only", "auth_delete_error": auth_err}
    return {"status": "deleted"}

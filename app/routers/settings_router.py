from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.models.schemas import CategoryResponse, TagResponse, StorageLocationResponse, VendorResponse, CategoryBase, TagBase, StorageLocationBase, VendorBase
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

def _api_error_code(exc: Exception) -> str | None:
    """
    Supabase/postgrest errors stringify to a dict-like message. We keep this
    helper lightweight to avoid binding to a specific exception class.
    """
    try:
        if isinstance(exc.args[0], dict):
            return exc.args[0].get("code")
    except Exception:
        return None
    return None

def _conflict_as_existing(detail: str) -> HTTPException:
    return HTTPException(status_code=409, detail=detail)

# Categories
@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    db = get_db()
    return db.table(settings.CATEGORIES_TABLE).select("*").execute().data

@router.post("/categories", response_model=CategoryResponse)
async def add_category(cat: CategoryBase):
    db = get_db()
    try:
        return db.table(settings.CATEGORIES_TABLE).insert(cat.dict()).execute().data[0]
    except Exception as exc:
        if _api_error_code(exc) == "23505":
            existing = db.table(settings.CATEGORIES_TABLE).select("*").eq("name", cat.name).single().execute()
            if existing.data:
                return existing.data
            raise _conflict_as_existing(f"Category '{cat.name}' already exists")
        raise

@router.patch("/categories/{old_name}")
async def update_category(old_name: str, cat: CategoryBase):
    db = get_db()
    # Update category name
    db.table(settings.CATEGORIES_TABLE).update({"name": cat.name}).eq("name", old_name).execute()
    # Update products using this category
    db.table(settings.PRODUCTS_TABLE).update({"category": cat.name}).eq("category", old_name).execute()
    return {"status": "updated"}

@router.delete("/categories/{name}")
async def delete_category(name: str):
    db = get_db()
    db.table(settings.CATEGORIES_TABLE).delete().eq("name", name).execute()
    return {"status": "deleted"}

# Tags
@router.get("/tags", response_model=List[TagResponse])
async def get_tags():
    db = get_db()
    return db.table(settings.TAGS_TABLE).select("*").execute().data

@router.post("/tags", response_model=TagResponse)
async def add_tag(tag: TagBase):
    db = get_db()
    try:
        return db.table(settings.TAGS_TABLE).insert(tag.dict()).execute().data[0]
    except Exception as exc:
        if _api_error_code(exc) == "23505":
            existing = db.table(settings.TAGS_TABLE).select("*").eq("name", tag.name).single().execute()
            if existing.data:
                return existing.data
            raise _conflict_as_existing(f"Tag '{tag.name}' already exists")
        raise

@router.patch("/tags/{old_name}")
async def update_tag(old_name: str, tag: TagBase):
    db = get_db()
    db.table(settings.TAGS_TABLE).update({"name": tag.name}).eq("name", old_name).execute()
    # Note: Updating tags in products is more complex because it's an array
    # In a real app, we'd use a SQL function or fetch and update all products
    return {"status": "updated"}

@router.delete("/tags/{name}")
async def delete_tag(name: str):
    db = get_db()
    db.table(settings.TAGS_TABLE).delete().eq("name", name).execute()
    return {"status": "deleted"}

# Storage Locations
@router.get("/storage-locations", response_model=List[StorageLocationResponse])
async def get_storage_locations():
    db = get_db()
    return db.table(settings.STORAGE_LOCATIONS_TABLE).select("*").execute().data

@router.post("/storage-locations", response_model=StorageLocationResponse)
async def add_storage(loc: StorageLocationBase):
    db = get_db()
    try:
        return db.table(settings.STORAGE_LOCATIONS_TABLE).insert(loc.dict()).execute().data[0]
    except Exception as exc:
        if _api_error_code(exc) == "23505":
            q = db.table(settings.STORAGE_LOCATIONS_TABLE).select("*").eq("area", loc.area)
            if loc.sub is None:
                q = q.is_("sub", None)
            else:
                q = q.eq("sub", loc.sub)
            existing = q.single().execute()
            if existing.data:
                return existing.data
            raise _conflict_as_existing("Storage location already exists")
        raise

@router.patch("/storage-locations")
async def update_storage(payload: Dict[str, Any]):
    db = get_db()
    old_loc = payload.get("oldLoc")
    new_loc = payload.get("newLoc")
    db.table(settings.STORAGE_LOCATIONS_TABLE).update(new_loc).eq("area", old_loc["area"]).eq("sub", old_loc["sub"]).execute()
    # Update products (simplified JSONB update)
    db.table(settings.PRODUCTS_TABLE).update({"storage": new_loc}).eq("storage->>area", old_loc["area"]).eq("storage->>sub", old_loc["sub"]).execute()
    return {"status": "updated"}

@router.delete("/storage-locations")
async def delete_storage_location(area: str = Query(...), sub: Optional[str] = Query(None)):
    db = get_db()
    q = db.table(settings.STORAGE_LOCATIONS_TABLE).delete().eq("area", area)
    if sub is None:
        q = q.is_("sub", None)
    else:
        q = q.eq("sub", sub)
    q.execute()
    # Clear storage for products referencing this location
    cleared = {"area": "", "sub": ""}
    prod_q = db.table(settings.PRODUCTS_TABLE).update({"storage": cleared}).eq("storage->>area", area)
    if sub is None:
        prod_q = prod_q.is_("storage->>sub", None)
    else:
        prod_q = prod_q.eq("storage->>sub", sub)
    prod_q.execute()
    return {"status": "deleted"}

# Vendors
@router.get("/vendors", response_model=List[VendorResponse])
async def get_vendors():
    db = get_db()
    return db.table(settings.VENDORS_TABLE).select("*").execute().data

@router.post("/vendors", response_model=VendorResponse)
async def add_vendor(vendor: VendorBase):
    db = get_db()
    try:
        return db.table(settings.VENDORS_TABLE).insert(vendor.dict()).execute().data[0]
    except Exception as exc:
        if _api_error_code(exc) == "23505":
            existing = db.table(settings.VENDORS_TABLE).select("*").eq("name", vendor.name).single().execute()
            if existing.data:
                return existing.data
            raise _conflict_as_existing(f"Vendor '{vendor.name}' already exists")
        raise

@router.patch("/vendors/{old_name}")
async def update_vendor(old_name: str, vendor: VendorBase):
    db = get_db()
    db.table(settings.VENDORS_TABLE).update(vendor.dict()).eq("name", old_name).execute()
    db.table(settings.PRODUCTS_TABLE).update({"vendor": vendor.dict()}).eq("vendor->>name", old_name).execute()
    return {"status": "updated"}

@router.delete("/vendors/{name}")
async def delete_vendor(name: str):
    db = get_db()
    db.table(settings.VENDORS_TABLE).delete().eq("name", name).execute()
    # Clear vendor for products referencing this vendor
    db.table(settings.PRODUCTS_TABLE).update({"vendor": {"name": "", "contact": ""}}).eq("vendor->>name", name).execute()
    return {"status": "deleted"}

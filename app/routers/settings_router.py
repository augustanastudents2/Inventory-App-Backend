from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.models.schemas import CategoryResponse, TagResponse, StorageLocationResponse, VendorResponse, CategoryBase, TagBase, StorageLocationBase, VendorBase
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

# Categories
@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    db = get_db()
    return db.table(settings.CATEGORIES_TABLE).select("*").execute().data

@router.post("/categories", response_model=CategoryResponse)
async def add_category(cat: CategoryBase):
    db = get_db()
    return db.table(settings.CATEGORIES_TABLE).insert(cat.dict()).execute().data[0]

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
    return db.table(settings.TAGS_TABLE).insert(tag.dict()).execute().data[0]

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
    return db.table(settings.STORAGE_LOCATIONS_TABLE).insert(loc.dict()).execute().data[0]

@router.patch("/storage-locations")
async def update_storage(payload: Dict[str, Any]):
    db = get_db()
    old_loc = payload.get("oldLoc")
    new_loc = payload.get("newLoc")
    db.table(settings.STORAGE_LOCATIONS_TABLE).update(new_loc).eq("area", old_loc["area"]).eq("sub", old_loc["sub"]).execute()
    # Update products (simplified JSONB update)
    db.table(settings.PRODUCTS_TABLE).update({"storage": new_loc}).eq("storage->>area", old_loc["area"]).eq("storage->>sub", old_loc["sub"]).execute()
    return {"status": "updated"}

# Vendors
@router.get("/vendors", response_model=List[VendorResponse])
async def get_vendors():
    db = get_db()
    return db.table(settings.VENDORS_TABLE).select("*").execute().data

@router.post("/vendors", response_model=VendorResponse)
async def add_vendor(vendor: VendorBase):
    db = get_db()
    return db.table(settings.VENDORS_TABLE).insert(vendor.dict()).execute().data[0]

@router.patch("/vendors/{old_name}")
async def update_vendor(old_name: str, vendor: VendorBase):
    db = get_db()
    db.table(settings.VENDORS_TABLE).update(vendor.dict()).eq("name", old_name).execute()
    db.table(settings.PRODUCTS_TABLE).update({"vendor": vendor.dict()}).eq("vendor->>name", old_name).execute()
    return {"status": "updated"}

from fastapi import APIRouter, Depends, HTTPException
from typing import List
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

# Storage Locations
@router.get("/storage-locations", response_model=List[StorageLocationResponse])
async def get_storage_locations():
    db = get_db()
    return db.table(settings.STORAGE_LOCATIONS_TABLE).select("*").execute().data

@router.post("/storage-locations", response_model=StorageLocationResponse)
async def add_storage(loc: StorageLocationBase):
    db = get_db()
    return db.table(settings.STORAGE_LOCATIONS_TABLE).insert(loc.dict()).execute().data[0]

# Vendors
@router.get("/vendors", response_model=List[VendorResponse])
async def get_vendors():
    db = get_db()
    return db.table(settings.VENDORS_TABLE).select("*").execute().data

@router.post("/vendors", response_model=VendorResponse)
async def add_vendor(vendor: VendorBase):
    db = get_db()
    return db.table(settings.VENDORS_TABLE).insert(vendor.dict()).execute().data[0]

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.models.schemas import ProductResponse, ProductCreate, ProductUpdate, StockAdjustment
from app.core.database import get_db
from app.core.config import settings
import uuid
from datetime import datetime

router = APIRouter()

def compute_availability(quantity: int, threshold: int) -> str:
    if quantity == 0: return "Out of stock"
    if quantity <= threshold: return "Low stock"
    return "In-stock"

_PRODUCT_DB_FIELD_MAP = {
    # Supabase columns in your project are all-lowercase without underscores
    "buyingPrice": "buyingprice",
    "thresholdValue": "thresholdvalue",
    "expiryDate": "expirydate",
    "createdAt": "createdat",
    "updatedAt": "updatedat",
}

def _product_to_db(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in payload.items():
        out[_PRODUCT_DB_FIELD_MAP.get(k, k)] = v
    return out

def _product_from_db(row: Dict[str, Any]) -> Dict[str, Any]:
    reverse = {v: k for k, v in _PRODUCT_DB_FIELD_MAP.items()}
    out: Dict[str, Any] = {}
    for k, v in row.items():
        out[reverse.get(k, k)] = v
    return out

@router.get("/", response_model=List[ProductResponse])
async def get_products():
    db = get_db()
    response = db.table(settings.PRODUCTS_TABLE).select("*").execute()
    # In a real app, we'd also fetch stock history for each product or use a join
    return [_product_from_db(p) for p in (response.data or [])]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    db = get_db()
    response = db.table(settings.PRODUCTS_TABLE).select("*").eq("id", product_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return _product_from_db(response.data)

@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    db = get_db()
    product_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    availability = compute_availability(product.quantity, product.thresholdValue)
    
    product_data = _product_to_db(product.dict())
    product_data.update({
        "id": product_id,
        _PRODUCT_DB_FIELD_MAP.get("createdAt", "createdAt"): now,
        _PRODUCT_DB_FIELD_MAP.get("updatedAt", "updatedAt"): now,
        "availability": availability
    })
    
    # Create initial stock history
    history_entry = {
        "id": f"evt_{int(datetime.utcnow().timestamp())}",
        "productid": product_id,
        "at": now,
        "delta": product.quantity,
        "reason": "Initial stock"
    }
    
    response = db.table(settings.PRODUCTS_TABLE).insert(product_data).execute()
    db.table(settings.STOCK_HISTORY_TABLE).insert(history_entry).execute()
    
    return _product_from_db(response.data[0])

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, updates: ProductUpdate):
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    # Get current product to recompute availability if needed
    current = db.table(settings.PRODUCTS_TABLE).select("*").eq("id", product_id).single().execute()
    if not current.data:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = _product_to_db(updates.dict(exclude_unset=True))
    update_data[_PRODUCT_DB_FIELD_MAP.get("updatedAt", "updatedAt")] = now
    
    thr_key = _PRODUCT_DB_FIELD_MAP.get("thresholdValue", "thresholdValue")
    if "quantity" in update_data or thr_key in update_data:
        qty = update_data.get("quantity", current.data.get("quantity"))
        thr = update_data.get(thr_key, current.data.get(thr_key))
        update_data["availability"] = compute_availability(qty, thr)
        
    response = db.table(settings.PRODUCTS_TABLE).update(update_data).eq("id", product_id).execute()
    return _product_from_db(response.data[0])

@router.post("/adjust-stock")
async def adjust_stock(adjustment: StockAdjustment):
    db = get_db()
    now = datetime.utcnow().isoformat()
    
    current = db.table(settings.PRODUCTS_TABLE).select("*").eq("id", adjustment.productId).single().execute()
    if not current.data:
        raise HTTPException(status_code=404, detail="Product not found")
        
    new_qty = max(0, current.data["quantity"] + adjustment.delta)
    thr_key = _PRODUCT_DB_FIELD_MAP.get("thresholdValue", "thresholdValue")
    new_availability = compute_availability(new_qty, current.data.get(thr_key, 0))
    
    db.table(settings.PRODUCTS_TABLE).update({
        "quantity": new_qty,
        "availability": new_availability,
        _PRODUCT_DB_FIELD_MAP.get("updatedAt", "updatedAt"): now
    }).eq("id", adjustment.productId).execute()
    
    history_entry = {
        "id": f"evt_{int(datetime.utcnow().timestamp())}",
        "productid": adjustment.productId,
        "at": now,
        "delta": adjustment.delta,
        "reason": adjustment.reason or "Stock adjustment"
    }
    db.table(settings.STOCK_HISTORY_TABLE).insert(history_entry).execute()
    
    return {"status": "success", "new_quantity": new_qty}

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    db = get_db()
    db.table(settings.PRODUCTS_TABLE).delete().eq("id", product_id).execute()
    return {"status": "deleted"}

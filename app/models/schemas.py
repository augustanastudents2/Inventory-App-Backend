"""
 * Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "Admin"
    STAFF = "Staff"


class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    role: UserRole = Field(default=UserRole.STAFF)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime


class TagBase(BaseModel):
    name: str


class TagResponse(TagBase):
    id: int
    created_at: datetime


class StorageLocationBase(BaseModel):
    area: str
    sub: Optional[str] = None


class StorageLocationResponse(StorageLocationBase):
    id: int
    created_at: datetime


class VendorBase(BaseModel):
    name: str
    contact: Optional[str] = None


class VendorResponse(VendorBase):
    id: int
    created_at: datetime


class ProductAvailability(str, Enum):
    IN_STOCK = "In-stock"
    LOW_STOCK = "Low stock"
    OUT_OF_STOCK = "Out of stock"


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = ""
    buyingPrice: float = 0.0
    quantity: int = 0
    unit: str = "Units"
    thresholdValue: int = 0
    expiryDate: Optional[str] = ""
    category: Optional[str] = ""
    tags: List[str] = []
    vendor: Dict[str, Any] = {"name": "", "contact": ""}
    storage: Dict[str, Any] = {"area": "", "sub": ""}
    availability: Optional[ProductAvailability] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    buyingPrice: Optional[float] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    thresholdValue: Optional[int] = None
    expiryDate: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    vendor: Optional[Dict[str, Any]] = None
    storage: Optional[Dict[str, Any]] = None
    availability: Optional[ProductAvailability] = None


class StockHistoryEvent(BaseModel):
    id: str
    at: datetime
    delta: int
    reason: str


class ProductResponse(ProductBase):
    id: str
    createdAt: datetime
    updatedAt: datetime
    stockHistory: List[StockHistoryEvent] = []
    
    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    productId: str
    delta: int
    reason: Optional[str] = ""


class LoginRequest(BaseModel):
    email: str
    password: str

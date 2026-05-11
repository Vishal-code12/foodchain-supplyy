from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    password_hash: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Crop:
    id: int
    farmer_id: int
    current_owner_id: int
    name: str
    description: Optional[str] = None
    quantity: float = 0.0
    unit: str = 'kg'
    price_per_unit: float = 0.0
    image_path: Optional[str] = None
    category: str = 'vegetables'
    status: str = 'available'
    harvest_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    location: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Transaction:
    id: int
    crop_id: int
    from_user_id: int
    to_user_id: int
    transaction_type: str
    quantity: float
    price: float
    timestamp: datetime
    block_hash: str
    previous_hash: str
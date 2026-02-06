from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any


class BusinessProfileBase(BaseModel):
    business_name: str
    website: str | None = None
    industry: str | None = None
    problems_solving: List[str] | None = None
    target_customers: List[str] | None = None
    products: List[str] | None = None
    customer_stages: List[str] | None = None
    trigger_events: List[str] | None = None


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileUpdate(BaseModel):
    business_name: str | None = None
    website: str | None = None
    industry: str | None = None
    problems_solving: List[str] | None = None
    target_customers: List[str] | None = None
    products: List[str] | None = None
    customer_stages: List[str] | None = None
    trigger_events: List[str] | None = None


class BusinessProfileResponse(BusinessProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

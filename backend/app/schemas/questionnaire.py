from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any


class QuestionnaireBase(BaseModel):
    business_profile_id: UUID
    client_name: str | None = None
    product_description: str | None = None
    problem_statement: str | None = None
    competitive_differentiation: str | None = None
    competitors: List[str] | None = None
    target_icp: str | None = None
    marketing_channels: List[str] | None = None
    business_objectives: str | None = None
    budget_range: str | None = None
    timeline: str | None = None


class QuestionnaireCreate(QuestionnaireBase):
    pass


class QuestionnaireUpdate(BaseModel):
    client_name: str | None = None
    product_description: str | None = None
    problem_statement: str | None = None
    competitive_differentiation: str | None = None
    competitors: List[str] | None = None
    target_icp: str | None = None
    marketing_channels: List[str] | None = None
    business_objectives: str | None = None
    budget_range: str | None = None
    timeline: str | None = None


class QuestionnaireResponse(QuestionnaireBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

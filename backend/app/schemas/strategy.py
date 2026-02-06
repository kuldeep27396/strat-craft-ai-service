from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Dict, Any


class StrategyGenerate(BaseModel):
    questionnaire_id: UUID


class StrategyResponse(BaseModel):
    id: UUID
    questionnaire_id: UUID
    strategy_content: Dict[str, Any] | None = None
    status: str
    generation_metadata: Dict[str, Any] | None = None
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StrategyUpdate(BaseModel):
    strategy_content: Dict[str, Any]

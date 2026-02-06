from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Questionnaire(Base):
    __tablename__ = "questionnaires"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_profile_id = Column(UUID(as_uuid=True), ForeignKey("business_profiles.id", ondelete="CASCADE"), nullable=False)
    client_name = Column(String(255))
    
    # Questionnaire responses
    product_description = Column(Text)
    problem_statement = Column(Text)
    competitive_differentiation = Column(Text)
    competitors = Column(JSON)  # Array of competitor URLs
    target_icp = Column(JSON)  # ICP details
    marketing_channels = Column(JSON)  # Preferred channels
    business_objectives = Column(JSON)  # Goals + metrics
    budget_range = Column(String(50))
    timeline = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_name = Column(String(255), nullable=False)
    website = Column(String(255))
    industry = Column(String(100))
    
    # Core sections from Common Input (stored as JSONB)
    problems_solving = Column(JSON)  # Array of main problems
    target_customers = Column(JSON)  # Customer segments
    products = Column(JSON)  # Product portfolio
    customer_stages = Column(JSON)  # Lifecycle stages
    trigger_events = Column(JSON)  # Trigger events
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # user = relationship("User", back_populates="business_profiles")

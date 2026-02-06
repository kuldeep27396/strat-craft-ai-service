from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    questionnaire_id = Column(UUID(as_uuid=True), ForeignKey("questionnaires.id", ondelete="CASCADE"), nullable=False)
    
    # Generated content (structured JSON)
    strategy_content = Column(JSON)  # Full strategy structure
    
    # Metadata
    status = Column(String(50), default="generating")  # 'generating', 'completed', 'failed'
    generation_metadata = Column(JSON)  # AI model, tokens used, duration
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

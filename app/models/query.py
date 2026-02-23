from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable = True)
    status = Column(String, default = "PENDING")
    latency_ms = Column(Integer, nullable = True )
    created_at = Column(DateTime(timezone=True), server_default = func.now())
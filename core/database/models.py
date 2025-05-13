from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class LearnedInfo(Base):
    __tablename__ = "learned_info"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    content = Column(Text)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APIRequest(Base):
    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String, index=True)
    url = Column(String, index=True)
    headers = Column(Text, nullable=True)  # Storing as JSON string or similar
    body = Column(Text, nullable=True)     # Storing as JSON string or similar
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True) # For AI-generated notes or analysis

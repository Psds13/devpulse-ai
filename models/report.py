from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.config import Base

class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"))
    commit_sha = Column(String, index=True)
    issues_found = Column(JSON) # Store issues as JSON
    ai_suggestions = Column(JSON)
    quality_score = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    repository = relationship("Repository")

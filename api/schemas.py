from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

class RepoCreate(BaseModel):
    url: str

class RepoResponse(BaseModel):
    id: int
    name: str
    owner: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    repository_id: int

class ReportResponse(BaseModel):
    id: int
    repository_id: int
    commit_sha: str
    issues_found: List[Dict[str, Any]]
    ai_suggestions: Dict[str, Any]
    quality_score: int
    created_at: datetime

    class Config:
        from_attributes = True

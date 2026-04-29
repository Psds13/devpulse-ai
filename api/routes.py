from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from database.config import get_db
from models.repository import Repository
from models.report import AnalysisReport
from api import schemas
from services.github import GitHubService
from services.report import ReportGenerator

router = APIRouter()

@router.post("/repo", response_model=schemas.RepoResponse)
def register_repository(repo_in: schemas.RepoCreate, db: Session = Depends(get_db)):
    """ Register a new GitHub repository to monitor. """
    github = GitHubService()
    try:
        owner, name = github.parse_repo_url(repo_in.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    existing = db.query(Repository).filter(Repository.url == repo_in.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repository already registered")
        
    repo = Repository(name=name, owner=owner, url=repo_in.url)
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo

@router.get("/repo", response_model=List[schemas.RepoResponse])
def list_repositories(db: Session = Depends(get_db)):
    """ List all monitored repositories. """
    return db.query(Repository).all()

@router.post("/analyze")
async def run_manual_analysis(req: schemas.AnalyzeRequest, db: Session = Depends(get_db)):
    """ Trigger an analysis manually on a specific repository. """
    generator = ReportGenerator(db)
    try:
        report = await generator.run_analysis(req.repository_id)
        return {"message": "Analysis completed", "report_id": report.id, "score": report.quality_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{report_id}", response_model=schemas.ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """ Fetch a specific analysis report by ID. """
    report = db.query(AnalysisReport).filter(AnalysisReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

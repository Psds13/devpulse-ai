from sqlalchemy.orm import Session
from models.repository import Repository
from models.report import AnalysisReport
from services.github import GitHubService
from services.analyzer import CodeAnalyzer
from services.ai import AIService
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.github = GitHubService()
        self.analyzer = CodeAnalyzer()
        self.ai = AIService()

    async def run_analysis(self, repository_id: int) -> AnalysisReport:
        logger.info(f"Starting analysis for repo_id {repository_id}")
        repo = self.db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            raise ValueError(f"Repository with id {repository_id} not found")

        commits = await self.github.get_recent_commits(repo.owner, repo.name)
        if not commits:
            raise ValueError("No commits found or could not fetch commits")
            
        latest_commit_sha = commits[0]["sha"]
        
        # Check if we already analyzed this commit
        existing_report = self.db.query(AnalysisReport).filter(
            AnalysisReport.repository_id == repository_id, 
            AnalysisReport.commit_sha == latest_commit_sha
        ).first()
        
        if existing_report:
            logger.info("Already analyzed latest commit.")
            return existing_report

        commit_details = await self.github.get_commit_details(repo.owner, repo.name, latest_commit_sha)
        files = commit_details.get("files", [])
        
        all_issues = []
        all_suggestions = {}
        
        for file in files:
            filename = file.get("filename")
            patch = file.get("patch", "")
            
            # Code Analysis
            issues = self.analyzer.analyze_diff(patch, filename)
            all_issues.extend(issues)
            
            # AI Suggestions
            suggestions = await self.ai.get_suggestions(filename, patch, issues)
            all_suggestions.update(suggestions)
            
        # Calculate a basic quality score (100 - base penalty)
        score = max(0, 100 - (len(all_issues) * 10))
        
        report = AnalysisReport(
            repository_id=repo.id,
            commit_sha=latest_commit_sha,
            issues_found=all_issues,
            ai_suggestions=all_suggestions,
            quality_score=score
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"Analysis completed for {repo.name}. Score: {score}")
        return report

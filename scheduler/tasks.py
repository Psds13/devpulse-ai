from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database.config import SessionLocal
from models.repository import Repository
from services.report import ReportGenerator
from utils.logger import setup_logger
import asyncio

logger = setup_logger(__name__)

scheduler = AsyncIOScheduler()

async def run_automated_analysis():
    logger.info("Running automated analysis task for all repositories...")
    db = SessionLocal()
    try:
        repos = db.query(Repository).all()
        for repo in repos:
            gen = ReportGenerator(db)
            try:
                await gen.run_analysis(repo.id)
            except Exception as e:
                logger.error(f"Automated analysis failed for repo {repo.name}: {e}")
    finally:
        db.close()

def start_scheduler():
    # Setting an interval of 30 minutes, easily configurable
    scheduler.add_job(
        run_automated_analysis, 
        trigger=IntervalTrigger(minutes=30),
        id='auto_analysis_job',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started.")

from app.services.job_stores import JobStore
from fastapi import APIRouter, BackgroundTasks
from app.models.recommendation import RecommendationRequest, JobStatus
from app.services.recommendation_engine import generate_recommendations
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/recommendations/start")
async def start_recommendations(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks
):
    job_id = str(uuid.uuid4())
    JobStore.create_job(job_id)

    logger.info(f"Starting job {job_id}")
    
    background_tasks.add_task(
        generate_recommendations,
        job_id,
        request.ratings,
        request.algorithm
    )
    
    return {"jobId": job_id}

@router.get("/recommendations/status/{job_id}")
async def get_job_status(job_id: str):
    job = JobStore.get_job(job_id)
    if not job:
        return JobStatus(status="failed", error="Job not found")
    return job
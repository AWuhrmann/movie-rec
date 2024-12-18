from typing import Optional
from app.services.job_stores import JobStore
from fastapi import APIRouter
from app.models.recommendation import MovieRequest, RecommendationRequest, JobStatus
from app.services.recommendation_engine import check_if_in, find_movie, generate_recommendations
import uuid
import logging
from asyncio import create_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/recommendations/start")
async def start_recommendations(
    request: RecommendationRequest,
):
    job_id = str(uuid.uuid4())
    await JobStore.create_job(job_id)

    logger.info(f"Starting job {job_id}")
    
    create_task(
        generate_recommendations(
            job_id,
            request.ratings,
            request.algorithm,
            request.params)
    )
    
    return {"jobId": job_id}

@router.get("/recommendations/status/{job_id}")
async def get_job_status(job_id: str):
    print(job_id)
    job = await JobStore.get_job(job_id)
    print(job)
    if not job:
        return JobStatus(status="failed", error="Job not found")
    return job

@router.post('/movies/check')
async def is_in_our_db(
    request: MovieRequest,
    ):
    job_id = str(uuid.uuid4())
    await JobStore.create_job(job_id)

    logger.info(f'Starting job {job_id}')

    create_task(
        check_if_in,
        job_id,
        request.movies
    )

    return {"jobId": job_id}

@router.get('/movies/find/{query}')
async def findMovie(
    query: str,
    ):

    results = await find_movie(query, 80)

    return results


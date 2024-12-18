from typing import Dict, Optional
from app.models.recommendation import JobStatus
import asyncio

class JobStore:
    _jobs: Dict[str, JobStatus] = {}
    _lock = asyncio.Lock()  # Add lock for thread-safety

    @classmethod
    async def create_job(cls, job_id: str):
        async with cls._lock:
            cls._jobs[job_id] = JobStatus(status="pending")

    @classmethod
    async def update_job(cls, job_id: str, status: JobStatus):
        async with cls._lock:
            cls._jobs[job_id] = status

    @classmethod
    async def get_job(cls, job_id: str) -> Optional[JobStatus]:
        async with cls._lock:
            return cls._jobs.get(job_id)
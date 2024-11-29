from typing import Dict, Optional
from app.models.recommendation import JobStatus

class JobStore:
    _jobs: Dict[str, JobStatus] = {}

    @classmethod
    def create_job(cls, job_id: str):
        cls._jobs[job_id] = JobStatus(status="pending")

    @classmethod
    def update_job(cls, job_id: str, status: JobStatus):
        cls._jobs[job_id] = status

    @classmethod
    def get_job(cls, job_id: str) -> Optional[JobStatus]:
        return cls._jobs.get(job_id)


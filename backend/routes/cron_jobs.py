from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import CronJob
from database import cron_jobs

router = APIRouter(prefix="/api/cron-jobs", tags=["cron-jobs"])

@router.post("", response_model=CronJob)
async def create_cron_job(job: CronJob):
    cron_jobs[job.id] = job
    return job

@router.get("", response_model=List[CronJob])
async def get_cron_jobs(client_id: Optional[str] = None):
    if client_id:
        return [j for j in cron_jobs.values() if j.clientId == client_id]
    return list(cron_jobs.values())

@router.put("/{job_id}", response_model=CronJob)
async def update_cron_job(job_id: str, job: CronJob):
    if job_id not in cron_jobs:
        raise HTTPException(status_code=404, detail="Cron job not found")
    cron_jobs[job_id] = job
    return job

@router.delete("/{job_id}")
async def delete_cron_job(job_id: str):
    if job_id not in cron_jobs:
        raise HTTPException(status_code=404, detail="Cron job not found")
    del cron_jobs[job_id]
    return {"message": "Cron job deleted successfully"}

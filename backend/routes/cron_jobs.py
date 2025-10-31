from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import CronJob
from database import db

router = APIRouter(prefix="/api/cron-jobs", tags=["cron-jobs"])

@router.post("", response_model=CronJob)
async def create_cron_job(job: CronJob):
    return await db.create_cron_job(job)

@router.get("", response_model=List[CronJob])
async def get_cron_jobs(client_id: Optional[str] = None):
    return await db.get_all_cron_jobs(client_id)

@router.put("/{job_id}", response_model=CronJob)
async def update_cron_job(job_id: str, job: CronJob):
    existing = await db.get_all_cron_jobs()
    if not any(j.id == job_id for j in existing):
        raise HTTPException(status_code=404, detail="Cron job not found")
    return await db.update_cron_job(job_id, job)

@router.delete("/{job_id}")
async def delete_cron_job(job_id: str):
    success = await db.delete_cron_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cron job not found")
    return {"message": "Cron job deleted successfully"}

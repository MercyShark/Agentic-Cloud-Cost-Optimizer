from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import Recommendation
from database import db

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("", response_model=List[Recommendation])
async def get_recommendations(client_id: Optional[str] = None):
    return await db.get_all_recommendations(client_id)

@router.get("/{rec_id}", response_model=Recommendation)
async def get_recommendation(rec_id: str):
    recommendation = await db.get_recommendation(rec_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation

@router.put("/{rec_id}/status")
async def update_recommendation_status(rec_id: str, status: str):
    success = await db.update_recommendation_status(rec_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"message": "Status updated successfully"}

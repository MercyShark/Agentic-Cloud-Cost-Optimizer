from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import Recommendation
from database import recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("", response_model=List[Recommendation])
async def get_recommendations(client_id: Optional[str] = None):
    if client_id:
        return [r for r in recommendations.values() if r.clientId == client_id]
    return list(recommendations.values())

@router.get("/{rec_id}", response_model=Recommendation)
async def get_recommendation(rec_id: str):
    if rec_id not in recommendations:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendations[rec_id]

@router.put("/{rec_id}/status")
async def update_recommendation_status(rec_id: str, status: str):
    if rec_id not in recommendations:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    recommendations[rec_id].status = status
    return {"message": "Status updated successfully"}

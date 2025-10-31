from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import Alert
from database import db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("", response_model=List[Alert])
async def get_alerts(client_id: Optional[str] = None):
    return await db.get_all_alerts(client_id)

@router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    success = await db.mark_alert_read(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert marked as read"}

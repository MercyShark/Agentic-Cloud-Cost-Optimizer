from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models import Alert
from database import alerts

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("", response_model=List[Alert])
async def get_alerts(client_id: Optional[str] = None):
    if client_id:
        return [a for a in alerts.values() if a.clientId == client_id]
    return list(alerts.values())

@router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    if alert_id not in alerts:
        raise HTTPException(status_code=404, detail="Alert not found")
    alerts[alert_id].isRead = True
    return {"message": "Alert marked as read"}

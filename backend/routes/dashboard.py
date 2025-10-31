from fastapi import APIRouter
from typing import Optional
from database import db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(client_id: Optional[str] = None):
    clients = await db.get_all_clients()
    client_recs = await db.get_all_recommendations(client_id)
    client_alerts = await db.get_all_alerts(client_id)
    
    total_savings = sum(r.monthlySavings for r in client_recs)
    
    return {
        "totalClients": len(clients),
        "activeRecommendations": len([r for r in client_recs if r.status == "pending"]),
        "potentialSavings": total_savings,
        "activeAlerts": len([a for a in client_alerts if not a.isRead]),
        "totalResources": sum(c.totalResources for c in clients),
        "monthlyCost": sum(c.monthlyCost for c in clients)
    }

from fastapi import APIRouter
from typing import Optional
from database import cloud_clients, recommendations, alerts

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(client_id: Optional[str] = None):
    client_recs = [r for r in recommendations.values() if not client_id or r.clientId == client_id]
    client_alerts = [a for a in alerts.values() if not client_id or a.clientId == client_id]
    
    total_savings = sum(r.monthlySavings for r in client_recs)
    
    return {
        "totalClients": len(cloud_clients),
        "activeRecommendations": len([r for r in client_recs if r.status == "pending"]),
        "potentialSavings": total_savings,
        "activeAlerts": len([a for a in client_alerts if not a.isRead]),
        "totalResources": sum(c.totalResources for c in cloud_clients.values()),
        "monthlyCost": sum(c.monthlyCost for c in cloud_clients.values())
    }

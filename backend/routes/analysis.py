from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from bedrock_agent import BedrockOptimizationAgent
from models import AnalysisRequest, Recommendation
from database import cloud_clients, analysis_results, recommendations

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/analyze")
async def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
    if request.clientId not in cloud_clients:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = cloud_clients[request.clientId]
    
    try:
        agent = BedrockOptimizationAgent(
            role_arn=client.roleArn or "",
            region=client.region,
            bedrock_region=client.region,
            profile_name="sova-profile"
        )
        
        result = agent.analyze(request.query)
        
        analysis_id = f"analysis_{datetime.utcnow().timestamp()}"
        analysis_results[analysis_id] = {
            "id": analysis_id,
            "clientId": request.clientId,
            "query": request.query,
            "result": result,
            "timestamp": datetime.utcnow()
        }
        
        if result.get("status") == "success":
            analysis_text = result.get("analysis", "")
            
            rec_id = f"rec_{datetime.utcnow().timestamp()}"
            recommendations[rec_id] = Recommendation(
                id=rec_id,
                clientId=request.clientId,
                title="Cost Optimization Recommendations",
                description=analysis_text[:500],
                category="cost_optimization",
                impact="high",
                monthlySavings=0.0,
                status="pending",
                createdAt=datetime.utcnow()
            )
        
        return {
            "analysisId": analysis_id,
            "status": result.get("status"),
            "message": "Analysis completed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis_results[analysis_id]

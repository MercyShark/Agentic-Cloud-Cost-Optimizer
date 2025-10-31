from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from bedrock_agent import BedrockOptimizationAgent
from models import AnalysisRequest, Recommendation
from database import db

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/analyze")
async def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
    client = await db.get_client(request.clientId)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        agent = BedrockOptimizationAgent(
            role_arn=client.roleArn or "",
            region=client.region,
            bedrock_region=client.region,
            profile_name="sova-profile"
        )
        
        result = agent.analyze(request.query)
        
        analysis_id = f"analysis_{datetime.utcnow().timestamp()}"
        analysis_data = {
            "id": analysis_id,
            "clientId": request.clientId,
            "query": request.query,
            "result": result,
            "timestamp": datetime.utcnow()
        }
        
        await db.create_analysis_result(analysis_id, analysis_data)
        
        if result.get("status") == "success":
            analysis_text = result.get("analysis", "")
            
            rec_id = f"rec_{datetime.utcnow().timestamp()}"
            recommendation = Recommendation(
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
            await db.create_recommendation(recommendation)
        
        return {
            "analysisId": analysis_id,
            "status": result.get("status"),
            "message": "Analysis completed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    result = await db.get_analysis_result(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from routes import clients, analysis, recommendations, alerts, cron_jobs, dashboard

app = FastAPI(title="Cloud Cost Optimizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(analysis.router)
app.include_router(recommendations.router)
app.include_router(alerts.router)
app.include_router(cron_jobs.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "Cloud Cost Optimizer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

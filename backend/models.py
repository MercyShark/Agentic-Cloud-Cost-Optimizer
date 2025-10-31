from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

class CloudClient(BaseModel):
    id: str
    name: str
    provider: CloudProvider
    region: str
    roleArn: Optional[str] = None
    accessKeyId: Optional[str] = None
    secretAccessKey: Optional[str] = None
    isActive: bool = True
    lastSync: Optional[datetime] = None
    totalResources: int = 0
    monthlyCost: float = 0.0

class AnalysisRequest(BaseModel):
    query: str
    clientId: str

class CronJob(BaseModel):
    id: str
    name: str
    schedule: str
    query: str
    clientId: str
    isActive: bool = True
    lastRun: Optional[datetime] = None
    nextRun: Optional[datetime] = None

class Recommendation(BaseModel):
    id: str
    clientId: str
    title: str
    description: str
    category: str
    impact: str
    monthlySavings: float
    status: str = "pending"
    createdAt: datetime

class Alert(BaseModel):
    id: str
    clientId: str
    title: str
    message: str
    severity: str
    isRead: bool = False
    createdAt: datetime

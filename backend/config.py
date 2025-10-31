import os

AWS_PROFILE = os.getenv("AWS_PROFILE", "sova-profile")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

DYNAMODB_TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "superops")

DYNAMODB_TABLES = {
    "clients": f"{DYNAMODB_TABLE_PREFIX}_cloud_clients",
    "recommendations": f"{DYNAMODB_TABLE_PREFIX}_recommendations",
    "alerts": f"{DYNAMODB_TABLE_PREFIX}_alerts",
    "cron_jobs": f"{DYNAMODB_TABLE_PREFIX}_cron_jobs",
    "analysis_results": f"{DYNAMODB_TABLE_PREFIX}_analysis_results",
}

API_TITLE = "Cloud Cost Optimizer API"
API_VERSION = "1.0.0"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

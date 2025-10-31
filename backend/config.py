import os

AWS_PROFILE = os.getenv("AWS_PROFILE", "sova-profile")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

API_TITLE = "Cloud Cost Optimizer API"
API_VERSION = "1.0.0"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

from typing import Dict, Any
from models import CloudClient, Recommendation, Alert, CronJob

cloud_clients: Dict[str, CloudClient] = {}
recommendations: Dict[str, Recommendation] = {}
alerts: Dict[str, Alert] = {}
cron_jobs: Dict[str, CronJob] = {}
analysis_results: Dict[str, Any] = {}

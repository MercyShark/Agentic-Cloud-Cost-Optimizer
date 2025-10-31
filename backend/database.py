import boto3
from botocore.exceptions import ClientError
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import json
from models import CloudClient, Recommendation, Alert, CronJob
from config import AWS_REGION, AWS_PROFILE, DYNAMODB_TABLES

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

class DynamoDBDatabase:
    def __init__(self):
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        self.dynamodb = session.resource('dynamodb')
        self.tables = {
            'clients': self.dynamodb.Table(DYNAMODB_TABLES['clients']),
            'recommendations': self.dynamodb.Table(DYNAMODB_TABLES['recommendations']),
            'alerts': self.dynamodb.Table(DYNAMODB_TABLES['alerts']),
            'cron_jobs': self.dynamodb.Table(DYNAMODB_TABLES['cron_jobs']),
            'analysis_results': self.dynamodb.Table(DYNAMODB_TABLES['analysis_results']),
        }
    
    def _convert_floats_to_decimal(self, obj):
        if isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        elif isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    def _convert_decimals_to_float(self, obj):
        if isinstance(obj, dict):
            return {k: self._convert_decimals_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimals_to_float(item) for item in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
    
    async def create_client(self, client: CloudClient) -> CloudClient:
        item = self._convert_floats_to_decimal(client.model_dump())
        self.tables['clients'].put_item(Item=item)
        return client
    
    async def get_client(self, client_id: str) -> Optional[CloudClient]:
        try:
            response = self.tables['clients'].get_item(Key={'id': client_id})
            if 'Item' in response:
                item = self._convert_decimals_to_float(response['Item'])
                return CloudClient(**item)
            return None
        except ClientError:
            return None
    
    async def get_all_clients(self) -> List[CloudClient]:
        try:
            response = self.tables['clients'].scan()
            items = self._convert_decimals_to_float(response.get('Items', []))
            return [CloudClient(**item) for item in items]
        except ClientError:
            return []
    
    async def update_client(self, client_id: str, client: CloudClient) -> CloudClient:
        item = self._convert_floats_to_decimal(client.model_dump())
        self.tables['clients'].put_item(Item=item)
        return client
    
    async def delete_client(self, client_id: str) -> bool:
        try:
            self.tables['clients'].delete_item(Key={'id': client_id})
            return True
        except ClientError:
            return False
    
    async def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        item = self._convert_floats_to_decimal(recommendation.model_dump())
        self.tables['recommendations'].put_item(Item=item)
        return recommendation
    
    async def get_recommendation(self, rec_id: str) -> Optional[Recommendation]:
        try:
            response = self.tables['recommendations'].get_item(Key={'id': rec_id})
            if 'Item' in response:
                item = self._convert_decimals_to_float(response['Item'])
                return Recommendation(**item)
            return None
        except ClientError:
            return None
    
    async def get_all_recommendations(self, client_id: Optional[str] = None) -> List[Recommendation]:
        try:
            if client_id:
                response = self.tables['recommendations'].scan(
                    FilterExpression='clientId = :client_id',
                    ExpressionAttributeValues={':client_id': client_id}
                )
            else:
                response = self.tables['recommendations'].scan()
            items = self._convert_decimals_to_float(response.get('Items', []))
            return [Recommendation(**item) for item in items]
        except ClientError:
            return []
    
    async def update_recommendation(self, rec_id: str, recommendation: Recommendation) -> Recommendation:
        item = self._convert_floats_to_decimal(recommendation.model_dump())
        self.tables['recommendations'].put_item(Item=item)
        return recommendation
    
    async def update_recommendation_status(self, rec_id: str, status: str) -> bool:
        try:
            self.tables['recommendations'].update_item(
                Key={'id': rec_id},
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status}
            )
            return True
        except ClientError:
            return False
    
    async def create_alert(self, alert: Alert) -> Alert:
        item = self._convert_floats_to_decimal(alert.model_dump())
        self.tables['alerts'].put_item(Item=item)
        return alert
    
    async def get_all_alerts(self, client_id: Optional[str] = None) -> List[Alert]:
        try:
            if client_id:
                response = self.tables['alerts'].scan(
                    FilterExpression='clientId = :client_id',
                    ExpressionAttributeValues={':client_id': client_id}
                )
            else:
                response = self.tables['alerts'].scan()
            items = self._convert_decimals_to_float(response.get('Items', []))
            return [Alert(**item) for item in items]
        except ClientError:
            return []
    
    async def mark_alert_read(self, alert_id: str) -> bool:
        try:
            self.tables['alerts'].update_item(
                Key={'id': alert_id},
                UpdateExpression='SET isRead = :read',
                ExpressionAttributeValues={':read': True}
            )
            return True
        except ClientError:
            return False
    
    async def create_cron_job(self, job: CronJob) -> CronJob:
        item = self._convert_floats_to_decimal(job.model_dump())
        self.tables['cron_jobs'].put_item(Item=item)
        return job
    
    async def get_all_cron_jobs(self, client_id: Optional[str] = None) -> List[CronJob]:
        try:
            if client_id:
                response = self.tables['cron_jobs'].scan(
                    FilterExpression='clientId = :client_id',
                    ExpressionAttributeValues={':client_id': client_id}
                )
            else:
                response = self.tables['cron_jobs'].scan()
            items = self._convert_decimals_to_float(response.get('Items', []))
            return [CronJob(**item) for item in items]
        except ClientError:
            return []
    
    async def update_cron_job(self, job_id: str, job: CronJob) -> CronJob:
        item = self._convert_floats_to_decimal(job.model_dump())
        self.tables['cron_jobs'].put_item(Item=item)
        return job
    
    async def delete_cron_job(self, job_id: str) -> bool:
        try:
            self.tables['cron_jobs'].delete_item(Key={'id': job_id})
            return True
        except ClientError:
            return False
    
    async def create_analysis_result(self, analysis_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        item = self._convert_floats_to_decimal(data)
        item['id'] = analysis_id
        self.tables['analysis_results'].put_item(Item=item)
        return data
    
    async def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.tables['analysis_results'].get_item(Key={'id': analysis_id})
            if 'Item' in response:
                return self._convert_decimals_to_float(response['Item'])
            return None
        except ClientError:
            return None

db = DynamoDBDatabase()

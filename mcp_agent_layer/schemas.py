from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
class RoleArnRequest(BaseModel):
    role_arn: str = Field(..., description="AWS IAM Role ARN to assume")
class EC2InstancesRequest(RoleArnRequest):
    region: str = Field(default="us-east-1", description="AWS region")
class MetricStatisticsRequest(RoleArnRequest):
    namespace: str = Field(..., description="CloudWatch namespace")
    metric_name: str = Field(..., description="Metric name")
    dimensions: List[Dict[str, str]] = Field(..., description="Metric dimensions")
    start_hours_ago: int = Field(default=24, ge=1, le=2160, description="Hours of history")
    period: int = Field(default=3600, ge=60, description="Period in seconds")
    statistics: List[str] = Field(default=["Average", "Maximum", "Minimum"])
    region: str = Field(default="us-east-1")
class CostAndUsageRequest(RoleArnRequest):
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    granularity: str = Field(default="DAILY", description="DAILY, MONTHLY, or HOURLY")
    metrics: List[str] = Field(default=["UnblendedCost", "UsageQuantity"])
    group_by: Optional[List[Dict[str, str]]] = None
class StandardResponse(BaseModel):
    account_id: str
    region: str
    data_type: str
    timestamp: str
    status: str
    data: Any
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    recoverable: Optional[bool] = None
class EC2Instance(BaseModel):
    instance_id: str
    instance_type: str
    state: str
    launch_time: Optional[str]
    availability_zone: Optional[str]
    private_ip: Optional[str]
    public_ip: Optional[str]
    vpc_id: Optional[str]
    subnet_id: Optional[str]
    tags: Dict[str, str]
    platform: str
    monitoring: Optional[str]
class RDSInstance(BaseModel):
    db_instance_identifier: str
    db_instance_class: str
    engine: str
    engine_version: str
    db_instance_status: str
    allocated_storage: int
    storage_type: str
    multi_az: bool
    availability_zone: Optional[str]
    endpoint: Optional[str]
    port: Optional[int]
class LambdaFunction(BaseModel):
    function_name: str
    function_arn: str
    runtime: str
    handler: str
    code_size: int
    timeout: int
    memory_size: int
    last_modified: str
class S3Bucket(BaseModel):
    name: str
    creation_date: str
    region: str
    versioning: str
    encryption: str
    lifecycle_rules: int
class MetricDataPoint(BaseModel):
    Timestamp: str
    Average: Optional[float] = None
    Maximum: Optional[float] = None
    Minimum: Optional[float] = None
    Sum: Optional[float] = None
    SampleCount: Optional[float] = None
    Unit: Optional[str] = None

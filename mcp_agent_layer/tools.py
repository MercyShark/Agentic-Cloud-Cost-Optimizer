import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import time
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from fastapi import FastAPI
from fastmcp import FastMCP
from dateutil.relativedelta import relativedelta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="AWS Optimization Tools",
    description="Read-only AWS data exposure for AI-driven cost optimization",
    version="1.0.0"
)
mcp = FastMCP("aws-optimization-tools")
def assume_role_session(role_arn: str, session_name: str = "MCPSession") -> boto3.Session:
    try:
        sts_client = boto3.client('sts')
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            DurationSeconds=3600
        )
        credentials = response['Credentials']
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        logger.info(f"Successfully assumed role: {role_arn}")
        return session
    except ClientError as e:
        logger.error(f"Failed to assume role {role_arn}: {str(e)}")
        raise Exception(f"Role assumption failed: {str(e)}")
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    if error_code in ['ThrottlingException', 'RequestLimitExceeded', 'TooManyRequestsException']:
                        retries += 1
                        if retries >= max_retries:
                            logger.error(f"Max retries reached for {func.__name__}")
                            raise
                        delay = base_delay * (2 ** retries)
                        logger.warning(f"Throttled. Retrying in {delay}s... (Attempt {retries}/{max_retries})")
                        time.sleep(delay)
                    else:
                        raise
            return func(*args, **kwargs)
        return wrapper
    return decorator
def safe_call(func, *args, **kwargs) -> Dict[str, Any]:
    try:
        result = func(*args, **kwargs)
        return {
            "status": "success",
            "data": result
        }
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"AWS ClientError in {func.__name__}: {error_code} - {error_message}")
        return {
            "status": "error",
            "error_code": error_code,
            "error_message": error_message,
            "recoverable": error_code in ['AccessDenied', 'UnauthorizedOperation']
        }
    except Exception as e:
        logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
        return {
            "status": "error",
            "error_code": "UnexpectedError",
            "error_message": str(e),
            "recoverable": False
        }
def paginate_results(client, method_name: str, result_key: str, **kwargs) -> List[Dict]:
    results = []
    try:
        if hasattr(client, 'get_paginator'):
            try:
                paginator = client.get_paginator(method_name)
                page_iterator = paginator.paginate(**kwargs)
                for page in page_iterator:
                    if result_key in page:
                        results.extend(page[result_key])
            except Exception:
                method = getattr(client, method_name)
                response = method(**kwargs)
                if result_key in response:
                    results.extend(response[result_key])
                while 'NextToken' in response or 'NextMarker' in response:
                    next_token = response.get('NextToken') or response.get('NextMarker')
                    kwargs['NextToken' if 'NextToken' in response else 'Marker'] = next_token
                    response = method(**kwargs)
                    if result_key in response:
                        results.extend(response[result_key])
        else:
            method = getattr(client, method_name)
            response = method(**kwargs)
            if result_key in response:
                results.extend(response[result_key])
    except Exception as e:
        logger.error(f"Pagination error for {method_name}: {str(e)}")
        raise
    return results
def get_account_id(session: boto3.Session) -> str:
    try:
        sts = session.client('sts')
        return sts.get_caller_identity()['Account']
    except Exception as e:
        logger.error(f"Failed to get account ID: {str(e)}")
        return "unknown"
def create_response(
    account_id: str,
    region: str,
    data_type: str,
    data: Any,
    status: str = "success",
    error_info: Optional[Dict] = None
) -> Dict[str, Any]:
    response = {
        "account_id": account_id,
        "region": region,
        "data_type": data_type,
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "data": data
    }
    if error_info:
        response.update(error_info)
    return response
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_ec2_instances(role_arn: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    ec2_client = session.client('ec2', region_name=region)
    result = safe_call(
        paginate_results,
        ec2_client,
        'describe_instances',
        'Reservations'
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "ec2_instances", [], "error", result)
    instances = []
    for reservation in result['data']:
        for instance in reservation.get('Instances', []):
            instances.append({
                'instance_id': instance.get('InstanceId'),
                'instance_type': instance.get('InstanceType'),
                'state': instance.get('State', {}).get('Name'),
                'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else None,
                'availability_zone': instance.get('Placement', {}).get('AvailabilityZone'),
                'private_ip': instance.get('PrivateIpAddress'),
                'public_ip': instance.get('PublicIpAddress'),
                'vpc_id': instance.get('VpcId'),
                'subnet_id': instance.get('SubnetId'),
                'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                'platform': instance.get('Platform', 'linux'),
                'monitoring': instance.get('Monitoring', {}).get('State'),
            })
    return create_response(account_id, region, "ec2_instances", instances)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_ec2_tags(role_arn: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    ec2_client = session.client('ec2', region_name=region)
    result = safe_call(
        paginate_results,
        ec2_client,
        'describe_tags',
        'Tags'
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "ec2_tags", [], "error", result)
    return create_response(account_id, region, "ec2_tags", result['data'])
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_rds_instances(role_arn: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    rds_client = session.client('rds', region_name=region)
    result = safe_call(
        paginate_results,
        rds_client,
        'describe_db_instances',
        'DBInstances'
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "rds_instances", [], "error", result)
    instances = []
    for db in result['data']:
        instances.append({
            'db_instance_identifier': db.get('DBInstanceIdentifier'),
            'db_instance_class': db.get('DBInstanceClass'),
            'engine': db.get('Engine'),
            'engine_version': db.get('EngineVersion'),
            'db_instance_status': db.get('DBInstanceStatus'),
            'allocated_storage': db.get('AllocatedStorage'),
            'storage_type': db.get('StorageType'),
            'multi_az': db.get('MultiAZ'),
            'availability_zone': db.get('AvailabilityZone'),
            'endpoint': db.get('Endpoint', {}).get('Address') if db.get('Endpoint') else None,
            'port': db.get('Endpoint', {}).get('Port') if db.get('Endpoint') else None,
            'instance_create_time': db.get('InstanceCreateTime').isoformat() if db.get('InstanceCreateTime') else None,
            'backup_retention_period': db.get('BackupRetentionPeriod'),
            'vpc_id': db.get('DBSubnetGroup', {}).get('VpcId') if db.get('DBSubnetGroup') else None,
            'publicly_accessible': db.get('PubliclyAccessible'),
        })
    return create_response(account_id, region, "rds_instances", instances)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_rds_clusters(role_arn: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    rds_client = session.client('rds', region_name=region)
    result = safe_call(
        paginate_results,
        rds_client,
        'describe_db_clusters',
        'DBClusters'
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "rds_clusters", [], "error", result)
    clusters = []
    for cluster in result['data']:
        clusters.append({
            'db_cluster_identifier': cluster.get('DBClusterIdentifier'),
            'engine': cluster.get('Engine'),
            'engine_version': cluster.get('EngineVersion'),
            'status': cluster.get('Status'),
            'endpoint': cluster.get('Endpoint'),
            'reader_endpoint': cluster.get('ReaderEndpoint'),
            'multi_az': cluster.get('MultiAZ'),
            'database_name': cluster.get('DatabaseName'),
            'cluster_create_time': cluster.get('ClusterCreateTime').isoformat() if cluster.get('ClusterCreateTime') else None,
            'members': [m.get('DBInstanceIdentifier') for m in cluster.get('DBClusterMembers', [])],
            'allocated_storage': cluster.get('AllocatedStorage'),
        })
    return create_response(account_id, region, "rds_clusters", clusters)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_lambda_functions(role_arn: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    lambda_client = session.client('lambda', region_name=region)
    result = safe_call(
        paginate_results,
        lambda_client,
        'list_functions',
        'Functions'
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "lambda_functions", [], "error", result)
    functions = []
    for func in result['data']:
        functions.append({
            'function_name': func.get('FunctionName'),
            'function_arn': func.get('FunctionArn'),
            'runtime': func.get('Runtime'),
            'handler': func.get('Handler'),
            'code_size': func.get('CodeSize'),
            'description': func.get('Description'),
            'timeout': func.get('Timeout'),
            'memory_size': func.get('MemorySize'),
            'last_modified': func.get('LastModified'),
            'version': func.get('Version'),
            'vpc_config': func.get('VpcConfig'),
            'environment_vars': list(func.get('Environment', {}).get('Variables', {}).keys()),
            'architectures': func.get('Architectures', []),
            'package_type': func.get('PackageType'),
        })
    return create_response(account_id, region, "lambda_functions", functions)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_lambda_function_config(role_arn: str, function_name: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    lambda_client = session.client('lambda', region_name=region)
    result = safe_call(
        lambda_client.get_function_configuration,
        FunctionName=function_name
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "lambda_function_config", {}, "error", result)
    return create_response(account_id, region, "lambda_function_config", result['data'])
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_s3_buckets(role_arn: str) -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    s3_client = session.client('s3')
    result = safe_call(s3_client.list_buckets)
    if result['status'] == 'error':
        return create_response(account_id, "global", "s3_buckets", [], "error", result)
    buckets = []
    for bucket in result['data'].get('Buckets', []):
        bucket_name = bucket['Name']
        bucket_info = {
            'name': bucket_name,
            'creation_date': bucket['CreationDate'].isoformat(),
        }
        try:
            location = s3_client.get_bucket_location(Bucket=bucket_name)
            bucket_info['region'] = location.get('LocationConstraint') or 'us-east-1'
        except Exception:
            bucket_info['region'] = 'unknown'
        try:
            versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
            bucket_info['versioning'] = versioning.get('Status', 'Disabled')
        except Exception:
            bucket_info['versioning'] = 'unknown'
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
            bucket_info['encryption'] = 'Enabled'
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                bucket_info['encryption'] = 'Disabled'
            else:
                bucket_info['encryption'] = 'unknown'
        try:
            lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            bucket_info['lifecycle_rules'] = len(lifecycle.get('Rules', []))
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                bucket_info['lifecycle_rules'] = 0
            else:
                bucket_info['lifecycle_rules'] = -1
        buckets.append(bucket_info)
    return create_response(account_id, "global", "s3_buckets", buckets)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_s3_bucket_size(role_arn: str, bucket_name: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    cloudwatch_client = session.client('cloudwatch', region_name=region)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    metrics_data = {}
    try:
        size_response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='BucketSizeBytes',
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'StandardStorage'}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=['Average']
        )
        if size_response.get('Datapoints'):
            metrics_data['size_bytes'] = size_response['Datapoints'][0]['Average']
            metrics_data['size_gb'] = round(metrics_data['size_bytes'] / (1024**3), 2)
    except Exception as e:
        logger.error(f"Error getting bucket size: {str(e)}")
        metrics_data['size_bytes'] = None
    try:
        count_response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='NumberOfObjects',
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=['Average']
        )
        if count_response.get('Datapoints'):
            metrics_data['object_count'] = int(count_response['Datapoints'][0]['Average'])
    except Exception as e:
        logger.error(f"Error getting object count: {str(e)}")
        metrics_data['object_count'] = None
    metrics_data['bucket_name'] = bucket_name
    return create_response(account_id, region, "s3_bucket_metrics", metrics_data)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_ecs_clusters(role_arn: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    ecs_client = session.client('ecs', region_name=region)
    cluster_arns_result = safe_call(
        paginate_results,
        ecs_client,
        'list_clusters',
        'clusterArns'
    )
    if cluster_arns_result['status'] == 'error':
        return create_response(account_id, region, "ecs_clusters", [], "error", cluster_arns_result)
    if not cluster_arns_result['data']:
        return create_response(account_id, region, "ecs_clusters", [])
    clusters_result = safe_call(
        ecs_client.describe_clusters,
        clusters=cluster_arns_result['data']
    )
    if clusters_result['status'] == 'error':
        return create_response(account_id, region, "ecs_clusters", [], "error", clusters_result)
    clusters = []
    for cluster in clusters_result['data'].get('clusters', []):
        clusters.append({
            'cluster_name': cluster.get('clusterName'),
            'cluster_arn': cluster.get('clusterArn'),
            'status': cluster.get('status'),
            'registered_container_instances_count': cluster.get('registeredContainerInstancesCount'),
            'running_tasks_count': cluster.get('runningTasksCount'),
            'pending_tasks_count': cluster.get('pendingTasksCount'),
            'active_services_count': cluster.get('activeServicesCount'),
        })
    return create_response(account_id, region, "ecs_clusters", clusters)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_ecs_tasks(role_arn: str, cluster_name: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    ecs_client = session.client('ecs', region_name=region)
    task_arns_result = safe_call(
        paginate_results,
        ecs_client,
        'list_tasks',
        'taskArns',
        cluster=cluster_name
    )
    if task_arns_result['status'] == 'error':
        return create_response(account_id, region, "ecs_tasks", [], "error", task_arns_result)
    if not task_arns_result['data']:
        return create_response(account_id, region, "ecs_tasks", [])
    all_tasks = []
    task_arns = task_arns_result['data']
    for i in range(0, len(task_arns), 100):
        batch = task_arns[i:i+100]
        tasks_result = safe_call(
            ecs_client.describe_tasks,
            cluster=cluster_name,
            tasks=batch
        )
        if tasks_result['status'] == 'success':
            for task in tasks_result['data'].get('tasks', []):
                all_tasks.append({
                    'task_arn': task.get('taskArn'),
                    'task_definition_arn': task.get('taskDefinitionArn'),
                    'cluster_arn': task.get('clusterArn'),
                    'last_status': task.get('lastStatus'),
                    'desired_status': task.get('desiredStatus'),
                    'cpu': task.get('cpu'),
                    'memory': task.get('memory'),
                    'created_at': task.get('createdAt').isoformat() if task.get('createdAt') else None,
                    'started_at': task.get('startedAt').isoformat() if task.get('startedAt') else None,
                    'launch_type': task.get('launchType'),
                })
    return create_response(account_id, region, "ecs_tasks", all_tasks)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_cloudwatch_metrics(role_arn: str, namespace: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    cloudwatch_client = session.client('cloudwatch', region_name=region)
    result = safe_call(
        paginate_results,
        cloudwatch_client,
        'list_metrics',
        'Metrics',
        Namespace=namespace
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "cloudwatch_metrics", [], "error", result)
    metrics = []
    for metric in result['data']:
        metrics.append({
            'namespace': metric.get('Namespace'),
            'metric_name': metric.get('MetricName'),
            'dimensions': metric.get('Dimensions', [])
        })
    return create_response(account_id, region, "cloudwatch_metrics", metrics)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_metric_statistics(
    role_arn: str,
    namespace: str,
    metric_name: str,
    dimensions: List[Dict[str, str]],
    start_hours_ago: int = 24,
    period: int = 3600,
    statistics: List[str] = None,
    region: str = "us-east-1"
) -> Dict[str, Any]:
    if statistics is None:
        statistics = ["Average", "Maximum", "Minimum"]
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    cloudwatch_client = session.client('cloudwatch', region_name=region)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=start_hours_ago)
    result = safe_call(
        cloudwatch_client.get_metric_statistics,
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start_time,
        EndTime=end_time,
        Period=period,
        Statistics=statistics
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "metric_statistics", {}, "error", result)
    datapoints = result['data'].get('Datapoints', [])
    datapoints.sort(key=lambda x: x['Timestamp'])
    for dp in datapoints:
        dp['Timestamp'] = dp['Timestamp'].isoformat()
    metric_data = {
        'namespace': namespace,
        'metric_name': metric_name,
        'dimensions': dimensions,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'period': period,
        'statistics': statistics,
        'datapoints': datapoints,
        'datapoint_count': len(datapoints)
    }
    return create_response(account_id, region, "metric_statistics", metric_data)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_ec2_cpu_utilization(
    role_arn: str,
    instance_id: str,
    start_hours_ago: int = 168,
    region: str = "us-east-1"
) -> Dict[str, Any]:
    return get_metric_statistics(
        role_arn=role_arn,
        namespace="AWS/EC2",
        metric_name="CPUUtilization",
        dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        start_hours_ago=start_hours_ago,
        period=3600,
        statistics=["Average", "Maximum", "Minimum"],
        region=region
    )
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_log_groups(role_arn: str, region: str = "us-east-1") -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    logs_client = session.client('logs', region_name=region)
    result = safe_call(
        paginate_results,
        logs_client,
        'describe_log_groups',
        'logGroups'
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "log_groups", [], "error", result)
    log_groups = []
    for lg in result['data']:
        log_groups.append({
            'log_group_name': lg.get('logGroupName'),
            'creation_time': datetime.fromtimestamp(lg.get('creationTime', 0) / 1000).isoformat(),
            'retention_in_days': lg.get('retentionInDays'),
            'stored_bytes': lg.get('storedBytes'),
            'stored_mb': round(lg.get('storedBytes', 0) / (1024**2), 2),
            'metric_filter_count': lg.get('metricFilterCount', 0),
        })
    return create_response(account_id, region, "log_groups", log_groups)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_log_streams(
    role_arn: str,
    log_group_name: str,
    limit: int = 50,
    region: str = "us-east-1"
) -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    logs_client = session.client('logs', region_name=region)
    result = safe_call(
        logs_client.describe_log_streams,
        logGroupName=log_group_name,
        limit=limit,
        orderBy='LastEventTime',
        descending=True
    )
    if result['status'] == 'error':
        return create_response(account_id, region, "log_streams", [], "error", result)
    streams = []
    for stream in result['data'].get('logStreams', []):
        streams.append({
            'log_stream_name': stream.get('logStreamName'),
            'creation_time': datetime.fromtimestamp(stream.get('creationTime', 0) / 1000).isoformat(),
            'first_event_timestamp': datetime.fromtimestamp(stream.get('firstEventTimestamp', 0) / 1000).isoformat() if stream.get('firstEventTimestamp') else None,
            'last_event_timestamp': datetime.fromtimestamp(stream.get('lastEventTimestamp', 0) / 1000).isoformat() if stream.get('lastEventTimestamp') else None,
            'stored_bytes': stream.get('storedBytes'),
        })
    return create_response(account_id, region, "log_streams", streams)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def filter_log_events(
    role_arn: str,
    log_group_name: str,
    filter_pattern: str = "",
    start_hours_ago: int = 24,
    limit: int = 100,
    region: str = "us-east-1"
) -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    logs_client = session.client('logs', region_name=region)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=start_hours_ago)
    params = {
        'logGroupName': log_group_name,
        'startTime': int(start_time.timestamp() * 1000),
        'endTime': int(end_time.timestamp() * 1000),
        'limit': limit
    }
    if filter_pattern:
        params['filterPattern'] = filter_pattern
    result = safe_call(logs_client.filter_log_events, **params)
    if result['status'] == 'error':
        return create_response(account_id, region, "log_events", [], "error", result)
    events = []
    for event in result['data'].get('events', []):
        events.append({
            'log_stream_name': event.get('logStreamName'),
            'timestamp': datetime.fromtimestamp(event.get('timestamp', 0) / 1000).isoformat(),
            'message': event.get('message'),
            'ingestion_time': datetime.fromtimestamp(event.get('ingestionTime', 0) / 1000).isoformat(),
        })
    return create_response(account_id, region, "log_events", {
        'events': events,
        'event_count': len(events),
        'filter_pattern': filter_pattern,
        'searched_time_range': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        }
    })
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_cost_and_usage(
    role_arn: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = "DAILY",
    metrics: List[str] = None,
    group_by: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    if metrics is None:
        metrics = ["UnblendedCost", "UsageQuantity"]
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    ce_client = session.client('ce', region_name='us-east-1')
    if not end_date:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    params = {
        'TimePeriod': {
            'Start': start_date,
            'End': end_date
        },
        'Granularity': granularity,
        'Metrics': metrics
    }
    if group_by:
        params['GroupBy'] = group_by
    result = safe_call(ce_client.get_cost_and_usage, **params)
    if result['status'] == 'error':
        return create_response(account_id, "global", "cost_and_usage", {}, "error", result)
    cost_data = {
        'time_period': {
            'start': start_date,
            'end': end_date
        },
        'granularity': granularity,
        'metrics': metrics,
        'results_by_time': result['data'].get('ResultsByTime', []),
        'dimension_value_attributes': result['data'].get('DimensionValueAttributes', [])
    }
    return create_response(account_id, "global", "cost_and_usage", cost_data)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_cost_forecast(
    role_arn: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = "MONTHLY",
    metric: str = "UNBLENDED_COST"
) -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    ce_client = session.client('ce', region_name='us-east-1')
    if not start_date:
        start_date = datetime.utcnow().strftime('%Y-%m-%d')
    if not end_date:
        end_date = (datetime.utcnow() + relativedelta(months=3)).strftime('%Y-%m-%d')
    result = safe_call(
        ce_client.get_cost_forecast,
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Metric=metric,
        Granularity=granularity
    )
    if result['status'] == 'error':
        return create_response(account_id, "global", "cost_forecast", {}, "error", result)
    forecast_data = {
        'time_period': {
            'start': start_date,
            'end': end_date
        },
        'granularity': granularity,
        'metric': metric,
        'total': result['data'].get('Total', {}),
        'forecast_results_by_time': result['data'].get('ForecastResultsByTime', [])
    }
    return create_response(account_id, "global", "cost_forecast", forecast_data)
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_cost_by_service(
    role_arn: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    return get_cost_and_usage(
        role_arn=role_arn,
        start_date=start_date,
        end_date=end_date,
        granularity="MONTHLY",
        metrics=["UnblendedCost"],
        group_by=[{"Type": "DIMENSION", "Key": "SERVICE"}]
    )
@mcp.tool()
@retry_with_backoff(max_retries=3)
def get_cost_tags(role_arn: str, tag_key: str) -> Dict[str, Any]:
    session = assume_role_session(role_arn)
    account_id = get_account_id(session)
    ce_client = session.client('ce', region_name='us-east-1')
    end_date = datetime.utcnow().strftime('%Y-%m-%d')
    start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    result = safe_call(
        ce_client.get_tags,
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        TagKey=tag_key
    )
    if result['status'] == 'error':
        return create_response(account_id, "global", "cost_tags", {}, "error", result)
    return create_response(account_id, "global", "cost_tags", {
        'tag_key': tag_key,
        'tags': result['data'].get('Tags', []),
        'time_period': {'start': start_date, 'end': end_date}
    })
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AWS Optimization Tools",
        "timestamp": datetime.utcnow().isoformat()
    }
@app.get("/")
async def root():
    return {
        "service": "AWS Optimization FastMCP Tools",
        "version": "1.0.0",
        "description": "Read-only AWS data exposure for Bedrock Agentic AI cost optimization",
        "available_tools": [
            "get_ec2_instances",
            "get_ec2_tags",
            "get_ec2_cpu_utilization",
            "get_rds_instances",
            "get_rds_clusters",
            "get_lambda_functions",
            "get_lambda_function_config",
            "get_s3_buckets",
            "get_s3_bucket_size",
            "get_ecs_clusters",
            "get_ecs_tasks",
            "get_cloudwatch_metrics",
            "get_metric_statistics",
            "get_log_groups",
            "get_log_streams",
            "filter_log_events",
            "get_cost_and_usage",
            "get_cost_forecast",
            "get_cost_by_service",
            "get_cost_tags"
        ],
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AWS Optimization FastMCP Server...")
    logger.info("Available at: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/docs")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

# AWS Optimization FastMCP Tools

Production-ready FastMCP toolset for exposing AWS read-only data to Bedrock Agentic AI systems for autonomous cost optimization analysis.

## 🎯 Overview

This toolset enables Bedrock AI models (Claude 3, Llama 3) to autonomously analyze AWS infrastructure and generate actionable cost-saving insights including:

- **Underutilized EC2 instances** - Identify instances with low CPU usage
- **Idle RDS replicas** - Detect unused database replicas
- **Unused Lambda functions** - Find functions with no recent invocations
- **S3 Glacier migration candidates** - Expensive buckets suitable for archival
- **CloudWatch metrics analysis** - Resource utilization patterns
- **Cost forecasting** - Predict future AWS spending

## 🏗️ Architecture

```
┌─────────────────┐
│  Bedrock Agent  │ (Claude 3 / Llama 3)
│   (LLM Brain)   │
└────────┬────────┘
         │ MCP Protocol
         ▼
┌─────────────────┐
│  FastMCP Server │ (This Project)
│   tools.py      │
└────────┬────────┘
         │ AWS SDK (boto3)
         ▼
┌─────────────────┐
│   AWS Account   │
│  (Read-Only)    │
│  STS AssumeRole │
└─────────────────┘
```

## 📋 Prerequisites

- Python 3.10 or higher
- AWS Account with appropriate IAM roles
- Read-only IAM role ARN for cross-account access

## 🚀 Quick Start

### 1. Installation

```powershell
# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Set up your AWS credentials:

```powershell
# Option 1: Environment variables
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"

# Option 2: AWS CLI profile
aws configure
```

### 3. Create IAM Role (Read-Only)

Create an IAM role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:ListMetrics",
        "cloudwatch:GetMetricData",
        "cloudwatch:GetMetricStatistics",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:GetLogEvents",
        "logs:FilterLogEvents",
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ce:GetTags",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning",
        "s3:GetEncryptionConfiguration",
        "s3:GetLifecycleConfiguration",
        "ec2:DescribeInstances",
        "ec2:DescribeTags",
        "rds:DescribeDBInstances",
        "rds:DescribeDBClusters",
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "ecs:ListClusters",
        "ecs:DescribeClusters",
        "ecs:ListTasks",
        "ecs:DescribeTasks"
      ],
      "Resource": "*"
    }
  ]
}
```

Trust policy for the role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 4. Run the Server

```powershell
# Start the FastMCP server
python tools.py
```

The server will start at `http://localhost:8000`

Access the interactive API documentation at `http://localhost:8000/docs`

## 🛠️ Available Tools

### EC2 Tools
- `get_ec2_instances` - Retrieve all EC2 instances with metadata
- `get_ec2_tags` - Get EC2 resource tags
- `get_ec2_cpu_utilization` - Get CPU metrics for specific instance

### RDS Tools
- `get_rds_instances` - Retrieve RDS database instances
- `get_rds_clusters` - Retrieve RDS clusters (Aurora)

### Lambda Tools
- `get_lambda_functions` - List all Lambda functions
- `get_lambda_function_config` - Get detailed function configuration

### S3 Tools
- `get_s3_buckets` - List all S3 buckets with metadata
- `get_s3_bucket_size` - Get bucket size and object count

### ECS Tools
- `get_ecs_clusters` - Retrieve ECS clusters
- `get_ecs_tasks` - Get tasks in a cluster

### CloudWatch Tools
- `get_cloudwatch_metrics` - List available metrics
- `get_metric_statistics` - Get metric statistics

### CloudWatch Logs Tools
- `get_log_groups` - List all log groups
- `get_log_streams` - Get log streams in a group
- `filter_log_events` - Search logs with pattern matching

### Cost Explorer Tools
- `get_cost_and_usage` - Retrieve cost and usage data
- `get_cost_forecast` - Get forecasted costs
- `get_cost_by_service` - Cost breakdown by service
- `get_cost_tags` - Get cost allocation tags

## 💡 Usage Examples

### From Bedrock Agent (Python)

```python
import boto3
import json

# Initialize MCP client
mcp_endpoint = "http://localhost:8000"

# Example: Get EC2 instances
role_arn = "arn:aws:iam::123456789012:role/ReadOnlyRole"

response = await mcp.invoke("get_ec2_instances", {
    "role_arn": role_arn,
    "region": "us-east-1"
})

instances = response['data']

# Example: Get cost data
cost_response = await mcp.invoke("get_cost_and_usage", {
    "role_arn": role_arn,
    "granularity": "MONTHLY",
    "group_by": [{"Type": "DIMENSION", "Key": "SERVICE"}]
})

# Example: Get CPU utilization for analysis
cpu_data = await mcp.invoke("get_ec2_cpu_utilization", {
    "role_arn": role_arn,
    "instance_id": "i-1234567890abcdef0",
    "start_hours_ago": 168  # 7 days
})

# AI analyzes data and generates insights
if cpu_data['data']['datapoints']:
    avg_cpu = sum(d['Average'] for d in cpu_data['data']['datapoints']) / len(cpu_data['data']['datapoints'])
    
    if avg_cpu < 10:
        print(f"💡 Insight: Instance {instance_id} is underutilized (Avg CPU: {avg_cpu}%)")
        print(f"💰 Recommendation: Consider downsizing or stopping this instance")
        print(f"📊 Estimated monthly savings: $50-150")
```

### Direct API Call (curl)

```powershell
# Get EC2 instances
curl -X POST "http://localhost:8000/tools/get_ec2_instances" `
  -H "Content-Type: application/json" `
  -d '{\"role_arn\": \"arn:aws:iam::123456789012:role/ReadOnlyRole\", \"region\": \"us-east-1\"}'

# Get cost forecast
curl -X POST "http://localhost:8000/tools/get_cost_forecast" `
  -H "Content-Type: application/json" `
  -d '{\"role_arn\": \"arn:aws:iam::123456789012:role/ReadOnlyRole\"}'
```

## 🔒 Security Features

✅ **Read-Only Operations** - No destructive actions possible  
✅ **STS AssumeRole** - Temporary credentials with automatic expiration  
✅ **Permission-Aware** - Graceful handling of AccessDenied errors  
✅ **Throttling Protection** - Automatic retry with exponential backoff  
✅ **Input Validation** - Pydantic schema validation  
✅ **Structured Logging** - Comprehensive audit trail  

## 📊 Response Format

All tools return a standardized response:

```json
{
  "account_id": "123456789012",
  "region": "us-east-1",
  "data_type": "ec2_instances",
  "timestamp": "2025-10-17T10:30:00.000000",
  "status": "success",
  "data": [
    {
      "instance_id": "i-1234567890abcdef0",
      "instance_type": "t3.medium",
      "state": "running",
      "launch_time": "2025-10-01T08:00:00",
      "tags": {"Name": "WebServer", "Environment": "Production"}
    }
  ]
}
```

Error response:

```json
{
  "account_id": "123456789012",
  "region": "us-east-1",
  "data_type": "ec2_instances",
  "timestamp": "2025-10-17T10:30:00.000000",
  "status": "error",
  "error_code": "AccessDenied",
  "error_message": "User is not authorized to perform: ec2:DescribeInstances",
  "recoverable": true,
  "data": []
}
```

## 🧠 AI Agent Workflow

1. **Data Collection Phase**
   - Agent calls multiple tools in parallel
   - Gathers EC2, RDS, Lambda, S3, and cost data

2. **Analysis Phase**
   - Correlates metrics with cost data
   - Identifies patterns and anomalies
   - Calculates utilization percentages

3. **Insight Generation Phase**
   - Generates actionable recommendations
   - Estimates cost savings
   - Prioritizes by impact

4. **Presentation Phase**
   - Formats insights for user review
   - Includes confidence scores
   - Provides implementation steps

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Server settings
PORT = 8000
HOST = "0.0.0.0"

# AWS settings
AWS_DEFAULT_REGION = "us-east-1"
AWS_STS_SESSION_DURATION = 3600

# Retry settings
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1.0
```

Or use environment variables:

```powershell
$env:PORT="8000"
$env:AWS_DEFAULT_REGION="us-west-2"
$env:LOG_LEVEL="DEBUG"
```

## 📝 Logging

Logs are output to console with configurable levels:

```python
# Change log level in tools.py
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Testing

Test individual tools:

```powershell
# Test EC2 instances
python -c "from tools import get_ec2_instances; print(get_ec2_instances('arn:aws:iam::123456789012:role/ReadOnly'))"

# Test cost data
python -c "from tools import get_cost_and_usage; print(get_cost_and_usage('arn:aws:iam::123456789012:role/ReadOnly'))"
```

## 🚀 Deployment

### Production Deployment

```powershell
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn tools:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "tools:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Integration with Bedrock

### Setup Bedrock Agent

```python
import boto3

bedrock_agent = boto3.client('bedrock-agent-runtime')

# Configure MCP tools endpoint
agent_config = {
    'agentId': 'your-agent-id',
    'agentAliasId': 'your-alias-id',
    'tools': [
        {
            'toolSpec': {
                'name': 'aws_optimization_tools',
                'description': 'AWS read-only data access for cost optimization',
                'inputSchema': {
                    'json': {
                        'type': 'object',
                        'properties': {
                            'tool_name': {'type': 'string'},
                            'parameters': {'type': 'object'}
                        }
                    }
                }
            }
        }
    ]
}
```

## ⚠️ Limitations

- Cost Explorer data has ~24 hour delay
- S3 CloudWatch metrics updated daily
- Some AWS APIs have rate limits
- STS temporary credentials expire after 1 hour

## 🐛 Troubleshooting

**Issue**: `AccessDenied` errors  
**Solution**: Verify IAM role permissions and trust policy

**Issue**: `ThrottlingException`  
**Solution**: Tool includes automatic retry with backoff

**Issue**: Missing data in responses  
**Solution**: Check if resources exist in specified region

**Issue**: Cost Explorer errors  
**Solution**: Ensure Cost Explorer is enabled in AWS account

## 📄 License

MIT License - See LICENSE file

## 👥 Authors

Senior Backend & AI Systems Engineer

## 🔗 Related Resources

- [AWS Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [FastMCP Documentation](https://github.com/fastmcp/fastmcp)
- [AWS Cost Explorer API](https://docs.aws.amazon.com/cost-management/latest/APIReference/Welcome.html)
- [Bedrock Agent Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)

---

**Built for production. Optimized for AI. Secured for peace of mind.** 🚀

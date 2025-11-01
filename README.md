# Agentic Cloud Cost Optimizer - Architecture & Design

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     BEDROCK AGENTIC AI LAYER                        │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │   Claude 3    │  │   Llama 3     │  │  Custom LLM   │          │
│  │    Model      │  │    Model      │  │               │          │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘          │
│          │                  │                   │                   │
│          └──────────────────┴───────────────────┘                   │
│                             │                                        │
│                    MCP Protocol (JSON-RPC)                          │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTMCP SERVER LAYER                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                         tools.py                               │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │ │
│  │  │ EC2 Tools│ │RDS Tools │ │S3 Tools  │ │Lambda    │         │ │
│  │  │          │ │          │ │          │ │Tools     │         │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │ │
│  │  │ECS Tools │ │CloudWatch│ │CW Logs   │ │Cost      │         │ │
│  │  │          │ │Tools     │ │Tools     │ │Explorer  │         │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              HELPER FUNCTIONS & UTILITIES                      │ │
│  │  • assume_role_session()   • safe_call()                       │ │
│  │  • paginate_results()      • retry_with_backoff()             │ │
│  │  • create_response()       • get_account_id()                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                     AWS SDK (boto3)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS SERVICES                                │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │  EC2 │ │ RDS  │ │  S3  │ │Lambda│ │ ECS  │ │  CW  │ │  CE  │  │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    AWS STS (AssumeRole)                        │ │
│  │  Temporary Credentials • Session Token • 1-hour Duration       │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow

1. **AI Agent Request**
   ```
   Agent → "Analyze EC2 instances for underutilization"
   ```

2. **MCP Tool Invocation**
   ```
   invoke("get_ec2_instances", {"role_arn": "...", "region": "us-east-1"})
   invoke("get_ec2_cpu_utilization", {"role_arn": "...", "instance_id": "i-xxx"})
   ```

3. **AWS Authentication**
   ```
   STS AssumeRole → Temporary Credentials → API Call
   ```

4. **Data Retrieval**
   ```
   Paginated API Calls → Aggregate Results → Format Response
   ```

5. **AI Analysis**
   ```
   LLM Processes Data → Generates Insights → Returns Recommendations
   ```

## 🛡️ Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
│                                                             │
│  Layer 1: IAM Role Permissions (Read-Only)                 │
│  ├─ Principle of Least Privilege                           │
│  ├─ No Write/Delete permissions                            │
│  └─ Resource-level constraints                             │
│                                                             │
│  Layer 2: STS Temporary Credentials                        │
│  ├─ 1-hour session duration                                │
│  ├─ Automatic expiration                                   │
│  └─ Session token required                                 │
│                                                             │
│  Layer 3: Exception Handling                               │
│  ├─ AccessDenied → Graceful degradation                    │
│  ├─ Throttling → Exponential backoff                       │
│  └─ Structured error responses                             │
│                                                             │
│  Layer 4: Input Validation                                 │
│  ├─ Pydantic schema validation                             │
│  ├─ Type checking                                          │
│  └─ Parameter sanitization                                 │
│                                                             │
│  Layer 5: Audit Logging                                    │
│  ├─ All API calls logged                                   │
│  ├─ Timestamp tracking                                     │
│  └─ Account/region metadata                                │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow Diagram

```
┌─────────────┐
│ AI Agent    │
│ (Bedrock)   │
└──────┬──────┘
       │ 1. Request: "Find underutilized EC2"
       ▼
┌─────────────────┐
│ FastMCP Server  │
│ (tools.py)      │
└──────┬──────────┘
       │ 2. assume_role_session(role_arn)
       ▼
┌─────────────────┐
│ AWS STS         │
│ AssumeRole      │
└──────┬──────────┘
       │ 3. Temporary credentials
       ▼
┌─────────────────┐
│ boto3 Session   │
└──────┬──────────┘
       │ 4. ec2.describe_instances()
       ▼
┌─────────────────┐      ┌─────────────────┐
│ AWS EC2 API     │ ───► │ Pagination      │
└──────┬──────────┘      └─────────────────┘
       │ 5. Instance data (JSON)
       ▼
┌─────────────────┐
│ Response        │
│ Formatter       │
└──────┬──────────┘
       │ 6. Standardized response
       ▼
┌─────────────────┐
│ AI Agent        │
│ (Analysis)      │
└──────┬──────────┘
       │ 7. "Instance i-xxx has 3% CPU"
       │ 8. Request: get_ec2_cpu_utilization(i-xxx)
       ▼
┌─────────────────┐
│ CloudWatch API  │
└──────┬──────────┘
       │ 9. Metric data (7 days)
       ▼
┌─────────────────┐
│ AI Agent        │
│ (Insight Gen)   │
└──────┬──────────┘
       │ 10. "💡 Recommendation: Stop i-xxx"
       │     "💰 Savings: $50/month"
       ▼
┌─────────────────┐
│ User Interface  │
└─────────────────┘
```

## 🧩 Component Breakdown

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| Main Tools | `tools.py` | MCP tool definitions, AWS API wrappers |
| Configuration | `config.py` | Settings, environment variables |
| Schemas | `schemas.py` | Pydantic models for validation |
| Example Agent | `example_agent.py` | Reference AI agent implementation |
| Tests | `test_tools.py` | Comprehensive test suite |

### Helper Functions

| Function | Purpose | Key Features |
|----------|---------|--------------|
| `assume_role_session()` | AWS authentication | STS role assumption, session management |
| `safe_call()` | Error handling | Exception wrapping, structured errors |
| `paginate_results()` | Data retrieval | Automatic pagination, rate limiting |
| `retry_with_backoff()` | Resilience | Exponential backoff, throttle handling |
| `create_response()` | Standardization | Consistent response format |

### Tool Categories

#### 1. **Compute Tools**
- EC2: Instance management, metrics
- Lambda: Function analysis, configuration
- ECS: Container orchestration

#### 2. **Storage Tools**
- S3: Bucket analysis, size metrics
- RDS: Database instances, clusters

#### 3. **Monitoring Tools**
- CloudWatch: Metrics, statistics
- CloudWatch Logs: Log analysis, filtering

#### 4. **Cost Tools**
- Cost Explorer: Usage, forecasts, tags

## 🔐 IAM Permissions Matrix

| Service | Required Permissions | Tool Usage |
|---------|---------------------|------------|
| EC2 | `DescribeInstances`, `DescribeTags` | Instance inventory, utilization |
| RDS | `DescribeDBInstances`, `DescribeDBClusters` | Database analysis |
| Lambda | `ListFunctions`, `GetFunction*` | Function optimization |
| S3 | `ListAllMyBuckets`, `GetBucket*` | Storage optimization |
| ECS | `ListClusters`, `DescribeClusters` | Container analysis |
| CloudWatch | `ListMetrics`, `GetMetric*` | Performance metrics |
| Logs | `DescribeLogGroups`, `FilterLogEvents` | Log analysis |
| Cost Explorer | `GetCostAndUsage`, `GetCostForecast` | Cost optimization |
| STS | `AssumeRole`, `GetCallerIdentity` | Authentication |

## 📈 Scalability Considerations

### Current Capabilities
- ✅ Handles 1000+ EC2 instances
- ✅ Processes 100+ S3 buckets
- ✅ Analyzes 500+ Lambda functions
- ✅ Supports multi-region queries
- ✅ Automatic pagination for large datasets

### Performance Optimizations
1. **Lazy Loading**: Data fetched on-demand
2. **Pagination**: Efficient memory usage
3. **Caching**: Session credentials cached
4. **Async Support**: Ready for async operations
5. **Rate Limiting**: Built-in throttle handling

## 🔮 Future Enhancements

### Phase 2 Features
- [ ] Multi-account aggregation
- [ ] Real-time streaming metrics
- [ ] Custom CloudWatch dashboards
- [ ] Automated remediation actions
- [ ] Cost anomaly detection
- [ ] ML-based recommendations

### Integration Options
- [ ] AWS Organizations support
- [ ] CloudFormation stack analysis
- [ ] Trusted Advisor integration
- [ ] AWS Well-Architected reviews
- [ ] Savings Plans analysis

## 📝 Code Quality Standards

### Design Principles
1. **Read-Only by Design**: No destructive operations
2. **Defense in Depth**: Multiple security layers
3. **Fail Gracefully**: Structured error handling
4. **Type Safety**: Full type annotations
5. **Documentation First**: Comprehensive docstrings

### Best Practices Implemented
- ✅ PEP 8 compliance
- ✅ Type hints throughout
- ✅ Comprehensive logging
- ✅ Exception handling
- ✅ Input validation
- ✅ Consistent response formats
- ✅ Modular architecture
- ✅ Production-ready error handling

---

**Built with security, scalability, and AI-first design in mind.** 🚀

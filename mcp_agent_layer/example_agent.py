import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
class BedrockOptimizationAgent:
    def __init__(self, mcp_endpoint: str, role_arn: str):
        self.mcp_endpoint = mcp_endpoint
        self.role_arn = role_arn
        self.insights = []
    async def analyze_ec2_utilization(self, region: str = "us-east-1") -> List[Dict[str, Any]]:
        print("🔍 Analyzing EC2 instances...")
        from tools import get_ec2_instances, get_ec2_cpu_utilization
        instances_response = get_ec2_instances(self.role_arn, region)
        if instances_response['status'] != 'success':
            print(f"❌ Error getting instances: {instances_response.get('error_message')}")
            return []
        instances = instances_response['data']
        underutilized = []
        for instance in instances:
            if instance['state'] != 'running':
                continue
            instance_id = instance['instance_id']
            print(f"  📊 Checking {instance_id} ({instance['instance_type']})...")
            cpu_response = get_ec2_cpu_utilization(
                self.role_arn,
                instance_id,
                start_hours_ago=168,
                region=region
            )
            if cpu_response['status'] == 'success' and cpu_response['data']['datapoints']:
                datapoints = cpu_response['data']['datapoints']
                avg_cpu = sum(dp.get('Average', 0) for dp in datapoints) / len(datapoints)
                max_cpu = max(dp.get('Maximum', 0) for dp in datapoints)
                if avg_cpu < 10:
                    insight = {
                        'type': 'underutilized_ec2',
                        'severity': 'high' if avg_cpu < 5 else 'medium',
                        'instance_id': instance_id,
                        'instance_type': instance['instance_type'],
                        'avg_cpu': round(avg_cpu, 2),
                        'max_cpu': round(max_cpu, 2),
                        'recommendation': self._generate_ec2_recommendation(instance, avg_cpu),
                        'estimated_monthly_savings': self._estimate_ec2_savings(instance['instance_type'])
                    }
                    underutilized.append(insight)
                    print(f"    ⚠️  Underutilized! Avg CPU: {avg_cpu:.2f}%")
        return underutilized
    async def analyze_rds_usage(self, region: str = "us-east-1") -> List[Dict[str, Any]]:
        print("\n🔍 Analyzing RDS instances...")
        from tools import get_rds_instances
        rds_response = get_rds_instances(self.role_arn, region)
        if rds_response['status'] != 'success':
            print(f"❌ Error getting RDS instances: {rds_response.get('error_message')}")
            return []
        insights = []
        instances = rds_response['data']
        for db in instances:
            if db['multi_az'] and db['db_instance_class'].startswith('db.t'):
                insight = {
                    'type': 'expensive_rds_config',
                    'severity': 'medium',
                    'db_identifier': db['db_instance_identifier'],
                    'db_class': db['db_instance_class'],
                    'issue': 'Multi-AZ enabled on small instance type',
                    'recommendation': 'Consider if Multi-AZ is necessary for this workload',
                    'estimated_monthly_savings': 50
                }
                insights.append(insight)
                print(f"  ⚠️  {db['db_instance_identifier']}: Expensive Multi-AZ on small instance")
        return insights
    async def analyze_s3_storage(self) -> List[Dict[str, Any]]:
        print("\n🔍 Analyzing S3 buckets...")
        from tools import get_s3_buckets, get_s3_bucket_size
        buckets_response = get_s3_buckets(self.role_arn)
        if buckets_response['status'] != 'success':
            print(f"❌ Error getting buckets: {buckets_response.get('error_message')}")
            return []
        insights = []
        buckets = buckets_response['data']
        for bucket in buckets:
            if bucket['lifecycle_rules'] == 0:
                bucket_name = bucket['name']
                region = bucket['region']
                size_response = get_s3_bucket_size(
                    self.role_arn,
                    bucket_name,
                    region if region != 'unknown' else 'us-east-1'
                )
                if size_response['status'] == 'success':
                    size_gb = size_response['data'].get('size_gb', 0)
                    if size_gb and size_gb > 100:
                        insight = {
                            'type': 's3_lifecycle_missing',
                            'severity': 'medium',
                            'bucket_name': bucket_name,
                            'size_gb': size_gb,
                            'issue': 'No lifecycle policies configured',
                            'recommendation': 'Configure lifecycle policy to transition old objects to Glacier',
                            'estimated_monthly_savings': int(size_gb * 0.02)
                        }
                        insights.append(insight)
                        print(f"  💡 {bucket_name}: {size_gb}GB without lifecycle policy")
        return insights
    async def analyze_lambda_usage(self, region: str = "us-east-1") -> List[Dict[str, Any]]:
        print("\n🔍 Analyzing Lambda functions...")
        from tools import get_lambda_functions
        lambda_response = get_lambda_functions(self.role_arn, region)
        if lambda_response['status'] != 'success':
            print(f"❌ Error getting Lambda functions: {lambda_response.get('error_message')}")
            return []
        insights = []
        functions = lambda_response['data']
        for func in functions:
            memory_mb = func['memory_size']
            if memory_mb >= 3008:
                insight = {
                    'type': 'oversized_lambda',
                    'severity': 'low',
                    'function_name': func['function_name'],
                    'memory_mb': memory_mb,
                    'recommendation': 'Analyze actual memory usage and right-size allocation',
                    'estimated_monthly_savings': 20
                }
                insights.append(insight)
                print(f"  ⚠️  {func['function_name']}: High memory allocation ({memory_mb}MB)")
        return insights
    async def analyze_costs(self) -> Dict[str, Any]:
        print("\n💰 Analyzing costs...")
        from tools import get_cost_by_service, get_cost_forecast
        cost_response = get_cost_by_service(self.role_arn)
        if cost_response['status'] != 'success':
            print(f"❌ Error getting costs: {cost_response.get('error_message')}")
            return {}
        forecast_response = get_cost_forecast(self.role_arn)
        cost_summary = {
            'current_month_estimate': 0,
            'top_services': [],
            'forecast': {}
        }
        if cost_response['status'] == 'success':
            results = cost_response['data'].get('results_by_time', [])
            if results:
                for result in results:
                    groups = result.get('Groups', [])
                    for group in groups:
                        service = group['Keys'][0]
                        amount = float(group['Metrics']['UnblendedCost']['Amount'])
                        cost_summary['top_services'].append({
                            'service': service,
                            'cost': round(amount, 2)
                        })
        cost_summary['top_services'].sort(key=lambda x: x['cost'], reverse=True)
        cost_summary['top_services'] = cost_summary['top_services'][:5]
        if forecast_response['status'] == 'success':
            total = forecast_response['data'].get('total', {})
            cost_summary['forecast'] = {
                'amount': float(total.get('Amount', 0)),
                'unit': total.get('Unit', 'USD')
            }
        print(f"  📊 Top 5 services by cost:")
        for service in cost_summary['top_services']:
            print(f"    - {service['service']}: ${service['cost']:.2f}")
        return cost_summary
    async def generate_report(self, region: str = "us-east-1") -> Dict[str, Any]:
        print("\n" + "="*60)
        print("🚀 AWS OPTIMIZATION ANALYSIS REPORT")
        print("="*60)
        print(f"📅 Generated: {datetime.utcnow().isoformat()}")
        print(f"🌎 Region: {region}")
        print(f"🔑 Role: {self.role_arn}")
        print("="*60 + "\n")
        ec2_insights = await self.analyze_ec2_utilization(region)
        rds_insights = await self.analyze_rds_usage(region)
        s3_insights = await self.analyze_s3_storage()
        lambda_insights = await self.analyze_lambda_usage(region)
        cost_summary = await self.analyze_costs()
        all_insights = ec2_insights + rds_insights + s3_insights + lambda_insights
        total_savings = sum(insight.get('estimated_monthly_savings', 0) for insight in all_insights)
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'region': region,
            'total_insights': len(all_insights),
            'insights_by_type': {
                'ec2': len(ec2_insights),
                'rds': len(rds_insights),
                's3': len(s3_insights),
                'lambda': len(lambda_insights)
            },
            'estimated_monthly_savings': total_savings,
            'cost_summary': cost_summary,
            'insights': all_insights
        }
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        print(f"✅ Total Optimization Opportunities: {len(all_insights)}")
        print(f"💵 Estimated Monthly Savings: ${total_savings:.2f}")
        print(f"\nBreakdown:")
        print(f"  - EC2 Insights: {len(ec2_insights)}")
        print(f"  - RDS Insights: {len(rds_insights)}")
        print(f"  - S3 Insights: {len(s3_insights)}")
        print(f"  - Lambda Insights: {len(lambda_insights)}")
        print("="*60 + "\n")
        return report
    def _generate_ec2_recommendation(self, instance: Dict, avg_cpu: float) -> str:
        if avg_cpu < 5:
            return f"Consider stopping this instance or downsizing to a smaller type"
        elif avg_cpu < 10:
            return f"Monitor usage and consider downsizing from {instance['instance_type']}"
        return "Optimize usage patterns"
    def _estimate_ec2_savings(self, instance_type: str) -> int:
        pricing = {
            't2.micro': 10,
            't2.small': 20,
            't2.medium': 40,
            't3.medium': 50,
            't3.large': 80,
            'm5.large': 90,
            'm5.xlarge': 180
        }
        return pricing.get(instance_type, 50)
async def main():
    role_arn = "arn:aws:iam::123456789012:role/ReadOnlyRole"
    agent = BedrockOptimizationAgent(
        mcp_endpoint="http://localhost:8000",
        role_arn=role_arn
    )
    report = await agent.generate_report(region="us-east-1")
    output_file = f"optimization_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"📄 Full report saved to: {output_file}\n")
if __name__ == "__main__":
    asyncio.run(main())

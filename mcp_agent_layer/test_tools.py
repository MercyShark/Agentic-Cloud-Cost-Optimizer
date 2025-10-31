import sys
from typing import Dict, Any, List
from datetime import datetime
class ToolTester:
    def __init__(self, role_arn: str, region: str = "us-east-1"):
        self.role_arn = role_arn
        self.region = region
        self.results = []
    def test_tool(self, tool_name: str, tool_func, *args, **kwargs) -> bool:
        print(f"\n🧪 Testing: {tool_name}")
        print(f"   Args: {args}")
        print(f"   Kwargs: {kwargs}")
        try:
            result = tool_func(*args, **kwargs)
            if result.get('status') == 'success':
                data_count = 0
                if isinstance(result.get('data'), list):
                    data_count = len(result['data'])
                elif isinstance(result.get('data'), dict):
                    data_count = len(result['data'].keys())
                print(f"   ✅ SUCCESS - Retrieved {data_count} items")
                self.results.append({
                    'tool': tool_name,
                    'status': 'passed',
                    'data_count': data_count
                })
                return True
            else:
                error_msg = result.get('error_message', 'Unknown error')
                print(f"   ⚠️  WARNING - {error_msg}")
                self.results.append({
                    'tool': tool_name,
                    'status': 'warning',
                    'error': error_msg
                })
                return False
        except Exception as e:
            print(f"   ❌ FAILED - {str(e)}")
            self.results.append({
                'tool': tool_name,
                'status': 'failed',
                'error': str(e)
            })
            return False
    def run_all_tests(self):
        from tools import (
            get_ec2_instances, get_ec2_tags, get_ec2_cpu_utilization,
            get_rds_instances, get_rds_clusters,
            get_lambda_functions,
            get_s3_buckets,
            get_ecs_clusters,
            get_cloudwatch_metrics,
            get_log_groups,
            get_cost_and_usage, get_cost_forecast, get_cost_by_service
        )
        print("="*70)
        print("🚀 AWS OPTIMIZATION TOOLS - TEST SUITE")
        print("="*70)
        print(f"📅 Started: {datetime.utcnow().isoformat()}")
        print(f"🌎 Region: {self.region}")
        print(f"🔑 Role: {self.role_arn}")
        print("="*70)
        print("\n" + "─"*70)
        print("📦 EC2 TOOLS")
        print("─"*70)
        self.test_tool("get_ec2_instances", get_ec2_instances, self.role_arn, self.region)
        self.test_tool("get_ec2_tags", get_ec2_tags, self.role_arn, self.region)
        print("\n" + "─"*70)
        print("🗄️  RDS TOOLS")
        print("─"*70)
        self.test_tool("get_rds_instances", get_rds_instances, self.role_arn, self.region)
        self.test_tool("get_rds_clusters", get_rds_clusters, self.role_arn, self.region)
        print("\n" + "─"*70)
        print("⚡ LAMBDA TOOLS")
        print("─"*70)
        self.test_tool("get_lambda_functions", get_lambda_functions, self.role_arn, self.region)
        print("\n" + "─"*70)
        print("🪣 S3 TOOLS")
        print("─"*70)
        self.test_tool("get_s3_buckets", get_s3_buckets, self.role_arn)
        print("\n" + "─"*70)
        print("🐳 ECS TOOLS")
        print("─"*70)
        self.test_tool("get_ecs_clusters", get_ecs_clusters, self.role_arn, self.region)
        print("\n" + "─"*70)
        print("📊 CLOUDWATCH TOOLS")
        print("─"*70)
        self.test_tool("get_cloudwatch_metrics", get_cloudwatch_metrics, 
                      self.role_arn, "AWS/EC2", self.region)
        print("\n" + "─"*70)
        print("📝 CLOUDWATCH LOGS TOOLS")
        print("─"*70)
        self.test_tool("get_log_groups", get_log_groups, self.role_arn, self.region)
        print("\n" + "─"*70)
        print("💰 COST EXPLORER TOOLS")
        print("─"*70)
        self.test_tool("get_cost_and_usage", get_cost_and_usage, self.role_arn)
        self.test_tool("get_cost_forecast", get_cost_forecast, self.role_arn)
        self.test_tool("get_cost_by_service", get_cost_by_service, self.role_arn)
        self.print_summary()
    def print_summary(self):
        print("\n" + "="*70)
        print("📋 TEST RESULTS SUMMARY")
        print("="*70)
        passed = sum(1 for r in self.results if r['status'] == 'passed')
        warned = sum(1 for r in self.results if r['status'] == 'warning')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        total = len(self.results)
        print(f"\n✅ Passed:  {passed}/{total}")
        print(f"⚠️  Warning: {warned}/{total}")
        print(f"❌ Failed:  {failed}/{total}")
        if failed > 0:
            print("\n❌ Failed Tests:")
            for r in self.results:
                if r['status'] == 'failed':
                    print(f"   - {r['tool']}: {r.get('error', 'Unknown')}")
        if warned > 0:
            print("\n⚠️  Warnings:")
            for r in self.results:
                if r['status'] == 'warning':
                    print(f"   - {r['tool']}: {r.get('error', 'Unknown')}")
        print("\n" + "="*70)
        if failed == 0:
            print("🎉 ALL CRITICAL TESTS PASSED!")
        else:
            print("⚠️  SOME TESTS FAILED - Check permissions and AWS setup")
        print("="*70 + "\n")
        return failed == 0
def main():
    import argparse
    parser = argparse.ArgumentParser(description='Test AWS Optimization Tools')
    parser.add_argument('--role-arn', required=True, help='IAM Role ARN to assume')
    parser.add_argument('--region', default='us-east-1', help='AWS Region (default: us-east-1)')
    args = parser.parse_args()
    tester = ToolTester(args.role_arn, args.region)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
if __name__ == "__main__":
    main()

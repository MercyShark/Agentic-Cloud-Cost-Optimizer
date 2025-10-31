import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
import boto3
from botocore.exceptions import ClientError
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
class BedrockOptimizationAgent:
    def __init__(
        self,
        role_arn: str,
        region: str = "ap-south-1",
        bedrock_region: str = "ap-south-1",
        model_id: str = "openai.gpt-oss-120b-1:0",
        profile_name: str = "sova-profile"
    ):
        self.role_arn = role_arn
        self.region = region
        self.model_id = model_id
        self.profile_name = profile_name
        session = boto3.Session(profile_name=profile_name)
        self.bedrock_runtime = session.client(
            'bedrock-runtime',
            region_name=bedrock_region
        )
        self.conversation_history = []
        self.data_cache = {}
        logger.info(f"Initialized Bedrock Agent with model: {model_id}")
    def _import_mcp_tools(self):
        try:
            import tools
            def get_func(name):
                obj = getattr(tools, name)
                if hasattr(obj, 'fn'):
                    return obj.fn
                elif hasattr(obj, 'func'):
                    return obj.func
                elif callable(obj):
                    return obj
                else:
                    raise AttributeError(f"Cannot extract callable from {name}")
            return {
                'get_ec2_instances': get_func('get_ec2_instances'),
                'get_ec2_cpu_utilization': get_func('get_ec2_cpu_utilization'),
                'get_ec2_tags': get_func('get_ec2_tags'),
                'get_rds_instances': get_func('get_rds_instances'),
                'get_rds_clusters': get_func('get_rds_clusters'),
                'get_lambda_functions': get_func('get_lambda_functions'),
                'get_lambda_function_config': get_func('get_lambda_function_config'),
                'get_s3_buckets': get_func('get_s3_buckets'),
                'get_s3_bucket_size': get_func('get_s3_bucket_size'),
                'get_ecs_clusters': get_func('get_ecs_clusters'),
                'get_ecs_tasks': get_func('get_ecs_tasks'),
                'get_cloudwatch_metrics': get_func('get_cloudwatch_metrics'),
                'get_metric_statistics': get_func('get_metric_statistics'),
                'get_log_groups': get_func('get_log_groups'),
                'get_log_streams': get_func('get_log_streams'),
                'filter_log_events': get_func('filter_log_events'),
                'get_cost_and_usage': get_func('get_cost_and_usage'),
                'get_cost_forecast': get_func('get_cost_forecast'),
                'get_cost_by_service': get_func('get_cost_by_service'),
                'get_cost_tags': get_func('get_cost_tags')
            }
        except ImportError as e:
            logger.error(f"Failed to import MCP tools: {e}")
            raise
    def _create_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "toolSpec": {
                    "name": "get_ec2_instances",
                    "description": "Retrieve all EC2 instances with metadata including state, type, launch time, and tags. Use this to analyze compute resources.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "region": {
                                    "type": "string",
                                    "description": "AWS region to query",
                                    "default": self.region
                                }
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_ec2_cpu_utilization",
                    "description": "Get CPU utilization metrics for a specific EC2 instance over the past 7 days. Use this to identify underutilized instances.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "instance_id": {
                                    "type": "string",
                                    "description": "EC2 instance ID (e.g., i-1234567890abcdef0)"
                                },
                                "start_hours_ago": {
                                    "type": "integer",
                                    "description": "Hours of history to retrieve",
                                    "default": 168
                                },
                                "region": {
                                    "type": "string",
                                    "description": "AWS region",
                                    "default": self.region
                                }
                            },
                            "required": ["instance_id"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_rds_instances",
                    "description": "Retrieve all RDS database instances with configuration and status. Use this to analyze database resources.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "region": {
                                    "type": "string",
                                    "description": "AWS region to query",
                                    "default": self.region
                                }
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_lambda_functions",
                    "description": "List all Lambda functions with configuration details. Use this to identify unused or oversized functions.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "region": {
                                    "type": "string",
                                    "description": "AWS region to query",
                                    "default": self.region
                                }
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_s3_buckets",
                    "description": "List all S3 buckets with metadata including versioning, encryption, and lifecycle policies. Use this for storage optimization.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_cost_and_usage",
                    "description": "Retrieve AWS cost and usage data from Cost Explorer. Use this to analyze spending patterns.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "start_date": {
                                    "type": "string",
                                    "description": "Start date in YYYY-MM-DD format"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "End date in YYYY-MM-DD format"
                                },
                                "granularity": {
                                    "type": "string",
                                    "description": "Time granularity: DAILY or MONTHLY",
                                    "default": "MONTHLY"
                                }
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_cost_forecast",
                    "description": "Get forecasted AWS costs for the next 3 months. Use this to predict future spending.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_cost_by_service",
                    "description": "Get cost breakdown by AWS service. Use this to identify which services cost the most.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "get_log_groups",
                    "description": "List CloudWatch Log Groups with storage size. Use this to identify expensive log storage.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "region": {
                                    "type": "string",
                                    "description": "AWS region to query",
                                    "default": self.region
                                }
                            }
                        }
                    }
                }
            }
        ]
    def _convert_tools_for_model(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        openai_tools = []
        for tool in tools:
            tool_spec = tool.get("toolSpec", {})
            input_schema = tool_spec.get("inputSchema", {}).get("json", {})
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool_spec.get("name"),
                    "description": tool_spec.get("description"),
                    "parameters": input_schema
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools
    def _call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = f"{tool_name}:{json.dumps(parameters, sort_keys=True)}"
        if cache_key in self.data_cache:
            logger.info(f"Using cached data for {tool_name}")
            return self.data_cache[cache_key]
        tools = self._import_mcp_tools()
        if tool_name not in tools:
            return {
                "status": "error",
                "error_message": f"Tool {tool_name} not found"
            }
        try:
            parameters['role_arn'] = self.role_arn
            if 'region' in parameters and not parameters['region']:
                parameters['region'] = self.region
            logger.info(f"Calling MCP tool: {tool_name} with params: {parameters}")
            tool_func = tools[tool_name]
            if asyncio.iscoroutinefunction(tool_func):
                result = asyncio.run(tool_func(**parameters))
            else:
                result = tool_func(**parameters)
            if result.get('status') == 'success':
                self.data_cache[cache_key] = result
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    def _invoke_bedrock(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        try:
            request_body = {
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": 0.7
            }
            if tools:
                request_body["tools"] = tools
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            response_body = json.loads(response['body'].read())
            return response_body
        except ClientError as e:
            logger.error(f"Bedrock invocation error: {str(e)}")
            raise
    def analyze(self, user_prompt: str, max_iterations: int = 10) -> Dict[str, Any]:
        logger.info(f"Starting analysis for prompt: {user_prompt}")
        messages = [
            {
                "role": "user",
                "content": f"{system_prompt}\n\nUser Request: {user_prompt}"
            }
        ]
        tools = self._create_tool_definitions()
        tools = self._convert_tools_for_model(tools)
        iteration = 0
        tool_results = []
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}/{max_iterations}")
            response = self._invoke_bedrock(messages, tools)
            choice = response.get('choices', [{}])[0]
            message = choice.get('message', {})
            finish_reason = choice.get('finish_reason')
            tool_calls = message.get('tool_calls', [])
            content = message.get('content', '')
            if finish_reason == 'stop' and not tool_calls:
                logger.info("Agent completed analysis")
                return {
                    "status": "success",
                    "analysis": content,
                    "tool_calls": len(tool_results),
                    "iterations": iteration,
                    "timestamp": datetime.utcnow().isoformat()
                }
            elif tool_calls:
                logger.info(f"Agent requesting {len(tool_calls)} tool calls")
                messages.append({
                    "role": "assistant",
                    "content": content,
                    "tool_calls": tool_calls
                })
                tool_messages = []
                for tool_call in tool_calls:
                    tool_name = tool_call.get('function', {}).get('name')
                    tool_args_str = tool_call.get('function', {}).get('arguments', '{}')
                    tool_call_id = tool_call.get('id')
                    try:
                        tool_input = json.loads(tool_args_str)
                    except json.JSONDecodeError:
                        tool_input = {}
                    logger.info(f"Executing tool: {tool_name}")
                    result = self._call_mcp_tool(tool_name, tool_input)
                    tool_results.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result
                    })
                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(result, default=str)
                    })
                messages.extend(tool_messages)
            else:
                logger.warning(f"Unexpected finish reason: {finish_reason}")
                break
        logger.warning(f"Max iterations ({max_iterations}) reached")
        return {
            "status": "partial",
            "message": "Analysis incomplete - max iterations reached",
            "tool_calls": len(tool_results),
            "iterations": iteration
        }
    def chat(self, user_message: str) -> str:
        try:
            result = self.analyze(user_message)
            if result.get('status') == 'success':
                response = result.get('analysis', '')
                self.conversation_history.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.utcnow().isoformat()
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.utcnow().isoformat(),
                    "tool_calls": result.get('tool_calls', 0)
                })
                return response
            else:
                return f"Analysis incomplete: {result.get('message', 'Unknown error')}"
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"Error: {str(e)}"
    def save_conversation(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        logger.info(f"Conversation saved to {filename}")
    def clear_cache(self):
        self.data_cache.clear()
        logger.info("Cache cleared")
def interactive_mode(agent: BedrockOptimizationAgent):
    print("\n" + "="*70)
    print("AWS BEDROCK OPTIMIZATION AGENT")
    print("="*70)
    print("\nI'm your AI-powered AWS cost optimization assistant.")
    print("Ask me anything about your AWS infrastructure!\n")
    print("Examples:")
    print("  - Analyze my EC2 instances for underutilization")
    print("  - Show me cost optimization opportunities")
    print("  - What are my most expensive AWS services?")
    print("  - Find unused resources in my account")
    print("\nType 'quit' to exit, 'save' to save conversation, 'clear' to clear cache")
    print("="*70 + "\n")
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! Happy optimizing!")
                break
            elif user_input.lower() == 'save':
                filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                agent.save_conversation(filename)
                print(f"[OK] Conversation saved to {filename}")
                continue
            elif user_input.lower() == 'clear':
                agent.clear_cache()
                print("[OK] Cache cleared")
                continue
            print("\nAgent: Analyzing your request...\n")
            response = agent.chat(user_input)
            print(f"🤖 Agent:\n\n{response}\n")
        except KeyboardInterrupt:
            print("\n\nGoodbye! Happy optimizing!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {str(e)}")
            print(f"\n[ERROR] {str(e)}\n")
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='AWS Bedrock Optimization Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--role-arn',
        required=True,
        help='AWS IAM Role ARN for accessing resources'
    )
    parser.add_argument(
        '--region',
        default='ap-south-1',
        help='AWS region for resource analysis (default: us-east-1)'
    )
    parser.add_argument(
        '--bedrock-region',
        default='ap-south-1',
        help='AWS region for Bedrock service (default: us-east-1)'
    )
    parser.add_argument(
        '--model',
        default='openai.gpt-oss-120b-1:0',
        help='Bedrock model ID to use'
    )
    parser.add_argument(
        '--profile',
        default='sova-profile',
        help='AWS profile name to use (default: sova-profile)'
    )
    parser.add_argument(
        '--query',
        help='Single query to process (non-interactive mode)'
    )
    parser.add_argument(
        '--output',
        help='Output file for results (JSON format)'
    )
    args = parser.parse_args()
    print("Initializing Bedrock Agent...")
    print(f"Using AWS Profile: {args.profile}")
    try:
        agent = BedrockOptimizationAgent(
            role_arn=args.role_arn,
            region=args.region,
            bedrock_region=args.bedrock_region,
            model_id=args.model,
            profile_name=args.profile
        )
        print("[OK] Agent initialized successfully!\n")
        if args.query:
            print(f"Processing query: {args.query}\n")
            result = agent.analyze(args.query)
            if result.get('status') == 'success':
                print("\n" + "="*70)
                print("ANALYSIS RESULTS")
                print("="*70)
                print(f"\n{result.get('analysis', '')}\n")
                print("="*70)
                print(f"\nStatistics:")
                print(f"  - Tool calls: {result.get('tool_calls', 0)}")
                print(f"  - Iterations: {result.get('iterations', 0)}")
                print(f"  - Timestamp: {result.get('timestamp', '')}")
                print("="*70 + "\n")
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(result, f, indent=2)
                    print(f"[OK] Results saved to {args.output}\n")
            else:
                print(f"\n[ERROR] Analysis incomplete: {result.get('message', 'Unknown error')}\n")
                sys.exit(1)
        else:
            interactive_mode(agent)
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)
if __name__ == "__main__":
    main()

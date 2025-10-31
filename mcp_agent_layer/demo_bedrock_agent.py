from bedrock_agent import BedrockOptimizationAgent
import json
from datetime import datetime
def demo_ec2_analysis(agent):
    print("\n" + "="*70)
    print("📊 DEMO 1: EC2 Underutilization Analysis")
    print("="*70)
    print(f"\n💬 Prompt: {prompt.strip()}")
    print("\n🤔 Agent working...\n")
    result = agent.analyze(prompt)
    if result['status'] == 'success':
        print("🤖 Agent Response:")
        print("-" * 70)
        print(result['analysis'])
        print("-" * 70)
        print(f"\n📈 Stats: {result['tool_calls']} tool calls, {result['iterations']} iterations")
    else:
        print(f"❌ Error: {result.get('message')}")
def demo_cost_forecast(agent):
    print("\n" + "="*70)
    print("💰 DEMO 2: Cost Forecast & Trend Analysis")
    print("="*70)
    print(f"\n💬 Prompt: {prompt.strip()}")
    print("\n🤔 Agent working...\n")
    result = agent.analyze(prompt)
    if result['status'] == 'success':
        print("🤖 Agent Response:")
        print("-" * 70)
        print(result['analysis'])
        print("-" * 70)
        print(f"\n📈 Stats: {result['tool_calls']} tool calls, {result['iterations']} iterations")
    else:
        print(f"❌ Error: {result.get('message')}")
def demo_s3_optimization(agent):
    print("\n" + "="*70)
    print("🪣 DEMO 3: S3 Storage Optimization")
    print("="*70)
    print(f"\n💬 Prompt: {prompt.strip()}")
    print("\n🤔 Agent working...\n")
    result = agent.analyze(prompt)
    if result['status'] == 'success':
        print("🤖 Agent Response:")
        print("-" * 70)
        print(result['analysis'])
        print("-" * 70)
        print(f"\n📈 Stats: {result['tool_calls']} tool calls, {result['iterations']} iterations")
    else:
        print(f"❌ Error: {result.get('message')}")
def demo_comprehensive_analysis(agent):
    print("\n" + "="*70)
    print("🎯 DEMO 4: Comprehensive Cost Optimization Analysis")
    print("="*70)
    print(f"\n💬 Prompt: {prompt.strip()}")
    print("\n🤔 Agent working...\n")
    result = agent.analyze(prompt)
    if result['status'] == 'success':
        print("🤖 Agent Response:")
        print("-" * 70)
        print(result['analysis'])
        print("-" * 70)
        print(f"\n📈 Stats: {result['tool_calls']} tool calls, {result['iterations']} iterations")
        filename = f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full results saved to: {filename}")
    else:
        print(f"❌ Error: {result.get('message')}")
def demo_interactive_conversation(agent):
    print("\n" + "="*70)
    print("💬 DEMO 5: Interactive Conversation")
    print("="*70)
    prompts = [
        "What are my top 3 most expensive AWS services?",
        "Tell me more about the most expensive one",
        "What specific recommendations do you have to reduce those costs?"
    ]
    for i, prompt in enumerate(prompts, 1):
        print(f"\n💬 Turn {i}: {prompt}")
        print("🤔 Agent working...\n")
        response = agent.chat(prompt)
        print("🤖 Agent:")
        print("-" * 70)
        print(response)
        print("-" * 70)
        if i < len(prompts):
            input("\n⏸️  Press Enter to continue...")
    filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    agent.save_conversation(filename)
    print(f"\n💾 Conversation saved to: {filename}")
def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Bedrock Agent Demo')
    parser.add_argument('--role-arn', required=True, help='AWS IAM Role ARN')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--demo', type=int, help='Run specific demo (1-5)')
    args = parser.parse_args()
    print("\n🚀 Initializing Bedrock Agent...")
    try:
        agent = BedrockOptimizationAgent(
            role_arn=args.role_arn,
            region=args.region
        )
        print("✅ Agent initialized!\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)
    demos = {
        1: ("EC2 Underutilization Analysis", demo_ec2_analysis),
        2: ("Cost Forecast & Trends", demo_cost_forecast),
        3: ("S3 Storage Optimization", demo_s3_optimization),
        4: ("Comprehensive Analysis", demo_comprehensive_analysis),
        5: ("Interactive Conversation", demo_interactive_conversation)
    }
    if args.demo:
        if args.demo in demos:
            name, func = demos[args.demo]
            print(f"\n🎬 Running Demo {args.demo}: {name}")
            func(agent)
        else:
            print(f"❌ Invalid demo number. Choose 1-5")
    else:
        print("\n" + "="*70)
        print("🎬 BEDROCK AGENT - COMPLETE DEMO SUITE")
        print("="*70)
        print("\nThis will run 5 comprehensive demos:")
        print("  1. EC2 Underutilization Analysis")
        print("  2. Cost Forecast & Trends")
        print("  3. S3 Storage Optimization")
        print("  4. Comprehensive Analysis")
        print("  5. Interactive Conversation")
        print("\nEach demo will take 15-30 seconds.")
        print("="*70)
        choice = input("\n▶️  Run all demos? (y/n): ").strip().lower()
        if choice == 'y':
            for num, (name, func) in demos.items():
                print(f"\n\n{'='*70}")
                print(f"🎬 Demo {num}/{len(demos)}: {name}")
                print('='*70)
                func(agent)
                if num < len(demos):
                    input("\n⏸️  Press Enter to continue to next demo...")
            print("\n\n" + "="*70)
            print("🎉 ALL DEMOS COMPLETED!")
            print("="*70)
            print("\nCheck the generated JSON files for detailed results.")
        else:
            print("\n👋 Demo cancelled. Use --demo <1-5> to run specific demos.")
if __name__ == "__main__":
    main()

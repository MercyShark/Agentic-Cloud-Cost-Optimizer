# 🚀 Getting Started with Bedrock Agent

## Quick Setup Guide (5 minutes)

---

## ✅ Prerequisites Checklist

Before you start, make sure you have:

- [ ] Python 3.10+ installed
- [ ] AWS credentials configured
- [ ] IAM role ARN ready
- [ ] Bedrock model access enabled
- [ ] MCP tools set up (tools.py in same directory)

---

## 📋 Step-by-Step Setup

### Step 1: Enable Bedrock Model Access

**Important: You must enable Claude 3.5 Sonnet in AWS Bedrock first!**

1. Log in to AWS Console
2. Navigate to: **Amazon Bedrock** → **Model access**
3. Click **"Modify model access"** or **"Request model access"**
4. Find **"Claude 3.5 Sonnet"** in the list
5. Check the box next to **"anthropic.claude-3-5-sonnet-20241022-v2:0"**
6. Click **"Request model access"** or **"Save changes"**
7. Wait for approval (usually instant)

**Verify access:**
```powershell
aws bedrock list-foundation-models --region us-east-1 | Select-String "claude-3-5"
```

---

### Step 2: Set AWS Credentials

```powershell
# Option 1: Environment Variables
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-east-1"

# Option 2: AWS CLI
aws configure
```

**Test credentials:**
```powershell
aws sts get-caller-identity
```

---

### Step 3: Verify IAM Role

Your IAM role needs:
1. **Read-only permissions** for AWS services (see `iam_policy_readonly.json`)
2. **Trust policy** allowing your account to assume it

**Test role assumption:**
```powershell
aws sts assume-role `
  --role-arn "arn:aws:iam::123456789012:role/ReadOnlyRole" `
  --role-session-name "test-session"
```

---

### Step 4: Run Your First Query

```powershell
# Navigate to MCP directory
cd c:\Users\Rishabh\OneDrive\Desktop\super-ops-frontend\project-bolt-sb1-cwx4boqk\mcp

# Run interactive mode
python bedrock_agent.py --role-arn "arn:aws:iam::123456789012:role/ReadOnlyRole"
```

**You should see:**
```
🤖 AWS BEDROCK OPTIMIZATION AGENT
======================================================================

I'm your AI-powered AWS cost optimization assistant.
Ask me anything about your AWS infrastructure!

💬 You: 
```

---

## 🎯 Try These Example Prompts

### Beginner Prompts

```
Show me my AWS costs for the last month
```

```
List all my EC2 instances
```

```
What's my most expensive AWS service?
```

### Intermediate Prompts

```
Analyze my EC2 instances for underutilization
```

```
Find opportunities to reduce my S3 storage costs
```

```
Show me cost trends and forecast for next quarter
```

### Advanced Prompts

```
Perform a comprehensive cost optimization analysis covering all services
```

```
Identify all underutilized resources and calculate potential savings
```

```
Generate a detailed cost optimization report with prioritized recommendations
```

---

## 🧪 Run Demo Suite

Test all capabilities:

```powershell
python demo_bedrock_agent.py --role-arn "arn:aws:iam::123456789012:role/ReadOnlyRole"
```

Or run specific demos:
```powershell
# Demo 1: EC2 Analysis
python demo_bedrock_agent.py --role-arn "your-role-arn" --demo 1

# Demo 2: Cost Forecast
python demo_bedrock_agent.py --role-arn "your-role-arn" --demo 2

# Demo 3: S3 Optimization
python demo_bedrock_agent.py --role-arn "your-role-arn" --demo 3

# Demo 4: Comprehensive Analysis
python demo_bedrock_agent.py --role-arn "your-role-arn" --demo 4

# Demo 5: Interactive Conversation
python demo_bedrock_agent.py --role-arn "your-role-arn" --demo 5
```

---

## 💡 Usage Modes

### 1. Interactive Chat Mode

**Best for:** Exploratory analysis, follow-up questions

```powershell
python bedrock_agent.py --role-arn "arn:aws:iam::123:role/ReadOnly"
```

**Features:**
- Conversational interface
- Context awareness
- Follow-up questions
- Save/clear commands

**Commands:**
- `save` - Save conversation to JSON
- `clear` - Clear data cache
- `quit` - Exit

---

### 2. Single Query Mode

**Best for:** Automation, specific questions, CI/CD

```powershell
python bedrock_agent.py `
  --role-arn "arn:aws:iam::123:role/ReadOnly" `
  --query "Analyze my EC2 instances" `
  --output results.json
```

**Features:**
- One-shot analysis
- JSON output
- Scriptable
- Pipeline-friendly

---

### 3. Programmatic Mode

**Best for:** Custom applications, integration

```python
from bedrock_agent import BedrockOptimizationAgent

agent = BedrockOptimizationAgent(
    role_arn="arn:aws:iam::123:role/ReadOnly"
)

result = agent.analyze("Find underutilized EC2 instances")
print(result['analysis'])
```

---

## 🔧 Configuration Options

### Change AWS Region

```powershell
python bedrock_agent.py `
  --role-arn "arn:aws:iam::123:role/ReadOnly" `
  --region "us-west-2"
```

### Use Different Bedrock Region

```powershell
python bedrock_agent.py `
  --role-arn "arn:aws:iam::123:role/ReadOnly" `
  --bedrock-region "us-west-2"
```

### Use Different Model

```powershell
# Use Claude 3 Haiku (faster, cheaper)
python bedrock_agent.py `
  --role-arn "arn:aws:iam::123:role/ReadOnly" `
  --model "anthropic.claude-3-haiku-20240307-v1:0"
```

**Available Models:**
- `anthropic.claude-3-5-sonnet-20241022-v2:0` ⭐ Recommended
- `anthropic.claude-3-5-sonnet-20240620-v1:0`
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0` (Fastest)

---

## 🎓 Understanding the Output

### Analysis Response Structure

```
🤖 Agent:

## 🎯 Analysis Title

### Resource: resource-name (type)
- **Key Metric**: Value
- **Status**: State
- **Cost Impact**: HIGH/MEDIUM/LOW

**💰 Recommendation**: Specific action to take
**Estimated Savings**: $XX/month

**Implementation Steps**:
1. Step one
2. Step two
3. Step three

**Risk Level**: LOW/MEDIUM/HIGH - Explanation

---

📊 Summary Statistics
💵 Total Potential Savings: $XXX/month
```

### JSON Output Format

```json
{
  "status": "success",
  "analysis": "Full text response...",
  "tool_calls": 5,
  "iterations": 3,
  "timestamp": "2025-10-17T10:30:00.000000"
}
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "Model not found" or "Access denied"

**Cause:** Claude 3.5 Sonnet not enabled in Bedrock

**Solution:**
1. AWS Console → Bedrock → Model access
2. Request access to Claude 3.5 Sonnet
3. Wait for approval (instant)

---

### Issue 2: "AssumeRole permission denied"

**Cause:** Your IAM user can't assume the target role

**Solution:**
Add this to your IAM user policy:
```json
{
  "Effect": "Allow",
  "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::123456789012:role/ReadOnlyRole"
}
```

---

### Issue 3: "No module named 'tools'"

**Cause:** Wrong directory or tools.py not found

**Solution:**
```powershell
# Ensure you're in the MCP directory
cd c:\Users\Rishabh\OneDrive\Desktop\super-ops-frontend\project-bolt-sb1-cwx4boqk\mcp

# Verify tools.py exists
dir tools.py

# Run from this directory
python bedrock_agent.py --role-arn "your-role-arn"
```

---

### Issue 4: Slow or no response

**Causes & Solutions:**

**A. Large dataset:**
- Use more specific prompts
- Query single region instead of all
- Focus on specific service

**B. Bedrock throttling:**
- Wait a few minutes
- Use Claude Haiku for faster responses
- Reduce concurrent requests

**C. Network issues:**
- Check AWS connectivity
- Verify VPN not blocking
- Test: `aws bedrock list-foundation-models`

---

### Issue 5: Empty or incomplete responses

**Causes & Solutions:**

**A. No resources in account:**
- Verify resources exist in specified region
- Check: `aws ec2 describe-instances --region us-east-1`

**B. Insufficient permissions:**
- Verify IAM role has all required permissions
- See `iam_policy_readonly.json`

**C. Region mismatch:**
- Ensure resources are in the queried region
- Try different region with `--region`

---

## 📊 Performance Tips

### Optimize Query Speed

1. **Be specific:**
   ```
   ❌ "Analyze everything"
   ✅ "Analyze EC2 instances in us-east-1 for underutilization"
   ```

2. **Use cache:**
   - Don't clear cache unless needed
   - Repeated queries are faster

3. **Choose right model:**
   - Claude 3.5 Sonnet: Best quality
   - Claude 3 Haiku: Fastest

4. **Batch related questions:**
   ```
   ✅ "Analyze EC2, RDS, and S3 for cost optimization"
   
   Instead of 3 separate queries
   ```

---

## 🎯 Best Practices

### 1. Start Specific, Then Broaden

```
Turn 1: "Show me EC2 costs"
Turn 2: "Analyze those instances for underutilization"
Turn 3: "What are the top 3 recommendations?"
```

### 2. Use Interactive Mode for Exploration

```powershell
# Explore and refine
python bedrock_agent.py --role-arn "your-role-arn"

💬 You: Show me costs
💬 You: Focus on EC2
💬 You: What about underutilized instances?
💬 You: Give me implementation steps for top recommendation
```

### 3. Use Batch Mode for Automation

```powershell
# Generate weekly report
python bedrock_agent.py `
  --role-arn "your-role-arn" `
  --query "Generate weekly cost optimization report" `
  --output "reports/week-$(Get-Date -Format 'yyyy-MM-dd').json"
```

### 4. Save Important Conversations

```
💬 You: [complex analysis]
🤖 Agent: [detailed recommendations]

💬 You: save
✅ Conversation saved to conversation_20251017_103000.json
```

---

## 🚀 Next Steps

1. **✅ Run your first query** (above)
2. **📖 Read** [BEDROCK_AGENT_README.md](BEDROCK_AGENT_README.md) for full docs
3. **🧪 Try demo suite** to see all capabilities
4. **💡 Experiment** with different prompts
5. **🔧 Customize** for your use case
6. **📊 Integrate** into your workflow

---

## 🆘 Need Help?

| Issue | Resource |
|-------|----------|
| Setup problems | This guide |
| Usage examples | BEDROCK_AGENT_README.md |
| MCP tools reference | README.md |
| AWS permissions | iam_policy_readonly.json |
| General troubleshooting | TROUBLESHOOTING.md |

---

## 📞 Quick Reference

```powershell
# Interactive mode
python bedrock_agent.py --role-arn "arn:aws:iam::123:role/ReadOnly"

# Single query
python bedrock_agent.py --role-arn "arn:aws:iam::123:role/ReadOnly" `
  --query "Your question here"

# Save output
python bedrock_agent.py --role-arn "arn:aws:iam::123:role/ReadOnly" `
  --query "Your question" --output results.json

# Different region
python bedrock_agent.py --role-arn "arn:aws:iam::123:role/ReadOnly" `
  --region us-west-2

# Run demos
python demo_bedrock_agent.py --role-arn "arn:aws:iam::123:role/ReadOnly"
```

---

**You're all set! Start asking questions about your AWS infrastructure! 🚀**

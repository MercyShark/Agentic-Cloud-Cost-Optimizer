# 🔐 AWS Profile Setup Guide

## Profile Configuration Added

The Bedrock agent now uses AWS profile **"sova-profile"** by default.

---

## ✅ Setup AWS Profile

### Create the "sova-profile" in your AWS credentials file:

**Location:** `C:\Users\Rishabh\.aws\credentials`

```powershell
# Create .aws directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.aws"

# Add sova-profile to credentials file
@"
[sova-profile]
aws_access_key_id = 
aws_secret_access_key = 
"@ | Out-File -FilePath "$env:USERPROFILE\.aws\credentials" -Encoding ASCII -Append

# Add region configuration
@"
[profile sova-profile]
region = ap-south-1
output = json
"@ | Out-File -FilePath "$env:USERPROFILE\.aws\config" -Encoding ASCII -Append

echo "✅ sova-profile configured!"
```

---

## 🚀 Run the Agent

Now run the agent (it will use "sova-profile" automatically):

```powershell
py .\bedrock_agent.py --role-arn arn:aws:iam::905418130401:role/CloudInsightsReadOnly --query "identify underutilized ec2 instances"
```

Or specify a different profile:

```powershell
py .\bedrock_agent.py --role-arn arn:aws:iam::905418130401:role/CloudInsightsReadOnly --profile my-other-profile --query "show ec2 costs"
```

---

## 🧪 Verify Profile Setup

Test that the profile works:

```powershell
# Test with AWS CLI
aws sts get-caller-identity --profile sova-profile

# Or test with Python
python -c "import boto3; session = boto3.Session(profile_name='sova-profile'); print('✅ Profile OK:', session.client('sts').get_caller_identity()['Account'])"
```

---

## 📝 Manual Setup

If you prefer to edit manually:

1. Open: `C:\Users\Rishabh\.aws\credentials`
2. Add:
   ```ini
   [sova-profile]
   aws_access_key_id = 
   aws_secret_access_key = 
   ```

3. Open: `C:\Users\Rishabh\.aws\config`
4. Add:
   ```ini
   [profile sova-profile]
   region = ap-south-1
   output = json
   ```

---

## 🎯 Complete Example

```powershell
# Setup (run once)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.aws"

# Create credentials file
@"
[sova-profile]
aws_access_key_id =
aws_secret_access_key = 
"@ | Out-File -FilePath "$env:USERPROFILE\.aws\credentials" -Encoding ASCII

# Create config file
@"
[profile sova-profile]
region = ap-south-1
output = json
"@ | Out-File -FilePath "$env:USERPROFILE\.aws\config" -Encoding ASCII

# Verify
python -c "import boto3; s = boto3.Session(profile_name='sova-profile'); print('✅ Account:', s.client('sts').get_caller_identity()['Account'])"

# Run agent
py .\bedrock_agent.py --role-arn arn:aws:iam::905418130401:role/CloudInsightsReadOnly --query "identify underutilized ec2 instances"
```

---

## 🔍 What Changed in bedrock_agent.py

### 1. Added profile parameter:
```python
def __init__(
    self,
    role_arn: str,
    region: str = "ap-south-1",
    bedrock_region: str = "ap-south-1",
    model_id: str = "openai.gpt-oss-120b-1:0",
    profile_name: str = "sova-profile"  # NEW!
):
```

### 2. Uses boto3 Session with profile:
```python
# Initialize boto3 session with profile
session = boto3.Session(profile_name=profile_name)

# Initialize Bedrock client
self.bedrock_runtime = session.client(
    'bedrock-runtime',
    region_name=bedrock_region
)
```

### 3. Added CLI argument:
```python
parser.add_argument(
    '--profile',
    default='sova-profile',
    help='AWS profile name to use (default: sova-profile)'
)
```

---

## ✨ Benefits

✅ **Multiple AWS accounts** - Switch between profiles easily  
✅ **Secure credentials** - No environment variables needed  
✅ **Standard AWS workflow** - Works like AWS CLI  
✅ **Team friendly** - Each developer can have their own profile  

---

Ready to run! 🚀

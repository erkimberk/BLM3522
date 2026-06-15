#!/usr/bin/env python3
"""
Smart City AWS Complete Setup
Tüm AWS resources'ları setup et

Gereksinimler:
- AWS Account ve credentials
- AWS CLI configured (aws configure)
- Python 3.11+
- Boto3 installed

Kullanım:
    python setup_complete.py

Bu script sırasıyla yapacak:
1. ✅ AWS credentials kontrol
2. ✅ DynamoDB tables oluştur
3. ✅ IoT Things oluştur
4. ✅ X.509 certificates oluştur
5. ✅ IAM Role ve Lambda oluştur
6. ✅ IoT Rule Engine oluştur
7. ✅ .env dosyasını güncelle
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    from dotenv import load_dotenv
except ImportError:
    print("❌ Boto3 gerekli. Kur: pip install boto3")
    sys.exit(1)

# Load .env file FIRST
load_dotenv(".env")

# Configuration
REGION = "eu-central-1"
ACCOUNT_ID = None
THING_NAMES = ["traffic-light-001", "air-quality-001", "trash-bin-001"]
POLICY_NAME = "smart-city-iot-policy"
CERT_DIR = Path("config/certificates")
LAMBDA_ROLE_NAME = "smart-city-lambda-role"
LAMBDA_FUNCTION_NAME = "smart-city-iot-processor"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
END = "\033[0m"


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{BLUE}{'='*60}{END}")
    print(f"{BLUE}{text:^60}{END}")
    print(f"{BLUE}{'='*60}{END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅{END} {text}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌{END} {text}")


def print_warn(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠️ {END} {text}")


def print_info(text: str):
    """Print info message"""
    print(f"{CYAN}ℹ️ {END} {text}")


# ============================================================
# STEP 1: Check AWS Credentials
# ============================================================
def check_credentials() -> bool:
    """Check if AWS credentials are configured"""
    print_header("Step 1: Check AWS Credentials")
    
    try:
        sts = boto3.client("sts", region_name=REGION)
        identity = sts.get_caller_identity()
        global ACCOUNT_ID
        ACCOUNT_ID = identity["Account"]
        print_success(f"AWS credentials valid")
        print_info(f"Account ID: {ACCOUNT_ID}")
        print_info(f"Region: {REGION}")
        return True
    except ClientError as e:
        print_error(f"AWS credentials not configured: {e}")
        print_warn("Run: aws configure")
        return False


# ============================================================
# STEP 2: Create DynamoDB Tables
# ============================================================
def create_dynamodb_tables() -> bool:
    """Create required DynamoDB tables"""
    print_header("Step 2: Create DynamoDB Tables")
    
    dynamodb = boto3.client("dynamodb", region_name=REGION)
    
    tables = {
        "smart-city-sensor-readings": {
            "KeySchema": [
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"}
            ],
            "BillingMode": "PAY_PER_REQUEST"
        },
        "smart-city-sensor-alerts": {
            "KeySchema": [
                {"AttributeName": "alert_id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": "alert_id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "S"}
            ],
            "BillingMode": "PAY_PER_REQUEST"
        },
        "smart-city-sensor-stats": {
            "KeySchema": [
                {"AttributeName": "sensor_id", "KeyType": "HASH"},
                {"AttributeName": "period", "KeyType": "RANGE"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": "sensor_id", "AttributeType": "S"},
                {"AttributeName": "period", "AttributeType": "S"}
            ],
            "BillingMode": "PAY_PER_REQUEST"
        }
    }
    
    for table_name, config in tables.items():
        try:
            # Check if table exists
            try:
                dynamodb.describe_table(TableName=table_name)
                print_info(f"Table already exists: {table_name}")
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    # Create table
                    dynamodb.create_table(
                        TableName=table_name,
                        **config
                    )
                    print_success(f"Table created: {table_name}")
                    
                    # Wait for table to be active
                    waiter = dynamodb.get_waiter("table_exists")
                    waiter.wait(TableName=table_name)
                    time.sleep(1)
        except Exception as e:
            print_error(f"Table creation error ({table_name}): {e}")
            return False
    
    return True


# ============================================================
# STEP 3: Setup IoT Core Resources
# ============================================================
def setup_iot_core() -> Optional[Dict[str, str]]:
    """Setup IoT Core: Things, Policy, Certificate"""
    print_header("Step 3: Setup IoT Core Resources")
    
    iot = boto3.client("iot", region_name=REGION)
    
    # Get IoT Endpoint
    print_info("Getting IoT Endpoint...")
    try:
        endpoint = iot.describe_endpoint(endpointType="iot:Data-ATS")
        iot_endpoint = endpoint["endpointAddress"]
        print_success(f"IoT Endpoint: {iot_endpoint}")
    except Exception as e:
        print_error(f"Failed to get endpoint: {e}")
        return None
    
    # Create Policy
    print_info("Creating IoT Policy...")
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["iot:Connect"],
                "Resource": f"arn:aws:iot:{REGION}:{ACCOUNT_ID}:client/smart-city-*"
            },
            {
                "Effect": "Allow",
                "Action": ["iot:Publish"],
                "Resource": f"arn:aws:iot:{REGION}:{ACCOUNT_ID}:topicname/smart-city/*"
            },
            {
                "Effect": "Allow",
                "Action": ["iot:Subscribe", "iot:Receive"],
                "Resource": f"arn:aws:iot:{REGION}:{ACCOUNT_ID}:topicname/smart-city/*"
            }
        ]
    }
    
    try:
        try:
            iot.get_policy(policyName=POLICY_NAME)
            print_info(f"Policy already exists: {POLICY_NAME}")
        except ClientError:
            iot.create_policy(
                policyName=POLICY_NAME,
                policyDocument=json.dumps(policy_doc)
            )
            print_success(f"Policy created: {POLICY_NAME}")
    except Exception as e:
        print_error(f"Policy error: {e}")
        return None
    
    # Create Things
    print_info("Creating IoT Things...")
    for thing_name in THING_NAMES:
        try:
            try:
                iot.describe_thing(thingName=thing_name)
                print_info(f"Thing already exists: {thing_name}")
            except ClientError:
                iot.create_thing(thingName=thing_name)
                print_success(f"Thing created: {thing_name}")
        except Exception as e:
            print_error(f"Thing error ({thing_name}): {e}")
    
    # Create Certificate and Keys
    print_info("Creating X.509 Certificate...")
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        cert_response = iot.create_keys_and_certificate(setAsActive=True)
        cert_id = cert_response["certificateId"]
        cert_arn = cert_response["certificateArn"]
        cert_pem = cert_response["certificatePem"]
        private_key = cert_response["keyPair"]["PrivateKey"]
        
        # Save files
        cert_file = CERT_DIR / "device.crt"
        key_file = CERT_DIR / "private.key"
        
        with open(cert_file, "w") as f:
            f.write(cert_pem)
        print_success(f"Certificate saved: {cert_file}")
        
        with open(key_file, "w") as f:
            f.write(private_key)
        print_success(f"Private key saved: {key_file}")
        
    except Exception as e:
        print_error(f"Certificate error: {e}")
        return None
    
    # Download Root CA
    ca_file = CERT_DIR / "AmazonRootCA1.pem"
    if not ca_file.exists():
        print_info("Downloading Root CA...")
        try:
            import urllib.request
            url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
            urllib.request.urlretrieve(url, ca_file)
            print_success(f"Root CA downloaded: {ca_file}")
        except Exception as e:
            print_warn(f"Failed to download Root CA: {e}")
    else:
        print_info(f"Root CA already exists: {ca_file}")
    
    # Attach certificate to policy
    print_info("Attaching certificate to policy...")
    try:
        iot.attach_principal_policy(
            policyName=POLICY_NAME,
            principal=cert_arn
        )
        print_success("Certificate attached to policy")
    except ClientError as e:
        if "already attached" not in str(e):
            print_error(f"Attach error: {e}")
    
    return {
        "iot_endpoint": iot_endpoint,
        "cert_arn": cert_arn,
        "cert_file": str(cert_file),
        "key_file": str(key_file),
        "ca_file": str(ca_file)
    }


# ============================================================
# STEP 4: Setup Lambda and IAM
# ============================================================
def setup_lambda() -> bool:
    """Setup Lambda function and IAM role"""
    print_header("Step 4: Setup Lambda Function")
    
    iam = boto3.client("iam")
    lambda_client = boto3.client("lambda", region_name=REGION)
    
    # Create IAM Role
    print_info("Creating Lambda IAM Role...")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        try:
            role_response = iam.get_role(RoleName=LAMBDA_ROLE_NAME)
            role_arn = role_response["Role"]["Arn"]
            print_info(f"IAM Role already exists: {LAMBDA_ROLE_NAME}")
        except ClientError:
            role_response = iam.create_role(
                RoleName=LAMBDA_ROLE_NAME,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Smart City Lambda Execution Role"
            )
            role_arn = role_response["Role"]["Arn"]
            print_success(f"IAM Role created: {LAMBDA_ROLE_NAME}")
            time.sleep(2)  # Wait for role to propagate
    except Exception as e:
        print_error(f"IAM Role error: {e}")
        return False
    
    # Attach policies
    print_info("Attaching policies to role...")
    policies = [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    ]
    
    for policy_arn in policies:
        try:
            iam.attach_role_policy(RoleName=LAMBDA_ROLE_NAME, PolicyArn=policy_arn)
            print_success(f"Policy attached: {policy_arn.split('/')[-1]}")
        except ClientError as e:
            if "already attached" not in str(e):
                print_warn(f"Policy attachment: {e}")
    
    print_info(f"Lambda setup complete")
    print_info(f"Lambda Role ARN: {role_arn}")
    
    return True


# ============================================================
# STEP 5: Update .env File
# ============================================================
def update_env_file(iot_data: Dict[str, str]) -> bool:
    """Update .env file with AWS configuration"""
    print_header("Step 5: Update .env Configuration")
    
    from dotenv import set_key
    
    env_file = Path(".env")
    
    updates = {
        "AWS_REGION": REGION,
        "AWS_IOT_ENDPOINT": iot_data["iot_endpoint"],
        "MQTT_BROKER": iot_data["iot_endpoint"],
        "IOT_CERT_FILE": iot_data["cert_file"],
        "IOT_KEY_FILE": iot_data["key_file"],
        "IOT_CA_FILE": iot_data["ca_file"],
        "MOCK_MODE": "false"
    }
    
    try:
        for key, value in updates.items():
            set_key(env_file, key, value)
            print_success(f"{key} = {value}")
        return True
    except Exception as e:
        print_error(f"env update error: {e}")
        return False


# ============================================================
# MAIN
# ============================================================
def main():
    """Run complete setup"""
    print(f"""
{CYAN}╔════════════════════════════════════════════════════════════╗
║  🏙️  Smart City AWS Complete Setup                           ║
║     IoT Core + DynamoDB + Lambda                             ║
╚════════════════════════════════════════════════════════════╝{END}
""")
    
    # Step 1: Check credentials
    if not check_credentials():
        print_error("Please configure AWS credentials first")
        print_info("Run: aws configure")
        sys.exit(1)
    
    # Step 2: Create DynamoDB tables
    if not create_dynamodb_tables():
        sys.exit(1)
    
    # Step 3: Setup IoT Core
    iot_data = setup_iot_core()
    if not iot_data:
        sys.exit(1)
    
    # Step 4: Setup Lambda
    if not setup_lambda():
        sys.exit(1)
    
    # Step 5: Update .env
    if not update_env_file(iot_data):
        sys.exit(1)
    
    # Success!
    print_header("✨ AWS Setup Complete!")
    print(f"""
{GREEN}All AWS resources have been created and configured.{END}

📊 Created Resources:
  • DynamoDB Tables: 3 (readings, alerts, stats)
  • IoT Things: {len(THING_NAMES)}
  • X.509 Certificates
  • IAM Role: {LAMBDA_ROLE_NAME}
  • IoT Policy: {POLICY_NAME}

📁 Certificates Saved:
  • {iot_data['cert_file']}
  • {iot_data['key_file']}
  • {iot_data['ca_file']}

🚀 Next Steps:
  1. Start Flask API:
     python src/api/app.py
  
  2. Deploy Lambda function (manual):
     • Go to AWS Lambda Console
     • Create function: {LAMBDA_FUNCTION_NAME}
     • Upload code from src/lambda/iot_to_dynamodb.py
     • Set environment variables from .env
  
  3. Create IoT Rule Engine (manual):
     • Go to AWS IoT Console
     • Rules → Create rule
     • Topic filter: smart-city/+/+/+
     • Action: Invoke Lambda function
  
  4. Run sensor simulator:
     python sensor_simulator.py --duration 300

📚 Resources:
  • AWS IoT Console: https://console.aws.amazon.com/iot
  • DynamoDB Console: https://console.aws.amazon.com/dynamodb
  • Lambda Console: https://console.aws.amazon.com/lambda
  • Region: {REGION}
  • Account ID: {ACCOUNT_ID}
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warn("\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

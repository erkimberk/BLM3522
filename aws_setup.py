şu a"""
AWS IoT Smart City Application Setup Script
AWS IoT Core konfigürasyonu ve resource oluşturması

Kullanım:
    python aws_setup.py
"""

import boto3
import json
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Load existing env
load_dotenv(".env")

REGION = os.getenv("AWS_REGION", "eu-central-1")
THING_NAME = "smart-city-hub"
POLICY_NAME = "smart-city-iot-policy"
CERT_DIR = Path("config/certificates")

print("""
╔════════════════════════════════════════════════════════════╗
║    🏙️  AWS IoT Smart City Setup                          ║
║    IoT Core Resources Auto-Oluştur                         ║
╚════════════════════════════════════════════════════════════╝
""")

# Create certificates directory
CERT_DIR.mkdir(parents=True, exist_ok=True)
print(f"✅ Sertifika dizini: {CERT_DIR}")

# Initialize AWS clients
try:
    iot_client = boto3.client("iot", region_name=REGION)
    iot_data = boto3.client("iot-data", region_name=REGION)
    print(f"✅ AWS bağlantısı başarılı (Region: {REGION})")
except Exception as e:
    print(f"❌ AWS bağlantı hatası: {e}")
    print("   AWS credentials'ı kontrol et: aws configure")
    exit(1)

# ============================================================
# ADIM 1: IoT Endpoint'i al
# ============================================================
print("\n📍 ADIM 1: IoT Endpoint'i getir...")
try:
    endpoint_response = iot_client.describe_endpoint(endpointType="iot:Data-ATS")
    iot_endpoint = endpoint_response["endpointAddress"]
    print(f"✅ Endpoint: {iot_endpoint}")
except Exception as e:
    print(f"❌ Endpoint hatası: {e}")
    exit(1)

# ============================================================
# ADIM 2: IoT Policy oluştur
# ============================================================
print("\n🔐 ADIM 2: IoT Policy oluştur...")

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:Connect"
            ],
            "Resource": f"arn:aws:iot:{REGION}:*:client/smart-city-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iot:Publish"
            ],
            "Resource": f"arn:aws:iot:{REGION}:*:topicname/smart-city/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iot:Subscribe"
            ],
            "Resource": f"arn:aws:iot:{REGION}:*:topicname/smart-city/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iot:Receive"
            ],
            "Resource": f"arn:aws:iot:{REGION}:*:topicname/smart-city/*"
        }
    ]
}

try:
    # Check if policy exists
    try:
        iot_client.get_policy(policyName=POLICY_NAME)
        print(f"ℹ️  Policy zaten var: {POLICY_NAME}")
    except iot_client.exceptions.ResourceNotFoundException:
        # Create policy
        iot_client.create_policy(
            policyName=POLICY_NAME,
            policyDocument=json.dumps(policy_document)
        )
        print(f"✅ Policy oluşturuldu: {POLICY_NAME}")
except Exception as e:
    print(f"❌ Policy hatası: {e}")

# ============================================================
# ADIM 3: Thing oluştur (3 sensör cihazı)
# ============================================================
print("\n🔌 ADIM 3: IoT Things oluştur...")

devices = [
    "traffic-light-001",
    "air-quality-001",
    "trash-bin-001"
]

created_things = []
for device_id in devices:
    try:
        # Check if thing exists
        try:
            iot_client.describe_thing(thingName=device_id)
            print(f"ℹ️  Thing zaten var: {device_id}")
        except iot_client.exceptions.ResourceNotFoundException:
            # Create thing
            iot_client.create_thing(thingName=device_id)
            created_things.append(device_id)
            print(f"✅ Thing oluşturuldu: {device_id}")
    except Exception as e:
        print(f"❌ Thing hatası ({device_id}): {e}")

# ============================================================
# ADIM 4: Certificate ve Keys oluştur
# ============================================================
print("\n🔑 ADIM 4: X.509 Certificates oluştur...")

try:
    cert_response = iot_client.create_keys_and_certificate(setAsActive=True)
    
    cert_id = cert_response["certificateId"]
    cert_arn = cert_response["certificateArn"]
    cert_pem = cert_response["certificatePem"]
    private_key = cert_response["keyPair"]["PrivateKey"]
    
    # Save certificate files
    cert_file = CERT_DIR / "device.crt"
    key_file = CERT_DIR / "private.key"
    
    with open(cert_file, "w") as f:
        f.write(cert_pem)
    print(f"✅ Sertifika kaydedildi: {cert_file}")
    
    with open(key_file, "w") as f:
        f.write(private_key)
    print(f"✅ Private Key kaydedildi: {key_file}")
    
    # Download Root CA
    ca_file = CERT_DIR / "AmazonRootCA1.pem"
    if not ca_file.exists():
        print("⏳ Root CA indiriliyor...")
        import urllib.request
        url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
        try:
            urllib.request.urlretrieve(url, ca_file)
            print(f"✅ Root CA kaydedildi: {ca_file}")
        except Exception as e:
            print(f"⚠️  Root CA indirilemedi: {e}")
    else:
        print(f"ℹ️  Root CA zaten var: {ca_file}")
    
except Exception as e:
    print(f"❌ Certificate hatası: {e}")
    exit(1)

# ============================================================
# ADIM 5: Certificate'ı Things'e bağla
# ============================================================
print("\n🔗 ADIM 5: Certificate'ları Things'e bağla...")

try:
    for device_id in devices:
        try:
            iot_client.attach_principal_policy(
                policyName=POLICY_NAME,
                principal=cert_arn
            )
            print(f"✅ Policy bağlandı: {device_id}")
        except iot_client.exceptions.PolicyVersionNotSetAsDefaultException:
            print(f"⚠️  Policy version set required")
        except Exception as e:
            if "already attached" not in str(e):
                print(f"⚠️  Policy bağlanması hatası: {e}")
    
    # Attach certificate to thing (if not already attached to a principal policy)
    try:
        iot_client.attach_thing_principal(
            thingName=devices[0],
            principal=cert_arn
        )
        print(f"✅ Certificate Thing'e bağlandı")
    except Exception as e:
        if "already attached" not in str(e):
            print(f"⚠️  Thing bağlanması: {e}")
            
except Exception as e:
    print(f"❌ Bağlanma hatası: {e}")

# ============================================================
# ADIM 6: .env dosyasını güncelle
# ============================================================
print("\n📝 ADIM 6: .env dosyasını güncelle...")

env_updates = {
    "AWS_REGION": REGION,
    "AWS_IOT_ENDPOINT": iot_endpoint,
    "IOT_CERT_FILE": str(cert_file.relative_to(Path.cwd())),
    "IOT_KEY_FILE": str(key_file.relative_to(Path.cwd())),
    "IOT_CA_FILE": str(ca_file.relative_to(Path.cwd())),
    "MQTT_BROKER": iot_endpoint,
    "MOCK_MODE": "false"  # Disable mock mode
}

for key, value in env_updates.items():
    set_key(".env", key, value)
    print(f"✅ {key} = {value}")

print("\n" + "="*60)
print("✨ AWS IoT Setup Başarılı!")
print("="*60)
print(f"""
📊 Oluşturulan Kaynaklar:
  • Policy: {POLICY_NAME}
  • Things: {', '.join(devices)}
  • Certificate ID: {cert_id}
  • Endpoint: {iot_endpoint}

📁 Sertifikalar:
  • {cert_file}
  • {key_file}
  • {ca_file}

🚀 Sonraki Adımlar:
  1. DynamoDB tablolarını oluştur: 
     python -c "from config.dynamodb_schema import create_tables; create_tables()"
  
  2. Lambda fonksiyonunu deploy et:
     python config/lambda_deployment.py
  
  3. IoT Rule Engine oluştur:
     python config/iot_rule_engine.py
  
  4. Sensör simülatörünü çalıştır:
     python sensor_simulator.py --duration 300
  
  5. API'yi başlat:
     python src/api/app.py

📚 Daha Fazla İlgi:
  • AWS IoT Console: https://console.aws.amazon.com/iot
  • Region: {REGION}
""")


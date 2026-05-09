"""
IoT Core Rule Engine Configuration
AWS IoT Core Rule Engine'inde MQTT → Lambda/DynamoDB yönlendirmesi

Bu konfigürasyonlar AWS Console'da manuel olarak yapılır,
veya aşağıdaki CLI komutları kullanılır.
"""

# ============================================================
# AWS IoT Core Rule Engine - Rule Definition
# ============================================================

RULE_CONFIG = """
Rule Name: SmartCitySensorToDatabase

SQL Statement:
SELECT 
    timestamp() as timestamp,
    clientId() as device,
    topic(3) as metric,
    * as metadata
FROM 'smart-city/+/+/+'

Actions:
1. Lambda Action:
   - Function ARN: arn:aws:lambda:eu-central-1:ACCOUNT_ID:function:iot-to-dynamodb
   - Role: IoT Core Lambda Invoke Role

Description:
- Topic pattern: smart-city/{sensor_type}/{device_id}/{metric}
- Örnek: smart-city/traffic_light/traffic-light-001/congestion
- Her mesaj Lambda fonksiyonuna gönderilir
- Lambda: DynamoDB'ye kayıt ve uyarı kontrol
"""

# ============================================================
# AWS CLI Komutları
# ============================================================

CLI_CREATE_RULE = """
# 1. IoT Core Rule'u oluştur
aws iot create-topic-rule \\
  --rule-name SmartCitySensorToDatabase \\
  --topic-rule-payload '{
    "sql": "SELECT timestamp() as ts, clientId() as device, topic(3) as metric, * FROM '\''smart-city/+/+/+'\''",
    "actions": [
      {
        "lambda": {
          "functionArn": "arn:aws:lambda:eu-central-1:ACCOUNT_ID:function:iot-to-dynamodb"
        }
      }
    ],
    "ruleDisabled": false
  }' \\
  --region eu-central-1

# 2. Rule'ı kontrol et
aws iot get-topic-rule \\
  --rule-name SmartCitySensorToDatabase \\
  --region eu-central-1

# 3. Lambda Permission'u ekle (Rule'ın Lambda'yı invoke edebilmesi için)
aws lambda add-permission \\
  --function-name iot-to-dynamodb \\
  --statement-id AllowIoTInvoke \\
  --action lambda:InvokeFunction \\
  --principal iot.amazonaws.com \\
  --source-arn arn:aws:iot:eu-central-1:ACCOUNT_ID:rule/SmartCitySensorToDatabase \\
  --region eu-central-1

# 4. Rule'ları listele
aws iot list-topic-rules --region eu-central-1
"""

# ============================================================
# Topic Pattern Açıklaması
# ============================================================

TOPIC_PATTERN = """
Topic Pattern: smart-city/{sensor_type}/{device_id}/{metric}

Açıklama:
- smart-city/          : Root prefix (tüm cihazlar)
- {sensor_type}        : traffic_light, air_quality, trash_bin
- {device_id}          : Cihaz ID'si (traffic-light-001 vb.)
- {metric}             : Ölçüm adı (congestion, pm25, fill_level vb.)

Örnekler:
✓ smart-city/traffic_light/traffic-light-001/congestion
✓ smart-city/air_quality/air-quality-001/pm25
✓ smart-city/trash_bin/trash-bin-001/fill_level

SQL Query:
SELECT 
    timestamp() as ts,           # MQTT mesajın sunucu zamanı
    clientId() as device,        # MQTT client ID (device ID'si)
    topic(1) as root,            # "smart-city"
    topic(2) as sensor_type,     # "traffic_light" vb.
    topic(3) as device_id,       # "traffic-light-001" vb.
    topic(4) as metric,          # "congestion" vb.
    * as metadata                # Tüm message payload
FROM 'smart-city/+/+/+'         # Wildcard pattern
"""

# ============================================================
# Message Flow Diyagramı
# ============================================================

MESSAGE_FLOW = """
IoT Device (Python MQTT Client)
    ↓
    Publish: smart-city/traffic_light/traffic-light-001/congestion
    Payload: {
      "value": 65.5,
      "location": "Main Street",
      "status": "red"
    }
    ↓
AWS IoT Core (MQTT Broker)
    ↓
    Rule Engine: SmartCitySensorToDatabase
    SQL Match: SELECT ... FROM 'smart-city/+/+/+'
    ↓
AWS Lambda: iot-to-dynamodb
    ↓
    1. Parse event
    2. Save to DynamoDB (sensor-readings)
    3. Check thresholds
    4. Create alert if needed (sensor-alerts)
    ↓
DynamoDB
    ├─ smart-city-sensor-readings (timeseries data)
    ├─ smart-city-sensor-alerts (anomalies)
    └─ smart-city-sensor-stats (aggregates)
"""

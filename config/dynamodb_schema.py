"""
DynamoDB Schema Definition
DynamoDB tabloları için schema tanımları ve bilgiler

Tablolar:
1. sensor_readings - Sensör ölçümlerinin depolandığı ana tablo
2. sensor_alerts - Uyarılar ve kritik durumlar
3. sensor_stats - Saatlik/günlük istatistikler
"""

# ============================================================
# TABLO 1: sensor_readings
# ============================================================
"""
Amaç: Tüm sensör ölçümlerini depolama
Partition Key: sensor_type#device_id (e.g., "traffic_light#traffic-light-001")
Sort Key: timestamp (ISO format)

Yapı:
{
    "pk": "traffic_light#traffic-light-001",        // Partition Key
    "sk": "2026-05-09T13:48:00Z",                   // Sort Key (timestamp)
    "device_id": "traffic-light-001",
    "sensor_type": "traffic_light",
    "metric": "congestion",
    "value": 65.5,
    "location": "Main Street",
    "timestamp": "2026-05-09T13:48:00Z",
    "metadata": {
        "status": "red",
        "vehicle_count": 150,
        "speed": 45.5
    },
    "ttl": 1715335680                              // 30 gün sonra otomatik sil
}

Index:
- GSI: sensor_type-timestamp-index
  - Partition Key: sensor_type
  - Sort Key: timestamp
  - Benefit: Sensör türüne göre tarih aralığında sorgulama

- GSI: location-timestamp-index
  - Partition Key: location
  - Sort Key: timestamp
  - Benefit: Lokasyona göre son ölçümleri bulma
"""

# ============================================================
# TABLO 2: sensor_alerts
# ============================================================
"""
Amaç: Uyarılar ve anomalileri kaydetme
Partition Key: alert_type (e.g., "high_traffic", "poor_air")
Sort Key: timestamp

Yapı:
{
    "pk": "high_congestion",                        // Partition Key
    "sk": "2026-05-09T13:48:00Z",                   // Sort Key
    "alert_id": "alert_2026050913_001",
    "device_id": "traffic-light-001",
    "severity": "high",                             // low, medium, high, critical
    "message": "Trafik yoğunluğu 85% aştı!",
    "threshold": 85,
    "current_value": 92.5,
    "timestamp": "2026-05-09T13:48:00Z",
    "resolved": false,
    "resolved_at": null,
    "ttl": 1715335680                              // 30 gün
}

Possible alerts:
- high_congestion: Trafik %85+ → Critical
- poor_air_quality: AQI 200+ → Critical
- bin_full: Çöp %90+ → High
- unusual_pattern: Olası arıza → Medium
"""

# ============================================================
# TABLO 3: sensor_stats
# ============================================================
"""
Amaç: Aggregated istatistikler (1 saatlik ortalamalar)
Partition Key: sensor_type#device_id
Sort Key: period (e.g., "2026-05-09T13:00:00Z")

Yapı:
{
    "pk": "traffic_light#traffic-light-001",       // Partition Key
    "sk": "2026-05-09T13:00:00Z",                   // Sort Key (saat başı)
    "period": "2026-05-09T13:00:00Z",
    "measurement_count": 12,                        // Kaç ölçüm
    "avg_value": 65.5,
    "min_value": 42.0,
    "max_value": 89.5,
    "stddev": 14.2,
    "sensor_type": "traffic_light",
    "device_id": "traffic-light-001",
    "ttl": null                                    // Unlimited (historical data)
}

Benefit: Hızlı trend analizi, grafik çizimi
"""

# ============================================================
# CloudFormation / IaC Template (Python)
# ============================================================

DYNAMODB_TABLES = {
    "sensor_readings": {
        "TableName": "smart-city-sensor-readings",
        "BillingMode": "PAY_PER_REQUEST",  # On-demand pricing
        "AttributeDefinitions": [
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "sensor_type", "AttributeType": "S"},
            {"AttributeName": "location", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "pk", "KeyType": "HASH"},  # Partition Key
            {"AttributeName": "sk", "KeyType": "RANGE"},  # Sort Key
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "sensor-type-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "sensor_type", "KeyType": "HASH"},
                    {"AttributeName": "sk", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "location-timestamp-index",
                "KeySchema": [
                    {"AttributeName": "location", "KeyType": "HASH"},
                    {"AttributeName": "sk", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "TimeToLiveSpecification": {
            "AttributeName": "ttl",
            "Enabled": True,
        },
    },
    "sensor_alerts": {
        "TableName": "smart-city-sensor-alerts",
        "BillingMode": "PAY_PER_REQUEST",
        "AttributeDefinitions": [
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        "TimeToLiveSpecification": {
            "AttributeName": "ttl",
            "Enabled": True,
        },
    },
    "sensor_stats": {
        "TableName": "smart-city-sensor-stats",
        "BillingMode": "PAY_PER_REQUEST",
        "AttributeDefinitions": [
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        "KeySchema": [
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
    },
}

# ============================================================
# AWS CLI Commands for DynamoDB Creation
# ============================================================

CLI_COMMANDS = """
# 1. sensor_readings tablosu oluştur
aws dynamodb create-table \\
  --table-name smart-city-sensor-readings \\
  --attribute-definitions \\
    AttributeName=pk,AttributeType=S \\
    AttributeName=sk,AttributeType=S \\
    AttributeName=sensor_type,AttributeType=S \\
    AttributeName=location,AttributeType=S \\
  --key-schema \\
    AttributeName=pk,KeyType=HASH \\
    AttributeName=sk,KeyType=RANGE \\
  --billing-mode PAY_PER_REQUEST \\
  --global-secondary-indexes \\
    "IndexName=sensor-type-timestamp-index,KeySchema=[{AttributeName=sensor_type,KeyType=HASH},{AttributeName=sk,KeyType=RANGE}],Projection={ProjectionType=ALL}" \\
    "IndexName=location-timestamp-index,KeySchema=[{AttributeName=location,KeyType=HASH},{AttributeName=sk,KeyType=RANGE}],Projection={ProjectionType=ALL}" \\
  --time-to-live-specification Enabled=true,AttributeName=ttl \\
  --region eu-central-1

# 2. sensor_alerts tablosu oluştur
aws dynamodb create-table \\
  --table-name smart-city-sensor-alerts \\
  --attribute-definitions \\
    AttributeName=pk,AttributeType=S \\
    AttributeName=sk,AttributeType=S \\
  --key-schema \\
    AttributeName=pk,KeyType=HASH \\
    AttributeName=sk,KeyType=RANGE \\
  --billing-mode PAY_PER_REQUEST \\
  --time-to-live-specification Enabled=true,AttributeName=ttl \\
  --region eu-central-1

# 3. sensor_stats tablosu oluştur
aws dynamodb create-table \\
  --table-name smart-city-sensor-stats \\
  --attribute-definitions \\
    AttributeName=pk,AttributeType=S \\
    AttributeName=sk,AttributeType=S \\
  --key-schema \\
    AttributeName=pk,KeyType=HASH \\
    AttributeName=sk,KeyType=RANGE \\
  --billing-mode PAY_PER_REQUEST \\
  --region eu-central-1

# 4. Tabloların oluşturulmasını kontrol et
aws dynamodb list-tables --region eu-central-1
"""

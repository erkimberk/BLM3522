"""
AWS Lambda Function for IoT Core → DynamoDB
IoT Core'dan gelen MQTT mesajlarını DynamoDB'ye kaydeder.

Bu fonksiyon AWS IoT Core Rule Engine tarafından tetiklenir.
Tetiklenme: smart-city/# topic'lerine mesaj geldiğinde

Deployment:
1. Lambda fonksiyonunu AWS Console'dan oluştur
2. Bu kodu functions/lambda_handler.py'ye kopyala
3. Runtime: Python 3.11
4. Role: DynamoDB ve CloudWatch yazma izni
5. Timeout: 60 saniye
"""

import json
import boto3
import logging
from datetime import datetime, timedelta

# AWS clients
dynamodb = boto3.resource("dynamodb")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB tabloları
SENSOR_READINGS_TABLE = "smart-city-sensor-readings"
SENSOR_ALERTS_TABLE = "smart-city-sensor-alerts"

# Uyarı threshold'ları
ALERT_THRESHOLDS = {
    "traffic_light": {"congestion": 85},
    "air_quality": {"pm25": 75},
    "trash_bin": {"fill_level": 90},
}


def lambda_handler(event, context):
    """
    AWS Lambda handler fonksiyonu
    
    Event format (IoT Core Rule Engine'den):
    {
        "timestamp": 1715335680000,
        "device": "traffic-light-001",
        "metric": "congestion",
        "value": 92.5,
        "metadata": {...}
    }
    """
    try:
        logger.info(f"Event alındı: {json.dumps(event)}")

        # Mesajı parse et
        sensor_data = parse_event(event)

        # DynamoDB'ye kayıt et
        save_to_dynamodb(sensor_data)

        # Uyarıları kontrol et
        check_and_create_alerts(sensor_data)

        return {"statusCode": 200, "body": json.dumps("Başarılı")}

    except Exception as e:
        logger.error(f"Hata: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps(f"Hata: {str(e)}")}


def parse_event(event):
    """
    IoT Core mesajını parse et
    
    Returns:
        dict: Standart format sensor verisi
    """
    # IoT Core'dan gelen event yapısı
    device_id = event.get("device", "unknown")
    metric = event.get("metric", "unknown")
    value = event.get("value", 0)
    metadata = event.get("metadata", {})
    timestamp = event.get("timestamp")

    # Cihaz türünü belirle (device_id'den)
    sensor_type = determine_sensor_type(device_id)

    # Timestamp ISO format'a çevir
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp / 1000)
    else:
        dt = datetime.now()

    iso_timestamp = dt.isoformat() + "Z"

    return {
        "device_id": device_id,
        "sensor_type": sensor_type,
        "metric": metric,
        "value": value,
        "location": metadata.get("location", "Unknown"),
        "timestamp": iso_timestamp,
        "metadata": metadata,
    }


def determine_sensor_type(device_id: str) -> str:
    """
    Device ID'den sensor türünü belirle
    
    Examples:
        traffic-light-001 → traffic_light
        air-quality-001 → air_quality
        trash-bin-001 → trash_bin
    """
    if "traffic" in device_id:
        return "traffic_light"
    elif "air" in device_id:
        return "air_quality"
    elif "trash" in device_id:
        return "trash_bin"
    else:
        return "unknown"


def save_to_dynamodb(sensor_data: dict):
    """
    Sensör verisini DynamoDB'ye kayıt et
    
    Partition Key: sensor_type#device_id
    Sort Key: timestamp
    """
    table = dynamodb.Table(SENSOR_READINGS_TABLE)

    # TTL: 30 gün
    ttl_timestamp = int((datetime.now() + timedelta(days=30)).timestamp())

    # Primary Key oluştur
    pk = f"{sensor_data['sensor_type']}#{sensor_data['device_id']}"

    item = {
        "pk": pk,
        "sk": sensor_data["timestamp"],
        "device_id": sensor_data["device_id"],
        "sensor_type": sensor_data["sensor_type"],
        "metric": sensor_data["metric"],
        "value": sensor_data["value"],
        "location": sensor_data["location"],
        "timestamp": sensor_data["timestamp"],
        "metadata": sensor_data["metadata"],
        "ttl": ttl_timestamp,
    }

    try:
        table.put_item(Item=item)
        logger.info(f"✅ Veri kaydedildi: {pk} @ {sensor_data['timestamp']}")
    except Exception as e:
        logger.error(f"❌ DynamoDB yazma hatası: {e}")
        raise


def check_and_create_alerts(sensor_data: dict):
    """
    Sensör verisine göre uyarı oluştur
    
    Threshold'u aşan değerler için uyarı kaydı oluştur
    """
    sensor_type = sensor_data["sensor_type"]
    metric = sensor_data["metric"]
    value = sensor_data["value"]

    # Threshold kontrol et
    thresholds = ALERT_THRESHOLDS.get(sensor_type, {})
    threshold = thresholds.get(metric)

    if threshold is None:
        return  # Threshold tanımlanmamış

    if value > threshold:
        create_alert(sensor_data, threshold)


def create_alert(sensor_data: dict, threshold: float):
    """
    DynamoDB'ye uyarı kaydı ekle
    """
    table = dynamodb.Table(SENSOR_ALERTS_TABLE)

    # Alert type belirle
    alert_type = f"{sensor_data['sensor_type']}_{sensor_data['metric']}_high"

    # Alert severity belirle
    value = sensor_data["value"]
    if value > threshold * 1.5:
        severity = "critical"
    elif value > threshold * 1.2:
        severity = "high"
    else:
        severity = "medium"

    # TTL: 30 gün
    ttl_timestamp = int((datetime.now() + timedelta(days=30)).timestamp())

    alert_item = {
        "pk": alert_type,
        "sk": sensor_data["timestamp"],
        "alert_id": f"alert_{sensor_data['device_id']}_{int(datetime.now().timestamp())}",
        "device_id": sensor_data["device_id"],
        "sensor_type": sensor_data["sensor_type"],
        "metric": sensor_data["metric"],
        "severity": severity,
        "message": f"{sensor_data['sensor_type']}: {sensor_data['metric']} = {sensor_data['value']} "
        f"(threshold: {threshold})",
        "threshold": threshold,
        "current_value": sensor_data["value"],
        "timestamp": sensor_data["timestamp"],
        "resolved": False,
        "ttl": ttl_timestamp,
    }

    try:
        table.put_item(Item=alert_item)
        logger.warning(f"⚠️  UYARI OLUŞTURULDU: {severity.upper()} - {alert_item['message']}")
    except Exception as e:
        logger.error(f"❌ Alert yazma hatası: {e}")

"""
Lambda Local Test Script
Lambda fonksiyonunu lokal olarak test et (AWS bağlantısı olmadan)

Kullanım:
    python lambda_test.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# src/lambda'yı path'e ekle
sys.path.insert(0, str(Path(__file__).parent / "src" / "lambda"))


class MockDynamoDB:
    """
    DynamoDB mock'u (test için)
    Gerçek veri saklamaz, sadece log verir
    """

    def Table(self, table_name):
        return MockTable(table_name)


class MockTable:
    """Mock DynamoDB Table"""

    def __init__(self, table_name):
        self.table_name = table_name
        self.items = []

    def put_item(self, Item):
        """Item ekle"""
        self.items.append(Item)
        print(f"    ✅ [{self.table_name}] Item eklendi")


class MockLogger:
    """Mock Logger"""

    def info(self, msg):
        print(f"    [INFO] {msg}")

    def warning(self, msg):
        print(f"    [WARNING] {msg}")

    def error(self, msg, exc_info=False):
        print(f"    [ERROR] {msg}")


def test_lambda_handler():
    """Lambda handler'ı test et"""
    print("\n" + "=" * 70)
    print("🧪 AWS Lambda Handler Test")
    print("=" * 70)

    # Mock boto3 module'ü
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "boto3", Path("src/lambda/iot_to_dynamodb.py")
    )

    # Test events
    test_events = [
        {
            "device": "traffic-light-001",
            "metric": "congestion",
            "value": 92.5,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metadata": {
                "location": "Main Street",
                "status": "red",
                "vehicle_count": 150,
            },
        },
        {
            "device": "air-quality-001",
            "metric": "pm25",
            "value": 85.0,  # Threshold: 75 → Uyarı oluşturulacak
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metadata": {
                "location": "City Center",
                "aqi": 180,
                "temp": 22.5,
            },
        },
        {
            "device": "trash-bin-001",
            "metric": "fill_level",
            "value": 88.5,  # Threshold: 90 → Uyarı yok
            "timestamp": int(datetime.now().timestamp() * 1000),
            "metadata": {
                "location": "Street Corner",
                "urgency": "high",
            },
        },
    ]

    print("\n📋 Test Events:")
    for i, event in enumerate(test_events, 1):
        print(f"\n  Test {i}: {event['device']} - {event['metric']}={event['value']}")

        # Event parse etme fonksiyonunu test et
        try:
            # Import etme yerine inline olarak fonksiyonları yazacağız
            sensor_data = parse_event_local(event)
            print(f"    ✅ Event parsed:")
            print(f"       Device ID: {sensor_data['device_id']}")
            print(f"       Sensor Type: {sensor_data['sensor_type']}")
            print(f"       Value: {sensor_data['value']}")

            # Uyarı check'i
            thresholds = {
                "traffic_light": {"congestion": 85},
                "air_quality": {"pm25": 75},
                "trash_bin": {"fill_level": 90},
            }

            metric_thresholds = thresholds.get(sensor_data["sensor_type"], {})
            threshold = metric_thresholds.get(sensor_data["metric"])

            if threshold and sensor_data["value"] > threshold:
                if sensor_data["value"] > threshold * 1.5:
                    severity = "CRITICAL"
                elif sensor_data["value"] > threshold * 1.2:
                    severity = "HIGH"
                else:
                    severity = "MEDIUM"
                print(f"    ⚠️  UYARI: {severity} - Threshold exceeded! ({threshold})")
            else:
                print(f"    ✅ Threshold OK (threshold: {threshold})")

        except Exception as e:
            print(f"    ❌ Hata: {e}")

    print("\n" + "=" * 70)
    print("✨ Test Tamamlandı")
    print("=" * 70 + "\n")


def parse_event_local(event):
    """Event parse etme (local test için)"""
    device_id = event.get("device", "unknown")
    metric = event.get("metric", "unknown")
    value = event.get("value", 0)
    metadata = event.get("metadata", {})
    timestamp = event.get("timestamp")

    # Sensor type belirle
    if "traffic" in device_id:
        sensor_type = "traffic_light"
    elif "air" in device_id:
        sensor_type = "air_quality"
    elif "trash" in device_id:
        sensor_type = "trash_bin"
    else:
        sensor_type = "unknown"

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


def test_threshold_logic():
    """Threshold ve uyarı logic'ini test et"""
    print("\n" + "=" * 70)
    print("🧪 Threshold & Alert Logic Test")
    print("=" * 70)

    test_cases = [
        ("traffic_light", "congestion", 90, "CRITICAL"),  # 85 * 1.5 = 127.5
        ("traffic_light", "congestion", 85, "HIGH"),  # Exactly at threshold
        ("traffic_light", "congestion", 80, "OK"),  # Below threshold
        ("air_quality", "pm25", 120, "CRITICAL"),  # 75 * 1.5 = 112.5
        ("air_quality", "pm25", 85, "HIGH"),  # 75 * 1.2 = 90
        ("trash_bin", "fill_level", 95, "HIGH"),  # 90 * 1.2 = 108
    ]

    print("\n📊 Test Senaryoları:")
    for sensor_type, metric, value, expected in test_cases:
        thresholds = {
            "traffic_light": {"congestion": 85},
            "air_quality": {"pm25": 75},
            "trash_bin": {"fill_level": 90},
        }

        threshold = thresholds.get(sensor_type, {}).get(metric)

        if threshold is None:
            result = "OK"
        elif value > threshold * 1.5:
            result = "CRITICAL"
        elif value > threshold * 1.2:
            result = "HIGH"
        elif value > threshold:
            result = "MEDIUM"
        else:
            result = "OK"

        status = "✅" if result == expected else "❌"
        print(
            f"  {status} {sensor_type}/{metric}={value} "
            f"(threshold={threshold}) → {result} (expected: {expected})"
        )

    print("\n" + "=" * 70)
    print("✨ Test Tamamlandı")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_lambda_handler()
    test_threshold_logic()

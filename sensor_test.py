"""
Sensor Test Script
Sensörlerin veri üretimini test et (AWS bağlantısı olmadan)

Kullanım:
    python sensor_test.py
"""

import sys
from pathlib import Path
import json

# src/devices'ı path'e ekle
sys.path.insert(0, str(Path(__file__).parent / "src" / "devices"))

from traffic_light_sensor import TrafficLightSensor
from air_quality_sensor import AirQualitySensor
from trash_bin_sensor import TrashBinSensor


def test_sensors():
    """Sensörleri test et ve örnek çıktılar göster"""
    print("\n" + "=" * 70)
    print("🧪 IoT SENSÖR TEST")
    print("=" * 70)

    # 1. Traffic Light Sensor
    print("\n🚦 TRAFFIC LIGHT SENSOR")
    print("-" * 70)
    traffic = TrafficLightSensor("Main Street")

    # Normal durum
    print("\nNormal Durum (Off-peak):")
    traffic.set_peak_hour(False)
    for i in range(3):
        data = traffic.generate_data()
        print(f"\n  Ölçüm {i+1}:")
        print(f"    Yoğunluk: {data['congestion_percent']}%")
        print(f"    Durum: {data['status']}")
        print(f"    Araç Sayısı: {data['vehicle_count_5min']}")
        print(f"    Ort. Hız: {data['average_speed_kmh']} km/h")

    # Peak hour
    print("\nRush Hour (Peak):")
    traffic.set_peak_hour(True)
    for i in range(3):
        data = traffic.generate_data()
        print(f"\n  Ölçüm {i+1}:")
        print(f"    Yoğunluk: {data['congestion_percent']}%")
        print(f"    Durum: {data['status']}")
        print(f"    Araç Sayısı: {data['vehicle_count_5min']}")
        print(f"    Ort. Hız: {data['average_speed_kmh']} km/h")

    # 2. Air Quality Sensor
    print("\n\n💨 AIR QUALITY SENSOR")
    print("-" * 70)
    air = AirQualitySensor("City Center")

    # Normal durum
    print("\nNormal Hava Kalitesi:")
    air.set_pollution_level(False)
    for i in range(3):
        data = air.generate_data()
        print(f"\n  Ölçüm {i+1}:")
        print(f"    PM2.5: {data['pm25_ug_m3']} µg/m³")
        print(f"    PM10: {data['pm10_ug_m3']} µg/m³")
        print(f"    CO2: {data['co2_ppm']} ppm")
        print(f"    Sıcaklık: {data['temperature_celsius']} °C")
        print(f"    Nemlilik: {data['humidity_percent']} %")
        print(f"    AQI: {data['aqi']} ({data['aqi_category']})")

    # Yüksek kirlilik
    print("\nYüksek Kirlilik Seviyesi:")
    air.set_pollution_level(True)
    for i in range(3):
        data = air.generate_data()
        print(f"\n  Ölçüm {i+1}:")
        print(f"    PM2.5: {data['pm25_ug_m3']} µg/m³")
        print(f"    PM10: {data['pm10_ug_m3']} µg/m³")
        print(f"    AQI: {data['aqi']} ({data['aqi_category']})")

    # 3. Trash Bin Sensor
    print("\n\n🗑️  TRASH BIN SENSOR")
    print("-" * 70)
    trash = TrashBinSensor("Street Corner", max_weight_kg=50)

    print("\nÇöp Kutusu Doluluk Simülasyonu (10 ölçüm):")
    for i in range(10):
        data = trash.generate_data()
        urgency_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }
        emoji = urgency_emoji.get(data["collection_urgency"], "?")

        print(f"\n  Ölçüm {i+1}: {emoji}")
        print(f"    Doluluk: {data['fill_percentage']:.1f}%")
        print(f"    Ağırlık: {data['weight_kg']:.2f} kg")
        print(f"    Günlük Birikinti: {data['daily_accumulation_kg']:.2f} kg")
        print(f"    Aciliyet: {data['collection_urgency'].upper()}")
        if data["collection_needed"]:
            print(f"    ⚠️  COLLECTION REQUIRED!")

    print("\n" + "=" * 70)
    print("✅ TEST TAMAMLANDI")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_sensors()

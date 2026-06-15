"""
DynamoDB Query Helper Functions
DynamoDB'den veri sorgulama yardımcı fonksiyonları

Bu modül frontend ve analiz scripti tarafından kullanılır.
Mock mode devre dışı - sadece AWS'den gerçek veri çeker!
"""

import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import random

# Lokal mock mode - DEVRE DIŞI (sadece gerçek AWS verisi)
MOCK_MODE = False  # Hiçbir zaman mock data kullanma!

try:
    if MOCK_MODE:
        dynamodb = None
    else:
        dynamodb = boto3.resource("dynamodb")
except Exception as e:
    print(f"⚠️  DynamoDB bağlantısı başarısız, mock mode kullanılıyor: {e}")
    MOCK_MODE = True
    dynamodb = None


def _generate_mock_traffic_data(count: int = 20) -> List[Dict]:
    """Sahte traffic light verisi oluştur"""
    data = []
    now = datetime.now()
    for i in range(count):
        ts = now - timedelta(minutes=i*5)
        value = random.uniform(10, 95)
        data.append({
            "pk": "traffic_light#traffic-light-001",
            "sk": ts.isoformat() + "Z",
            "timestamp": ts.isoformat() + "Z",
            "sensor_type": "traffic_light",
            "device_id": "traffic-light-001",
            "metric": "congestion",
            "value": round(value, 2),
            "metadata": {
                "location": "Main Street",
                "status": "green" if value < 33 else "yellow" if value < 66 else "red",
                "vehicle_count": random.randint(200, 1500),
                "avg_speed": round(random.uniform(20, 80), 1)
            }
        })
    return sorted(data, key=lambda x: x["timestamp"], reverse=True)


def _generate_mock_air_data(count: int = 20) -> List[Dict]:
    """Sahte air quality verisi oluştur"""
    data = []
    now = datetime.now()
    for i in range(count):
        ts = now - timedelta(minutes=i*5)
        pm25 = random.uniform(20, 150)
        aqi = int(pm25 * 1.2)
        data.append({
            "pk": "air_quality#air-quality-001",
            "sk": ts.isoformat() + "Z",
            "timestamp": ts.isoformat() + "Z",
            "sensor_type": "air_quality",
            "device_id": "air-quality-001",
            "metric": "pm25",
            "value": round(pm25, 2),
            "metadata": {
                "location": "Downtown",
                "pm10": round(pm25 * 2.5, 2),
                "co2": random.randint(400, 800),
                "temperature": round(random.uniform(15, 30), 1),
                "humidity": random.randint(30, 80),
                "aqi": aqi,
                "category": "Good" if aqi < 50 else "Fair" if aqi < 100 else "Moderate" if aqi < 150 else "Poor"
            }
        })
    return sorted(data, key=lambda x: x["timestamp"], reverse=True)


def _generate_mock_trash_data(count: int = 20) -> List[Dict]:
    """Sahte trash bin verisi oluştur"""
    data = []
    now = datetime.now()
    weight = 0
    for i in range(count):
        ts = now - timedelta(minutes=i*5)
        weight += random.uniform(0.5, 3)
        fill_pct = min(weight / 100 * 100, 95)
        
        data.append({
            "pk": "trash_bin#trash-bin-001",
            "sk": ts.isoformat() + "Z",
            "timestamp": ts.isoformat() + "Z",
            "sensor_type": "trash_bin",
            "device_id": "trash-bin-001",
            "metric": "fill_level",
            "value": round(fill_pct, 2),
            "metadata": {
                "location": "Park Street",
                "weight_kg": round(weight, 2),
                "collection_needed": fill_pct > 85,
                "urgency": "critical" if fill_pct > 90 else "high" if fill_pct > 75 else "medium" if fill_pct > 50 else "low"
            }
        })
    return sorted(data, key=lambda x: x["timestamp"], reverse=True)


def _generate_mock_alerts(count: int = 5) -> List[Dict]:
    """Sahte uyarılar oluştur"""
    alerts = []
    now = datetime.now()
    
    alert_types = [
        {"type": "high_congestion", "severity": "critical", "message": "Trafik yoğunluğu kritik seviyeye ulaştı", "device": "traffic-light-001"},
        {"type": "poor_air_quality", "severity": "high", "message": "Hava kalitesi kötü", "device": "air-quality-001"},
        {"type": "trash_full", "severity": "high", "message": "Çöp kutusu doluluk %90'ı aştı", "device": "trash-bin-001"},
    ]
    
    for i, alert_type in enumerate(alert_types[:count]):
        ts = now - timedelta(hours=i*2)
        alerts.append({
            "alert_id": f"alert-{i+1}",
            "timestamp": ts.isoformat() + "Z",
            "device_id": alert_type["device"],
            "alert_type": alert_type["type"],
            "severity": alert_type["severity"],
            "message": alert_type["message"],
            "value": random.uniform(75, 150),
            "threshold": 85,
            "resolved": False
        })
    
    return alerts


class SensorDataQuery:
    """DynamoDB'den sensör verilerini sorgula (ya da mock data döndür)"""

    def __init__(self, region: str = "eu-central-1"):
        """
        Başlat
        
        Args:
            region: AWS bölgesi
        """
        self.region = region
        self.mock_mode = MOCK_MODE
        
        try:
            self.dynamodb = boto3.resource("dynamodb", region_name=region)
            self.readings_table = self.dynamodb.Table("smart-city-sensor-readings")
            self.alerts_table = self.dynamodb.Table("smart-city-sensor-alerts")
            print("✅ DynamoDB'ye bağlanıldı")
        except Exception as e:
            print(f"⚠️  DynamoDB bağlantı hatası: {e}")
            raise Exception("AWS DynamoDB bağlanamıyor. Lütfen sensör verisi gönderin!")

    def get_latest_readings(self, sensor_type: str, limit: int = 10) -> List[Dict]:
        """
        Belirtilen sensör türünün en son ölçümlerini al
        
        Args:
            sensor_type: "traffic_light", "air_quality", "trash_bin"
            limit: Kaç adet
            
        Returns:
            list: Sensör ölçümleri (boş ise veri yok!)
        """
        try:
            response = self.readings_table.query(
                IndexName="sensor-type-timestamp-index",
                KeyConditionExpression="sensor_type = :st",
                ExpressionAttributeValues={":st": sensor_type},
                ScanIndexForward=False,  # Descending order (en yeni önce)
                Limit=limit,
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"❌ Sorgu hatası: {e}")
            return []

    def get_readings_by_device(
        self, device_id: str, sensor_type: str, hours: int = 24
    ) -> List[Dict]:
        """
        Belirtilen cihazın son N saatlik ölçümlerini al
        
        Args:
            device_id: Cihaz ID'si
            sensor_type: Sensör türü
            hours: Kaç saat geriye
            
        Returns:
            list: Sensör ölçümleri (boş ise veri yok!)
        """
        pk = f"{sensor_type}#{device_id}"
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat() + "Z"

        try:
            response = self.readings_table.query(
                KeyConditionExpression="pk = :pk AND sk > :cutoff",
                ExpressionAttributeValues={":pk": pk, ":cutoff": cutoff_time},
                ScanIndexForward=False,  # En yeni önce
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"❌ Sorgu hatası: {e}")
            return []

    def get_readings_by_location(
        self, location: str, hours: int = 1
    ) -> List[Dict]:
        """
        Belirtilen lokasyondaki son ölçümleri al
        
        Args:
            location: Lokasyon adı
            hours: Kaç saat geriye
            
        Returns:
            list: Sensör ölçümleri (boş ise veri yok!)
        """
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat() + "Z"

        try:
            response = self.readings_table.query(
                IndexName="location-timestamp-index",
                KeyConditionExpression="location = :loc AND sk > :cutoff",
                ExpressionAttributeValues={":loc": location, ":cutoff": cutoff_time},
                ScanIndexForward=False,
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"❌ Sorgu hatası: {e}")
            return []

    def get_active_alerts(self) -> List[Dict]:
        """
        Çözülmemiş uyarıları al
        
        Returns:
            list: Aktif uyarılar (boş ise veri yok!)
        """
        try:
            response = self.alerts_table.scan(
                FilterExpression="resolved = :false",
                ExpressionAttributeValues={":false": False},
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"❌ Sorgu hatası: {e}")
            return []

    def get_alerts_for_device(self, device_id: str, hours: int = 24) -> List[Dict]:
        """
        Belirtilen cihaz için son N saatlik uyarıları al
        
        Args:
            device_id: Cihaz ID'si
            hours: Kaç saat geriye
            
        Returns:
            list: Uyarılar (boş ise veri yok!)
        """
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat() + "Z"

        try:
            response = self.alerts_table.scan(
                FilterExpression="device_id = :did AND #ts > :cutoff",
                ExpressionAttributeNames={"#ts": "timestamp"},
                ExpressionAttributeValues={":did": device_id, ":cutoff": cutoff_time},
            )
            return response.get("Items", [])
        except Exception as e:
            print(f"❌ Sorgu hatası: {e}")
            return []

    def get_statistics(self, sensor_type: str, device_id: str) -> Dict[str, Any]:
        """
        Sensör için istatistikler hesapla (son 24 saat)
        
        Args:
            sensor_type: Sensör türü
            device_id: Cihaz ID'si
            
        Returns:
            dict: Min, Max, Avg, Count vb.
        """
        readings = self.get_readings_by_device(device_id, sensor_type, hours=24)

        if not readings:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
            }

        values = [item["value"] for item in readings]

        return {
            "count": len(values),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
            "latest": round(values[0], 2) if values else None,
            "timestamp": readings[0].get("timestamp") if readings else None,
        }


# Kullanım örnekleri
if __name__ == "__main__":
    query = SensorDataQuery()

    # 1. Traffic light'ın son 10 ölçümü
    print("🚦 Traffic Light - Son 10 ölçüm:")
    readings = query.get_latest_readings("traffic_light", limit=10)
    for r in readings:
        print(
            f"  {r['timestamp']}: {r['value']}% "
            f"({r['metadata'].get('status', 'unknown')})"
        )

    # 2. Air quality son 24 saati
    print("\n💨 Air Quality - Son 24 saat:")
    readings = query.get_readings_by_device("air-quality-001", "air_quality", hours=24)
    print(f"  Toplam ölçüm: {len(readings)}")

    # 3. Aktif uyarılar
    print("\n⚠️  Aktif Uyarılar:")
    alerts = query.get_active_alerts()
    for alert in alerts:
        print(f"  {alert['severity'].upper()}: {alert['message']}")

    # 4. İstatistikler
    print("\n📊 Traffic Light İstatistikleri (24h):")
    stats = query.get_statistics("traffic_light", "traffic-light-001")
    print(f"  Min: {stats['min']}")
    print(f"  Max: {stats['max']}")
    print(f"  Avg: {stats['avg']:.2f}")
    print(f"  Count: {stats['count']}")

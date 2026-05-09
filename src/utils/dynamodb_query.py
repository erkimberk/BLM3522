"""
DynamoDB Query Helper Functions
DynamoDB'den veri sorgulama yardımcı fonksiyonları

Bu modül frontend ve analiz scripti tarafından kullanılır.
"""

import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Any

dynamodb = boto3.resource("dynamodb")


class SensorDataQuery:
    """DynamoDB'den sensör verilerini sorgula"""

    def __init__(self, region: str = "eu-central-1"):
        """
        Başlat
        
        Args:
            region: AWS bölgesi
        """
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.readings_table = self.dynamodb.Table("smart-city-sensor-readings")
        self.alerts_table = self.dynamodb.Table("smart-city-sensor-alerts")

    def get_latest_readings(self, sensor_type: str, limit: int = 10) -> List[Dict]:
        """
        Belirtilen sensör türünün en son ölçümlerini al
        
        Args:
            sensor_type: "traffic_light", "air_quality", "trash_bin"
            limit: Kaç adet
            
        Returns:
            list: Sensör ölçümleri
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
            list: Sensör ölçümleri
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
            list: Sensör ölçümleri
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
            list: Aktif uyarılar
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
            list: Uyarılar
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
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[0] if values else None,
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

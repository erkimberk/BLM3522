"""
Traffic Light Sensor Simulator
Trafik ışığı sensörü - Trafik yoğunluğu simülasyonu
"""

import random
import time
from datetime import datetime
import json


class TrafficLightSensor:
    """
    Trafik yoğunluğu sensörü simülasyonu
    
    Özellikleri:
    - congestion: 0-100% (trafik yoğunluğu)
    - vehicle_count: Geçen araç sayısı (5 dakikada)
    - average_speed: Ortalama araç hızı (km/h)
    - timestamp: Ölçüm zamanı
    """

    def __init__(self, location_id: str = "Main Street"):
        """
        Sensörü başlat.
        
        Args:
            location_id: Sensörün konumu
        """
        self.location_id = location_id
        self.base_congestion = random.randint(20, 50)  # Temel yoğunluk
        self.is_peak_hour = False

    def set_peak_hour(self, is_peak: bool):
        """
        Rush hour (yoğun saat) ayarı.
        Yoğun saatlerde trafik yoğunluğu artar.
        """
        self.is_peak_hour = is_peak

    def generate_data(self) -> dict:
        """
        Gerçekçi trafik verisi üret.
        
        Returns:
            dict: Trafik verileri
        """
        # Peak hour'da yoğunluk artar (temel + 30-50%)
        if self.is_peak_hour:
            congestion = self.base_congestion + random.randint(30, 50)
        else:
            # Off-peak saatlerde ±20% varyasyon
            congestion = max(10, self.base_congestion + random.randint(-20, 20))

        # Yoğunluğa bağlı olarak hız belirlenir
        # Yoğun → düşük hız, az yoğun → yüksek hız
        base_speed = 80 - (congestion * 0.5)  # Yoğunluk arttıkça hız düşer
        average_speed = max(5, base_speed + random.uniform(-10, 10))

        # Geçen araç sayısı (5 dakikada)
        vehicle_count = int((100 - congestion) * 15 + random.randint(-50, 50))
        vehicle_count = max(0, vehicle_count)

        return {
            "timestamp": datetime.now().isoformat(),
            "device": "traffic-light-001",
            "location": self.location_id,
            "metric": "congestion",
            "congestion_percent": round(congestion, 2),
            "vehicle_count_5min": vehicle_count,
            "average_speed_kmh": round(average_speed, 2),
            "status": self._get_status(congestion),
        }

    def _get_status(self, congestion: float) -> str:
        """
        Yoğunluk seviyesine göre durum belirle.
        
        Args:
            congestion: Yoğunluk yüzdesi (0-100)
            
        Returns:
            str: "green", "yellow", "red"
        """
        if congestion < 33:
            return "green"  # Az yoğun
        elif congestion < 66:
            return "yellow"  # Orta yoğun
        else:
            return "red"  # Çok yoğun

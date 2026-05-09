"""
Air Quality Sensor Simulator
Hava kalitesi sensörü - Hava kirliliği ve özellikleri simülasyonu
"""

import random
from datetime import datetime


class AirQualitySensor:
    """
    Hava kalitesi sensörü simülasyonu
    
    Ölçüm parametreleri:
    - PM2.5: İnce partikül madde (µg/m³)
    - PM10: Orta partikül madde (µg/m³)
    - CO2: Karbon dioksit (ppm)
    - Temperature: Sıcaklık (°C)
    - Humidity: Nemlilik (%)
    """

    def __init__(self, location_id: str = "City Center"):
        """
        Sensörü başlat.
        
        Args:
            location_id: Sensörün konumu
        """
        self.location_id = location_id
        self.base_pm25 = random.randint(20, 40)
        self.base_pm10 = random.randint(40, 60)
        self.is_pollution_high = False

    def set_pollution_level(self, high: bool):
        """
        Kirlilik seviyesini ayarla.
        
        Args:
            high: True → yüksek kirlilik, False → normal
        """
        self.is_pollution_high = high

    def generate_data(self) -> dict:
        """
        Gerçekçi hava kalitesi verisi üret.
        
        Returns:
            dict: Hava kalitesi verileri
        """
        # Yüksek kirlilik durumunda değerler artar
        if self.is_pollution_high:
            pm25 = self.base_pm25 + random.randint(40, 80)
            pm10 = self.base_pm10 + random.randint(40, 80)
        else:
            # Normal durumda ±15% varyasyon
            pm25 = max(5, self.base_pm25 + random.randint(-15, 20))
            pm10 = max(10, self.base_pm10 + random.randint(-15, 20))

        # CO2 (sabit + varyasyon)
        co2 = 400 + random.randint(-20, 50)

        # Sıcaklık (mevsime bağlı: şimdilik 15-28°C)
        temperature = round(random.uniform(15, 28), 1)

        # Nemlilik (%)
        humidity = random.randint(40, 80)

        # AQI (Air Quality Index) hesapla
        aqi = self._calculate_aqi(pm25)

        return {
            "timestamp": datetime.now().isoformat(),
            "device": "air-quality-001",
            "location": self.location_id,
            "metric": "air_quality",
            "pm25_ug_m3": round(pm25, 2),
            "pm10_ug_m3": round(pm10, 2),
            "co2_ppm": co2,
            "temperature_celsius": temperature,
            "humidity_percent": humidity,
            "aqi": aqi,
            "aqi_category": self._get_aqi_category(aqi),
        }

    def _calculate_aqi(self, pm25: float) -> int:
        """
        PM2.5'ten AQI hesapla (0-500 scale).
        
        Args:
            pm25: PM2.5 değeri
            
        Returns:
            int: AQI değeri
        """
        # Basitleştirilmiş AQI hesaplaması
        # WHO standartları: 0-12 Good, 12-35 Fair, 35-55 Moderate, vb.
        if pm25 <= 12:
            return int(pm25 * 50 / 12)
        elif pm25 <= 35.4:
            return int(50 + (pm25 - 12) * 50 / 23.4)
        elif pm25 <= 55.4:
            return int(100 + (pm25 - 35.4) * 50 / 20)
        elif pm25 <= 150.4:
            return int(150 + (pm25 - 55.4) * 50 / 95)
        else:
            return int(200 + (pm25 - 150.4) * 300 / 349.6)

    def _get_aqi_category(self, aqi: int) -> str:
        """
        AQI değerine göre kategori belirle.
        
        Args:
            aqi: AQI değeri
            
        Returns:
            str: Kategori adı
        """
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Fair"
        elif aqi <= 150:
            return "Moderate"
        elif aqi <= 200:
            return "Poor"
        elif aqi <= 300:
            return "Very Poor"
        else:
            return "Hazardous"

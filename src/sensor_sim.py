"""
IoT Sensör Simülatörü
Sıcaklık ve nem verilerini gerçekçi bir şekilde simüle eder
"""

import json
import time
import random
from datetime import datetime

class IoTSensorSimulator:
    """
    IoT sensörü simüle eden sınıf
    Sıcaklık (20-30°C arasında) ve nem (%40-80 arasında) verisi üretir
    """
    
    def __init__(self, sensor_id="sensor-001", location="Lab-Room1"):
        """
        Sensörü başlatır
        
        Args:
            sensor_id: Sensörün benzersiz kimliği
            location: Sensörün konumu (bina, oda vb.)
        """
        self.sensor_id = sensor_id
        self.location = location
        
        # Başlangıç değerleri
        self.base_temperature = 23.0  # Temel sıcaklık (°C)
        self.base_humidity = 60.0     # Temel nem (%)
        
        # Değişim hızı (sıcaklık ve nem nasıl değişecek)
        self.temp_variation = 0.5
        self.humidity_variation = 2.0
    
    def generate_sensor_data(self):
        """
        Gerçekçi bir şekilde sıcaklık ve nem verisi oluşturur
        
        Returns:
            dict: Sensör verisini içeren sözlük
        """
        
        # Sıcaklık: Temel değer + rastgele dalgalanma (±5°C aralığında)
        temperature = self.base_temperature + random.uniform(
            -self.temp_variation, 
            self.temp_variation
        )
        
        # Nem: Temel değer + rastgele dalgalanma
        humidity = self.base_humidity + random.uniform(
            -self.humidity_variation, 
            self.humidity_variation
        )
        
        # Sıcaklık ve nem mantıklı sınırlar içinde olsun
        temperature = round(max(15.0, min(35.0, temperature)), 2)
        humidity = round(max(30.0, min(90.0, humidity)), 2)
        
        # Sensör verisini JSON formatında oluştur
        sensor_data = {
            "sensor_id": self.sensor_id,
            "location": self.location,
            "temperature": temperature,          # Sıcaklık (°C cinsinden)
            "humidity": humidity,                # Nem (% olarak)
            "timestamp": datetime.utcnow().isoformat() + "Z",  # ISO 8601 formatında zaman
        }
        
        return sensor_data
    
    def simulate_continuous_reading(self, interval=5, iterations=10):
        """
        Sensörden belirli aralıklarla veri okur (simülasyon)
        
        Args:
            interval: Veri okuma aralığı (saniye)
            iterations: Kaç kez veri okuması yapılacak
        """
        
        print(f"\n{'='*60}")
        print(f"IoT Sensör Simülatörü Başlatılıyor...")
        print(f"Sensör ID: {self.sensor_id}")
        print(f"Konum: {self.location}")
        print(f"Okuma Aralığı: {interval} saniye")
        print(f"Toplam Okuma Sayısı: {iterations}")
        print(f"{'='*60}\n")
        
        for i in range(iterations):
            # Sensörden veri al
            data = self.generate_sensor_data()
            
            # Veriyi güzel bir şekilde ekrana yazdır
            print(f"[Okuma #{i+1}] Saat: {data['timestamp']}")
            print(f"  └─ Sıcaklık: {data['temperature']}°C")
            print(f"  └─ Nem: {data['humidity']}%")
            print(f"  └─ JSON: {json.dumps(data)}\n")
            
            # Son okuma hariç, belirtilen saniye kadar bekle
            if i < iterations - 1:
                time.sleep(interval)
        
        print(f"{'='*60}")
        print("Simülasyon Tamamlandı!")
        print(f"{'='*60}\n")


def main():
    """
    Ana program: Sensör simülatörünü çalıştır
    """
    
    # Sensörü oluştur
    sensor = IoTSensorSimulator(
        sensor_id="iot-sensor-001",
        location="Lab-Odası-1"
    )
    
    # Simülasyonu başlat (her 2 saniyede 1 veri, toplam 10 okuma)
    sensor.simulate_continuous_reading(interval=2, iterations=10)


if __name__ == "__main__":
    main()

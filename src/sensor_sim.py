"""
IoT Sensör Simülatörü - AWS IoT Core MQTT Bağlantılı
Sıcaklık ve nem verilerini simüle ederek AWS IoT Core'a MQTT ile gönderir
"""

import json
import time
import random
import os
import ssl
import sys
from datetime import datetime
import paho.mqtt.client as mqtt

class IoTSensorSimulator:
    """
    AWS IoT Core'a bağlanan IoT sensörü simüle eden sınıf
    Sıcaklık ve nem verilerini MQTT protokolü ile gönderir
    """
    
    def __init__(self, sensor_id="iot-sensor-001", location="Lab-Odası-1", 
                 aws_endpoint="", cert_path="", key_path="", ca_path=""):
        """
        Sensörü başlatır ve AWS IoT Core bağlantısını hazırlar
        
        Args:
            sensor_id: Sensörün benzersiz kimliği
            location: Sensörün konumu 
            aws_endpoint: AWS IoT Core endpoint'i (ör: xxx.iot.us-east-1.amazonaws.com)
            cert_path: Sertifika dosyasının yolu (.pem)
            key_path: Özel anahtar dosyasının yolu (.key)
            ca_path: Amazon Root CA dosyasının yolu
        """
        self.sensor_id = sensor_id
        self.location = location
        
        # AWS bağlantı bilgileri
        self.aws_endpoint = aws_endpoint
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        self.mqtt_port = 8883  # AWS IoT Core için standart port
        
        # MQTT istemcisi oluştur
        self.mqtt_client = mqtt.Client(client_id=sensor_id, protocol=mqtt.MQTTv311)
        
        # MQTT bağlantı callback'lerini ayarla
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_publish = self._on_publish
        self.mqtt_client.on_disconnect = self._on_disconnect
        
        # Başlangıç değerleri
        self.base_temperature = 23.0  # Temel sıcaklık (°C)
        self.base_humidity = 60.0     # Temel nem (%)
        
        # Değişim hızı
        self.temp_variation = 0.5
        self.humidity_variation = 2.0
        
        # Bağlantı durumu
        self.is_connected = False
        self.message_count = 0
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        MQTT bağlantı callback'i
        Bağlantı başarılı olduğunda çağrılır
        """
        if rc == 0:
            self.is_connected = True
            print(f"✓ AWS IoT Core'a başarılı şekilde bağlandı! (Sensor: {self.sensor_id})")
        else:
            print(f"✗ Bağlantı hatası! Hata kodu: {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """
        MQTT yayın callback'i
        Veri başarılı şekilde yayınlandığında çağrılır
        """
        self.message_count += 1
        print(f"  → Veri AWS'ye gönderildi (Toplam: {self.message_count} mesaj)")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        MQTT kesilme callback'i
        Bağlantı kesildiğinde çağrılır
        """
        if rc != 0:
            print(f"! Beklenmeyen MQTT kesilmesi, Hata kodu: {rc}")
        self.is_connected = False
    
    def connect_to_aws(self):
        """
        AWS IoT Core'a MQTT ile bağlanır
        
        Returns:
            bool: Bağlantı başarılı ise True, değilse False
        """
        
        if not all([self.aws_endpoint, self.cert_path, self.key_path, self.ca_path]):
            print("✗ Hata: AWS IoT sertifikalarının yolları belirtilmedi!")
            print("  Lütfen sensor_sim.py'yi çalıştırmadan önce sertifikalar klasöründe dosyaların olup olmadığını kontrol et.")
            return False
        
        # Dosyaların var olup olmadığını kontrol et
        if not os.path.exists(self.cert_path):
            print(f"✗ Hata: Sertifika dosyası bulunamadı: {self.cert_path}")
            return False
        if not os.path.exists(self.key_path):
            print(f"✗ Hata: Anahtar dosyası bulunamadı: {self.key_path}")
            return False
        if not os.path.exists(self.ca_path):
            print(f"✗ Hata: CA dosyası bulunamadı: {self.ca_path}")
            return False
        
        try:
            # TLS/SSL sertifikaları ayarla
            # AWS IoT Core, TLS 1.2 üzerinden MQTT kullanya
            self.mqtt_client.tls_set(
                ca_certs=self.ca_path,
                certfile=self.cert_path,
                keyfile=self.key_path,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                ciphers=None
            )
            
            # TLS sertifika doğrulamasını devre dışı bırak (sadece test için)
            self.mqtt_client.tls_insecure_set(False)
            
            # AWS IoT Core'a bağlan
            print(f"\n{'='*60}")
            print(f"AWS IoT Core'a bağlanılıyor...")
            print(f"Endpoint: {self.aws_endpoint}:{self.mqtt_port}")
            print(f"{'='*60}\n")
            
            self.mqtt_client.connect(self.aws_endpoint, self.mqtt_port, keepalive=60)
            
            # MQTT ağını başlat (background'de mesaj işleme)
            self.mqtt_client.loop_start()
            
            # Bağlantının kurulması için kısa bir bekleme
            time.sleep(2)
            
            return self.is_connected
            
        except Exception as e:
            print(f"✗ AWS IoT Core'a bağlanma hatası: {str(e)}")
            return False
    
    def generate_sensor_data(self):
        """
        Gerçekçi bir şekilde sıcaklık ve nem verisi oluşturur
        
        Returns:
            dict: Sensör verisini içeren sözlük
        """
        
        # Sıcaklık: Temel değer + rastgele dalgalanma
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
    
    def publish_data_to_aws(self, data):
        """
        Sensör verisini AWS IoT Core'a MQTT ile yayınlar
        
        Args:
            data: Yayınlanacak sensör verisi (dict)
        """
        
        if not self.is_connected:
            print("✗ AWS IoT Core'a bağlı değilsiniz! Veri gönderilemedi.")
            return False
        
        # MQTT topic'ini oluştur (AWS ileti yönlendirilmesi için)
        # Format: sensors/{sensor_id}/data
        topic = f"sensors/{self.sensor_id}/data"
        
        # Veriyi JSON'a dönüştür
        payload = json.dumps(data)
        
        try:
            # MQTT aracılığıyla veriyi yayınla
            self.mqtt_client.publish(topic, payload, qos=1)
            print(f"[Yayın] Topic: {topic}")
            print(f"  └─ Sıcaklık: {data['temperature']}°C")
            print(f"  └─ Nem: {data['humidity']}%")
            print(f"  └─ Zaman: {data['timestamp']}\n")
            return True
        except Exception as e:
            print(f"✗ MQTT yayın hatası: {str(e)}")
            return False
    
    def run_continuous_publishing(self, interval=5, iterations=10):
        """
        Sensörden belirli aralıklarla veri oluşturup AWS'ye gönderir
        
        Args:
            interval: Veri yayın aralığı (saniye)
            iterations: Kaç kez veri gönderilecek
        """
        
        print(f"\n{'='*60}")
        print(f"IoT Sensör Simülatörü Başlatılıyor...")
        print(f"Sensör ID: {self.sensor_id}")
        print(f"Konum: {self.location}")
        print(f"Yayın Aralığı: {interval} saniye")
        print(f"Toplam Yayın Sayısı: {iterations}")
        print(f"{'='*60}\n")
        
        for i in range(iterations):
            # Sensörden veri al
            data = self.generate_sensor_data()
            
            # Veriyi AWS'ye gönder
            self.publish_data_to_aws(data)
            
            # Son yayın hariç, belirtilen saniye kadar bekle
            if i < iterations - 1:
                time.sleep(interval)
        
        print(f"{'='*60}")
        print("Yayınlama Tamamlandı!")
        print(f"Toplam Yayın Edilen Mesaj: {self.message_count}")
        print(f"{'='*60}\n")
    
    def disconnect(self):
        """
        AWS IoT Core bağlantısını kapatır
        """
        if self.is_connected:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            print("\n✓ AWS IoT Core'dan bağlantı kesildi.")


def main():
    """
    Ana program: Sensör simülatörünü AWS IoT Core'a bağlayıp çalıştır
    """
    
    # AWS sertifikaları için dosya yollarını belirt
    # Adım 4'te certificates/ klasörüne indirilen dosyalar
    base_path = "../certificates"
    
    aws_config = {
        "sensor_id": "iot-sensor-001",
        "location": "Lab-Odası-1",
        "aws_endpoint": "avd01ikm8qx2k-ats.iot.eu-north-1.amazonaws.com",
        "cert_path": os.path.join(base_path, "bb286b6b4cc0dec45e44d6e339b784d1594333e26ecc234e2256ea8896d780ae-certificate.pem.crt"),
        "key_path": os.path.join(base_path, "bb286b6b4cc0dec45e44d6e339b784d1594333e26ecc234e2256ea8896d780ae-private.pem.key"),
        "ca_path": os.path.join(base_path, "AmazonRootCA1.pem"),
    }
    
    # Sensörü oluştur
    sensor = IoTSensorSimulator(**aws_config)
    
    # AWS IoT Core'a bağlanmayı dene
    if sensor.connect_to_aws():
        print("✓ Bağlantı başarılı! Veri yayınlanmaya başlanıyor...\n")
        
        # Simülasyonu başlat (her 2 saniyede 1 veri, toplam 10 yayın)
        sensor.run_continuous_publishing(interval=2, iterations=10)
    else:
        print("✗ AWS IoT Core'a bağlanılamadı. Lütfen sertifikaları ve endpoint'i kontrol et.")
        sys.exit(1)
    
    # Bağlantıyı kapat
    sensor.disconnect()


if __name__ == "__main__":
    main()

"""
AWS IoT Configuration Utility
Bu modül AWS IoT Core bağlantısı için gerekli konfigürasyonları yönetir.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class AWSIoTConfig:
    """AWS IoT Core için merkezi konfigürasyon sınıfı"""

    def __init__(self):
        """Konfigürasyonu environment variables'den oku"""
        self.region = os.getenv("AWS_REGION", "eu-central-1")
        self.iot_endpoint = os.getenv("AWS_IOT_ENDPOINT")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 8883))
        self.topic_prefix = os.getenv("MQTT_TOPIC_PREFIX", "smart-city")

        # Sertifika yolları
        self.cert_path = Path(os.getenv("IOT_CERT_PATH", "config/certificates/"))
        self.ca_cert = Path(os.getenv("IOT_CA_FILE", "config/certificates/AmazonRootCA1.pem"))
        self.device_cert = Path(os.getenv("IOT_CERT_FILE", "config/certificates/device.crt"))
        self.device_key = Path(os.getenv("IOT_KEY_FILE", "config/certificates/private.key"))

        # Thing IDs
        self.things = {
            "traffic_light": os.getenv("TRAFFIC_LIGHT_ID", "traffic-light-001"),
            "air_quality": os.getenv("AIR_QUALITY_ID", "air-quality-001"),
            "trash_bin": os.getenv("TRASH_BIN_ID", "trash-bin-001"),
        }

    def validate(self):
        """
        Konfigürasyonun geçerliliğini kontrol et.
        Eksik bilgiler için uyarı ver.
        """
        issues = []

        if not self.iot_endpoint:
            issues.append(
                "⚠️  AWS_IOT_ENDPOINT tanımlanmamış. .env dosyasını kontrol et."
            )

        if not self.ca_cert.exists():
            issues.append(f"⚠️  Root CA certificate bulunamadı: {self.ca_cert}")

        return issues

    def get_device_config(self, device_type: str):
        """
        Belirli bir cihaz türü için konfigürasyonu döndür.

        Args:
            device_type: "traffic_light", "air_quality", "trash_bin"

        Returns:
            dict: Cihaz konfigürasyonu
        """
        thing_name = self.things.get(device_type)
        if not thing_name:
            raise ValueError(f"Bilinmeyen cihaz türü: {device_type}")

        return {
            "thing_name": thing_name,
            "endpoint": self.iot_endpoint,
            "port": self.mqtt_port,
            "ca_cert": str(self.ca_cert),
            "region": self.region,
        }

    def get_mqtt_topic(self, device_type: str, metric: str) -> str:
        """
        MQTT topic string'ini oluştur.

        Args:
            device_type: "traffic_light", "air_quality", "trash_bin"
            metric: Metric adı (e.g., "congestion", "pm25")

        Returns:
            str: MQTT topic path
        """
        thing_name = self.things.get(device_type)
        if not thing_name:
            raise ValueError(f"Bilinmeyen cihaz türü: {device_type}")

        return f"{self.topic_prefix}/{device_type}/{thing_name}/{metric}"


# Global config instance
config = AWSIoTConfig()

"""
MQTT Client Wrapper
paho-mqtt client'ını sarmalayan ve AWS IoT Core ile bağlantıyı yöneten modül.
"""

import logging
import json
from typing import Callable, Optional
import paho.mqtt.client as mqtt
from aws_config import config

# Logging ayarla
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartCityMQTTClient:
    """AWS IoT Core'a MQTT üzerinden bağlanan client"""

    def __init__(self, device_type: str):
        """
        Client'ı başlat.

        Args:
            device_type: "traffic_light", "air_quality", "trash_bin"
        """
        self.device_type = device_type
        self.device_config = config.get_device_config(device_type)
        self.thing_name = self.device_config["thing_name"]

        # MQTT Client oluştur
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_message = self._on_message

        self.is_connected = False
        self.on_message_callback: Optional[Callable] = None

    def _on_connect(self, client, userdata, connect_flags, rc, properties=None):
        """MQTT bağlantı callback'i"""
        if rc == 0:
            logger.info(f"✅ {self.thing_name} bağlandı (MQTT)")
            self.is_connected = True
        else:
            logger.error(f"❌ {self.thing_name} bağlantı hatası: rc={rc}")
            self.is_connected = False

    def _on_disconnect(self, client, userdata, disconnect_flags, rc, properties=None):
        """MQTT bağlantı kopması callback'i"""
        # rc ReasonCode nesnesi olabilir, convert et
        try:
            rc_value = int(rc) if rc else 0
        except:
            rc_value = 0
            
        error_codes = {
            0: "Normal disconnect",
            1: "Unexpected disconnect",
            2: "MQTT Protocol error",
            3: "Broker unavailable",
            4: "Broker is closing",
            5: "Keep alive timeout",
            6: "Session taken over",
            7: "Invalid server response",
            8: "TLS handshake error",
            9: "Authentication error",
            10: "Not authorized",
            11: "Server not available",
            12: "Server moved",
            13: "Connection rate exceeded",
            14: "Maximum connect time exceeded",
            15: "Unspecified error",
        }
        
        error_msg = error_codes.get(rc_value, "Unknown error")
        if rc_value in [8, 9]:
            logger.error(f"❌ {self.thing_name} TLS/Auth hatası ({error_msg}): rc={rc_value} - Sertifikaları kontrol et!")
        elif rc_value != 0:
            logger.warning(f"⚠️  {self.thing_name} bağlantısı kesildi ({error_msg}): rc={rc_value}")
        self.is_connected = False

    def _on_publish(self, client, userdata, mid, rc, properties=None):
        """MQTT yayın callback'i"""
        if rc == 0:
            logger.debug(f"📤 {self.thing_name}: Mesaj yayınlandı")
        else:
            logger.error(f"❌ {self.thing_name}: Yayın hatası: rc={rc}")

    def _on_message(self, client, userdata, msg):
        """MQTT mesaj alım callback'i"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📥 {self.thing_name} mesaj aldı: {msg.topic}")

            if self.on_message_callback:
                self.on_message_callback(msg.topic, payload)
        except json.JSONDecodeError:
            logger.error(f"❌ JSON parse hatası: {msg.payload}")

    def connect(self):
        """AWS IoT Core'a bağlan"""
        try:
            # AWS IoT Core'a bağlan (TLS zaten set_device_certificates() ile yapıldı)
            logger.info(
                f"🔄 {self.thing_name} bağlanıyor: {self.device_config['endpoint']}:{self.device_config['port']}"
            )
            self.client.connect(
                self.device_config["endpoint"], self.device_config["port"], keepalive=60
            )

            # Background loop başlat
            self.client.loop_start()

        except Exception as e:
            logger.error(f"❌ Bağlantı hatası: {e}")
            raise

    def set_device_certificates(self, cert_file: str, key_file: str):
        """
        Client sertifikası ve private key ayarla.

        Args:
            cert_file: Sertifika dosyasının yolu
            key_file: Private key dosyasının yolu
        """
        from pathlib import Path
        
        try:
            # Dosyaların varlığını kontrol et
            cert_path = Path(cert_file)
            key_path = Path(key_file)
            ca_path = Path(self.device_config["ca_cert"])
            
            if not cert_path.exists():
                raise FileNotFoundError(f"Certificate bulunamadı: {cert_path.absolute()}")
            if not key_path.exists():
                raise FileNotFoundError(f"Private key bulunamadı: {key_path.absolute()}")
            if not ca_path.exists():
                raise FileNotFoundError(f"CA certificate bulunamadı: {ca_path.absolute()}")
            
            self.client.tls_set(
                ca_certs=str(ca_path),
                certfile=str(cert_path),
                keyfile=str(key_path),
                cert_reqs=True,
                tls_version=None,
                ciphers=None,
            )
            
            # Hostname doğrulamasını disable et (AWS IoT için)
            self.client.tls_insecure = False
            
            logger.info(f"✅ {self.thing_name} sertifikalar ayarlandı")
        except FileNotFoundError as e:
            logger.error(f"❌ Sertifika dosyası hatası: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Sertifika ayarlama hatası: {e}")
            raise

    def publish_data(self, metric: str, value: float, metadata: Optional[dict] = None):
        """
        Sensör verisini AWS IoT'ye yayınla.

        Args:
            metric: Metrik adı (e.g., "congestion", "pm25")
            value: Ölçüm değeri
            metadata: İlave metadata dict
        """
        if not self.is_connected:
            logger.warning(f"⚠️  {self.thing_name} henüz bağlı değil")
            return

        topic = config.get_mqtt_topic(self.device_type, metric)

        payload = {
            "timestamp": None,  # Lambda tarafında işlenecek
            "device": self.thing_name,
            "metric": metric,
            "value": value,
        }

        if metadata:
            payload["metadata"] = metadata

        try:
            result = self.client.publish(
                topic, json.dumps(payload), qos=1  # QoS 1: At least once
            )
            if result.rc == 0:
                logger.debug(f"📤 {metric}={value} yayınlandı → {topic}")
            else:
                logger.error(f"❌ Yayın hatası: rc={result.rc}")
        except Exception as e:
            logger.error(f"❌ Yayın sırasında hata: {e}")

    def subscribe_to_topic(self, topic: str, callback: Callable):
        """
        Belirtilen topic'e abone ol.

        Args:
            topic: Abone olunacak topic
            callback: Mesaj geldiğinde çağrılacak fonksiyon
        """
        self.on_message_callback = callback
        self.client.subscribe(topic, qos=1)
        logger.info(f"📨 Abone olundu: {topic}")

    def disconnect(self):
        """MQTT bağlantısını kapat"""
        logger.info(f"🔌 {self.thing_name} bağlantı kapatılıyor")
        self.client.loop_stop()
        self.client.disconnect()
        self.is_connected = False

    def __del__(self):
        """Object silindiğinde otomatik disconnect"""
        if self.is_connected:
            self.disconnect()

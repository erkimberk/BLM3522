"""
Main IoT Sensor Simulator
3 sensörü başlatıp AWS IoT'ye veri yayınlayan ana script.

Kullanım:
    python sensor_simulator.py [--duration SECONDS] [--interval SECONDS]

Örnek:
    python sensor_simulator.py --duration 300 --interval 5
    # 300 saniye boyunca her 5 saniyede bir veri yayınla
"""

import sys
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

# src/devices ve src/utils'ı path'e ekle
sys.path.insert(0, str(Path(__file__).parent / "src" / "devices"))
sys.path.insert(0, str(Path(__file__).parent / "src" / "utils"))

from traffic_light_sensor import TrafficLightSensor
from air_quality_sensor import AirQualitySensor
from trash_bin_sensor import TrashBinSensor
from mqtt_client import SmartCityMQTTClient
from aws_config import config

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SensorSimulator:
    """
    3 sensörü simüle ediyor ve AWS IoT'ye veri yayınlıyor.
    """

    def __init__(self):
        """Simülatörü başlat"""
        logger.info("🚀 Sensor Simulator başlıyor...")

        # Sensör nesneleri oluştur
        self.traffic_light = TrafficLightSensor("Main Street")
        self.air_quality = AirQualitySensor("City Center")
        self.trash_bin = TrashBinSensor("Street Corner")

        # MQTT clients oluştur
        try:
            self.mqtt_traffic = SmartCityMQTTClient("traffic_light")
            self.mqtt_air = SmartCityMQTTClient("air_quality")
            self.mqtt_trash = SmartCityMQTTClient("trash_bin")

            logger.info("✅ MQTT clients oluşturuldu")
        except Exception as e:
            logger.error(f"❌ MQTT client oluşturma hatası: {e}")
            raise

        self.published_count = 0
        self.start_time = None

    def setup_devices(self, cert_dir: str = "config/certificates"):
        """
        Cihazlar için sertifikaları ayarla.

        Args:
            cert_dir: Sertifika dosyalarının bulunduğu dizin
        """
        cert_path = Path(cert_dir)

        try:
            # Tüm cihazlar aynı sertifikaları kullanıyor (AWS IoT tarafında policy ile kontrol)
            cert_file = str(cert_path / "device.crt")
            key_file = str(cert_path / "private.key")

            # Traffic Light
            self.mqtt_traffic.set_device_certificates(cert_file, key_file)

            # Air Quality
            self.mqtt_air.set_device_certificates(cert_file, key_file)

            # Trash Bin
            self.mqtt_trash.set_device_certificates(cert_file, key_file)

            logger.info("✅ Sertifikalar ayarlandı")
        except FileNotFoundError as e:
            logger.warning(
                f"⚠️  Sertifika bulunamadı: {e}\n"
                f"Lütfen config/aws/setup_instructions.md'yi takip et"
            )

    def connect_all(self):
        """Tüm sensörleri AWS IoT'ye bağla"""
        try:
            logger.info("🔌 Bağlantılar kuruluyor...")
            self.mqtt_traffic.connect()
            self.mqtt_air.connect()
            self.mqtt_trash.connect()
            time.sleep(2)  # Bağlantı kurulması için bekleme
            logger.info("✅ Tüm cihazlar bağlandı")
        except Exception as e:
            logger.error(f"❌ Bağlantı hatası: {e}")
            raise

    def publish_sensor_data(self):
        """Sensör verilerini AWS IoT'ye yayınla"""
        try:
            # 1. Traffic Light
            if self.mqtt_traffic.is_connected:
                traffic_data = self.traffic_light.generate_data()
                self.mqtt_traffic.publish_data(
                    "congestion",
                    traffic_data["congestion_percent"],
                    metadata={
                        "location": traffic_data["location"],
                        "status": traffic_data["status"],
                        "vehicles": traffic_data["vehicle_count_5min"],
                        "speed": traffic_data["average_speed_kmh"],
                    },
                )
                logger.info(
                    f"📤 Traffic: {traffic_data['congestion_percent']}% "
                    f"(Status: {traffic_data['status']})"
                )

            # 2. Air Quality
            if self.mqtt_air.is_connected:
                air_data = self.air_quality.generate_data()
                self.mqtt_air.publish_data(
                    "pm25",
                    air_data["pm25_ug_m3"],
                    metadata={
                        "location": air_data["location"],
                        "pm10": air_data["pm10_ug_m3"],
                        "co2": air_data["co2_ppm"],
                        "aqi": air_data["aqi"],
                        "category": air_data["aqi_category"],
                        "temp": air_data["temperature_celsius"],
                        "humidity": air_data["humidity_percent"],
                    },
                )
                logger.info(
                    f"📤 Air Quality: PM2.5={air_data['pm25_ug_m3']} "
                    f"AQI={air_data['aqi']} ({air_data['aqi_category']})"
                )

            # 3. Trash Bin
            if self.mqtt_trash.is_connected:
                trash_data = self.trash_bin.generate_data()
                self.mqtt_trash.publish_data(
                    "fill_level",
                    trash_data["fill_percentage"],
                    metadata={
                        "location": trash_data["location"],
                        "weight_kg": trash_data["weight_kg"],
                        "collection_needed": trash_data["collection_needed"],
                        "urgency": trash_data["collection_urgency"],
                    },
                )
                logger.info(
                    f"📤 Trash Bin: {trash_data['fill_percentage']}% "
                    f"({trash_data['collection_urgency']})"
                )

            self.published_count += 3

        except Exception as e:
            logger.error(f"❌ Yayın hatası: {e}")

    def disconnect_all(self):
        """Tüm bağlantıları kapat"""
        logger.info("🔌 Bağlantılar kapatılıyor...")
        self.mqtt_traffic.disconnect()
        self.mqtt_air.disconnect()
        self.mqtt_trash.disconnect()
        logger.info("✅ Tüm bağlantılar kapatıldı")

    def run(self, duration: int = 60, interval: int = 5):
        """
        Simülatörü çalıştır.

        Args:
            duration: Çalışma süresi (saniye)
            interval: Veri yayın aralığı (saniye)
        """
        self.start_time = time.time()
        end_time = self.start_time + duration

        logger.info(f"📊 Simulasyon başlıyor (Duration: {duration}s, Interval: {interval}s)")

        try:
            while time.time() < end_time:
                elapsed = int(time.time() - self.start_time)
                logger.info(f"\n⏱️  [{elapsed}s] Veri yayınlanıyor...")

                self.publish_sensor_data()

                # Sonraki yayınına kadar bekle
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.warning("⚠️  Kullanıcı tarafından durduruldu (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Simülasyon hatası: {e}")
        finally:
            self._print_summary()
            self.disconnect_all()

    def _print_summary(self):
        """Simülasyon özeti yazdır"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            logger.info("\n" + "=" * 60)
            logger.info("📊 SIMÜLASYON ÖZET")
            logger.info("=" * 60)
            logger.info(f"Çalışma Süresi: {elapsed:.1f} saniye")
            logger.info(f"Yayınlanan Toplam Mesaj: {self.published_count}")
            logger.info(f"Ortalama: {self.published_count / elapsed:.2f} msg/sec")
            logger.info("=" * 60)


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="IoT Akıllı Şehir Sensör Simülatörü",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python sensor_simulator.py                      # Default: 60s, 5s interval
  python sensor_simulator.py --duration 300       # 5 dakika
  python sensor_simulator.py --duration 120 --interval 2  # 2 dakika, her 2 saniye
        """,
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Simülasyon süresi (saniye, default: 60)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Veri yayın aralığı (saniye, default: 5)",
    )
    parser.add_argument(
        "--cert-dir",
        type=str,
        default="config/certificates",
        help="Sertifika dizini (default: config/certificates)",
    )

    args = parser.parse_args()

    # Simülatör oluştur ve çalıştır
    simulator = SensorSimulator()

    try:
        # Not: Sertifikalar olmadan da AWS IoT'ye bağlanmayacak ama
        # simülatör hatası vermeyecek
        simulator.setup_devices(args.cert_dir)
        simulator.connect_all()
        simulator.run(duration=args.duration, interval=args.interval)
    except Exception as e:
        logger.error(f"❌ Hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

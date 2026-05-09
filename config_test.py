"""
AWS IoT Configuration Test Script
Konfigürasyonun geçerliliğini ve AWS IoT Core'a bağlantıyı test et.

Kullanım:
    python config_test.py
"""

import sys
from pathlib import Path

# src/utils'ı path'e ekle
sys.path.insert(0, str(Path(__file__).parent / "src" / "utils"))

from aws_config import config
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_configuration():
    """Konfigürasyonun tamamlığını test et"""
    logger.info("=" * 60)
    logger.info("🔍 AWS IoT Configuration Test Başlıyor...")
    logger.info("=" * 60)

    # 1. Temel bilgileri yazdır
    logger.info("\n📋 Temel Bilgiler:")
    logger.info(f"  Region: {config.region}")
    logger.info(f"  IoT Endpoint: {config.iot_endpoint or '❌ AYARLANMAMIŞ'}")
    logger.info(f"  MQTT Port: {config.mqtt_port}")
    logger.info(f"  Topic Prefix: {config.topic_prefix}")

    # 2. Thing names'i yazdır
    logger.info("\n🏷️  Thing Names:")
    for device_type, thing_name in config.things.items():
        logger.info(f"  {device_type}: {thing_name}")

    # 3. Sertifikası yollarını yazdır
    logger.info("\n📁 Sertifika Yolları:")
    logger.info(f"  CA Certificate: {config.ca_cert}")
    logger.info(f"    ✅ Var" if config.ca_cert.exists() else f"    ❌ Bulunamadı")

    # 4. Device config'leri test et
    logger.info("\n⚙️  Device Configurations:")
    for device_type in ["traffic_light", "air_quality", "trash_bin"]:
        try:
            dev_config = config.get_device_config(device_type)
            logger.info(f"\n  {device_type}:")
            logger.info(f"    Thing Name: {dev_config['thing_name']}")
            logger.info(f"    Endpoint: {dev_config['endpoint']}")
            logger.info(f"    Port: {dev_config['port']}")
        except Exception as e:
            logger.error(f"  ❌ {device_type} hatası: {e}")

    # 5. MQTT topic'lerini test et
    logger.info("\n📤 MQTT Topics:")
    topics = {
        "traffic_light": "congestion",
        "air_quality": "pm25",
        "trash_bin": "fill_level",
    }
    for device_type, metric in topics.items():
        try:
            topic = config.get_mqtt_topic(device_type, metric)
            logger.info(f"  {device_type}/{metric}: {topic}")
        except Exception as e:
            logger.error(f"  ❌ {device_type} hatası: {e}")

    # 6. Validation hatalarını kontrol et
    logger.info("\n✅ Validation Kontrol:")
    issues = config.validate()
    if issues:
        for issue in issues:
            logger.warning(f"  {issue}")
    else:
        logger.info("  ✅ Tüm kontroller geçildi!")

    logger.info("\n" + "=" * 60)
    logger.info("✨ Test Tamamlandı")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_configuration()

"""
AWS Lambda Function - IoT Sensör Verisini İşleme ve DynamoDB'ye Yazma
AWS IoT Core'dan gelen sensör verilerini analiz ederek DynamoDB tablosuna kaydeder
Özellikleri: Anomali tespiti, alert sistemi, veri doğrulaması
"""

import json
import boto3
from decimal import Decimal
from datetime import datetime

# DynamoDB istemcisini oluştur (AWS Lambda runtime'ında otomatik olarak credentials kurulur)
dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')

# DynamoDB tablosunu tanımla
# Adım 8'de bu tablo oluşturulacak, aynı isimle
TABLE_NAME = 'iot-sensor-data'
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    """
    Lambda fonksiyonunun ana işlev fonksiyonu
    AWS IoT Core tarafından çağrılır
    
    Yapılan işlemler:
    1. Sensör verisini alır
    2. Veri doğrulaması yapar
    3. Anomali tespiti yapar (sıcaklık ve nem eşikleri)
    4. DynamoDB'ye işlenmiş veriyi kaydeder
    5. Alert oluşturur (eğer uyarı durumu varsa)
    
    Args:
        event: IoT Core'dan alınan mesaj (sensör verisi)
        context: Lambda execution context
    
    Returns:
        dict: HTTP status ve mesaj döndürür
    """
    
    try:
        # IoT Core'dan gelen event'i loglama için yazdır
        print(f"[INPUT] Gelen IoT event: {json.dumps(event)}")
        
        # Event'ten sensör verilerini çıkar
        # Yapısı: { "sensor_id": "...", "location": "...", "temperature": X, "humidity": Y, "timestamp": "..." }
        sensor_id = event.get('sensor_id', 'unknown')
        location = event.get('location', 'unknown')
        temperature = float(event.get('temperature', 0.0))
        humidity = float(event.get('humidity', 0.0))
        timestamp = event.get('timestamp', datetime.utcnow().isoformat() + "Z")
        
        # Veri doğrulaması yap
        if not isinstance(temperature, (int, float)) or not isinstance(humidity, (int, float)):
            raise ValueError("Sıcaklık ve nem değerleri sayısal olmalıdır!")
        
        # ========================================
        # ADIM 1: ANOMALİ TESPİTİ (VERİ ANALİZİ)
        # ========================================
        alert_flag = False
        alert_messages = []
        alert_severity = "INFO"  # INFO, WARNING, CRITICAL
        
        # Sıcaklık kontrolleri
        if temperature > 30:  # UYARI: Çok yüksek sıcaklık
            alert_flag = True
            alert_messages.append(f"Yüksek sıcaklık tespit edildi: {temperature}°C (Eşik: 30°C)")
            if temperature > 35:  # KRİTİK: Tehlikeli derecede yüksek
                alert_severity = "CRITICAL"
            else:
                alert_severity = "WARNING"
        
        elif temperature < 15:  # UYARI: Çok düşük sıcaklık
            alert_flag = True
            alert_messages.append(f"Düşük sıcaklık tespit edildi: {temperature}°C (Eşik: 15°C)")
            if temperature < 0:  # KRİTİK: Donma noktası
                alert_severity = "CRITICAL"
            else:
                alert_severity = "WARNING"
        
        # Nem kontrolleri
        if humidity > 85:  # UYARI: Çok yüksek nem
            alert_flag = True
            alert_messages.append(f"Yüksek nem tespit edildi: {humidity}% (Eşik: 85%)")
            if alert_severity == "INFO":
                alert_severity = "WARNING"
        
        elif humidity < 25:  # UYARI: Çok düşük nem (kuruluk)
            alert_flag = True
            alert_messages.append(f"Düşük nem tespit edildi: {humidity}% (Eşik: 25%)")
            if alert_severity == "INFO":
                alert_severity = "WARNING"
        
        # ========================================
        # ADIM 2: VERİ İŞLEME
        # ========================================
        # DynamoDB'ye yazılacak item oluştur
        # ⚠️ ÖNEMLI: Float yerine Decimal kullan (DynamoDB requirement)
        item = {
            'sensor_id': sensor_id,                                    # Partition Key
            'timestamp': timestamp,                                    # Sort Key
            'location': location,                                      # Sensör konumu
            'temperature': Decimal(str(round(temperature, 2))),       # Sıcaklık (Decimal)
            'humidity': Decimal(str(round(humidity, 2))),             # Nem (Decimal)
            'received_at': datetime.utcnow().isoformat() + "Z",       # Alınma zamanı
            
            # ✅ ANALİZ SONUÇLARI
            'alert': alert_flag,                                       # Uyarı flag'ı
            'alert_severity': alert_severity,                          # Uyarı seviyesi (INFO/WARNING/CRITICAL)
            'alert_messages': alert_messages if alert_messages else ["Veri normaldir"],  # Uyarı mesajları
            'processed_at': datetime.utcnow().isoformat() + "Z",      # İşleme zamanı
            'analysis_version': "1.0"                                  # Analiz sürümü (raporlama için)
        }
        
        # DynamoDB'ye veriyi yaz
        response = table.put_item(Item=item)
        
        # ========================================
        # ADIM 3: LOGLAMA VE RESPONSE
        # ========================================
        log_message = f"""
[PROCESSED] ✓ Veri başarıyla işlendi ve kaydedildi:
  └─ Sensor ID: {sensor_id}
  └─ Konum: {location}
  └─ Sıcaklık: {temperature}°C
  └─ Nem: {humidity}%
  └─ Zaman: {timestamp}
  └─ ⚠️ ALERT: {alert_flag} (Severity: {alert_severity})
  └─ Alert Mesajları: {alert_messages}
"""
        print(log_message)
        
        # Başarılı response döndür
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Sensör verisi başarıyla işlendi ve kaydedildi',
                'sensor_id': sensor_id,
                'timestamp': timestamp,
                'alert': alert_flag,
                'alert_severity': alert_severity
            })
        }
    
    except KeyError as e:
        # Gelen event'te gerekli alan eksikse
        error_msg = f"Eksik veri alanı: {str(e)}"
        print(f"[ERROR] KeyError: {error_msg}")
        
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Başarısız',
                'message': error_msg
            })
        }
    
    except ValueError as e:
        # Veri tipi hatasıysa
        error_msg = f"Veri doğrulama hatası: {str(e)}"
        print(f"[ERROR] ValueError: {error_msg}")
        
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Başarısız',
                'message': error_msg
            })
        }
    
    except Exception as e:
        # Beklenmeyen bir hata oluştuysa
        error_msg = f"Beklenmeyen hata: {str(e)}"
        print(f"[ERROR] {error_msg}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'İç sunucu hatası',
                'message': error_msg
            })
        }
            'body': json.dumps({
                'error': 'Başarısız',
                'message': error_msg
            })
        }
    
    except Exception as e:
        # Diğer beklenmeyen hatalar
        error_msg = f"DynamoDB yazma hatası: {str(e)}"
        print(f"✗ Kritik hata: {error_msg}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Başarısız',
                'message': 'İç server hatası'
            })
        }

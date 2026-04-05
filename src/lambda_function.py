"""
AWS Lambda Function - IoT Sensör Verisini DynamoDB'ye Yazma
AWS IoT Core'dan gelen sensör verilerini alarak DynamoDB tablosuna kaydeder
"""

import json
import boto3
from datetime import datetime

# DynamoDB istemcisini oluştur (AWS Lambda runtime'ında otomatik olarak credentials kurulur)
dynamodb = boto3.resource('dynamodb')

# DynamoDB tablosunu tanımla
# Adım 8'de bu tablo oluşturulacak, aynı isimle
TABLE_NAME = 'iot-sensor-data'
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    """
    Lambda fonksiyonunun ana işlev fonksiyonu
    AWS IoT Core tarafından çağrılır
    
    Args:
        event: IoT Core'dan alınan mesaj (sensör verisi)
        context: Lambda execution context
    
    Returns:
        dict: HTTP status ve mesaj döndürür
    """
    
    try:
        # IoT Core'dan gelen event'i loglama için yazdır
        print(f"Gelen event: {json.dumps(event)}")
        
        # Event'ten sensör verilerini çıkar
        # Yapısı: { "sensor_id": "...", "location": "...", "temperature": X, "humidity": Y, "timestamp": "..." }
        sensor_id = event.get('sensor_id', 'unknown')
        location = event.get('location', 'unknown')
        temperature = event.get('temperature', 0.0)
        humidity = event.get('humidity', 0.0)
        timestamp = event.get('timestamp', datetime.utcnow().isoformat() + "Z")
        
        # Veri doğrulaması yap
        # Sıcaklık ve nem değerleri sayısal olmalıdır
        if not isinstance(temperature, (int, float)) or not isinstance(humidity, (int, float)):
            raise ValueError("Sıcaklık ve nem değerleri sayısal olmalıdır!")
        
        # DynamoDB'ye yazılacak item oluştur
        # Primary Key: sensor_id + timestamp (compound key)
        item = {
            'sensor_id': sensor_id,                          # Partition Key (sensör ID'si)
            'timestamp': timestamp,                          # Sort Key (zaman damgası)
            'location': location,                            # Sensörün konumu
            'temperature': round(temperature, 2),            # Sıcaklık (2 ondalak basamak)
            'humidity': round(humidity, 2),                  # Nem (2 ondalak basamak)
            'received_at': datetime.utcnow().isoformat() + "Z",  # Verilerin alındığı zaman
        }
        
        # DynamoDB'ye veriyi yaz
        # put_item: Yeni bir öğe oluşturur (var olanı üzerine de yazabilir)
        response = table.put_item(Item=item)
        
        # İşlem başarılıysa loglama
        print(f"✓ Veri başarıyla DynamoDB'ye yazıldı:")
        print(f"  Sensor ID: {sensor_id}")
        print(f"  Zaman: {timestamp}")
        print(f"  Sıcaklık: {temperature}°C")
        print(f"  Nem: {humidity}%")
        
        # Başarılı response döndür
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Sensör verisi başarıyla kaydedildi',
                'sensor_id': sensor_id,
                'timestamp': timestamp
            })
        }
    
    except KeyError as e:
        # Gelen event'te gerekli alan eksikse
        error_msg = f"Eksik veri alanı: {str(e)}"
        print(f"✗ Hata: {error_msg}")
        
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
        print(f"✗ Hata: {error_msg}")
        
        return {
            'statusCode': 400,
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

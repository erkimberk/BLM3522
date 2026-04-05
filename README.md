# Gerçek Zamanlı IoT Veri Akışı ve İşleme Projesi

**Dersin Adı:** 3522 Bulut Bilişim ve Uygulamaları
**Proje Adı:** Gerçek Zamanlı IoT Veri Akışı ve İşleme  
**Tarih:** Nisan 2026

## Proje Mimarisi

IoT Sensör (Python, simüle edilmiş) → MQTT → AWS IoT Core → AWS Lambda → AWS DynamoDB

## Proje Bileşenleri

1. **sensor_sim.py**: Sıcaklık ve nem verilerini simüle eden IoT sensörü
2. **lambda_function.py**: IoT Core'dan gelen veriyi alan ve DynamoDB'ye yazan AWS Lambda fonksiyonu
3. **requirements.txt**: Python kütüphaneleri listesi
4. **AWS Yapılandırması**: IoT Core Thing'i, Rule'lar, DynamoDB tablosu, IAM rolleri

## Gelişim Özeti

### Adım 1: Proje Yapısı ve Temel Dosyalar
Proje klasör yapısı oluşturuldu (src/, config/, certificates/, reports/). .gitignore dosyası sertifikalar ve hassas veriler için yapılandırıldı. README.md taslağı oluşturuldu.

### Adım 2: Python Kütüphaneleri (requirements.txt)
Proje için gerekli Python kütüphaneleri listelenmiştir:
- boto3 (AWS servisleri)
- paho-mqtt (MQTT protokolü)
- python-dotenv (Ortam değişkenleri)
- Diğer yardımcı kütüphaneler

### Adım 3: IoT Sensör Simülatörü (sensor_sim.py)
IoT sensörünün temel sınıfı yazılmıştır. Sıcaklık ve nem verilerini simüle ederek JSON formatında üretir. Henüz AWS bağlantısı yoktur.

### Adım 4: AWS IoT Core Thing ve Sertifikalar
AWS IoT Core'da "iot-sensor-001" Thing'i oluşturuldu. Sertifika dosyaları (cert.pem, private.key, AmazonRootCA1.pem) indirildi ve certificates/ klasörüne yerleştirildi. IoT Policy oluşturulup sertifikaya atanmıştır.

### Adım 5: Sensör Simülatörüne AWS MQTT Bağlantısı
sensor_sim.py dosyası AWS IoT Core'a MQTT aracılığıyla bağlanacak şekilde güncellenmiştir.
- MQTT bağlantısı kuruluyor
- Callback fonksiyonları uygulanmıştır
- TLS/SSL sertifikaları ile güvenli bağlantı sağlanmıştır
- Endpoint: avd01ikm8qx2k-ats.iot.eu-north-1.amazonaws.com
- Sensör verileri `sensors/{sensor_id}/data` topic'ine yayınlanır

### Adım 6: IoT Core → Lambda Rule (Kinesis yerine)
AWS IoT Core'da rule oluşturuldu. Topic'e gelen mesajlar direkt olarak Lambda fonksiyonunu trigger edecek. Kinesis, free tier'da ücretli olduğu için kullanılmamıştır. Mimarisi yeniden tasarlanmıştır: IoT Core → Lambda → DynamoDB.
- Rule: `iot_to_lambda_rule`
- SQL Select: `SELECT * FROM 'sensors/+/data'`
- Action: Lambda function `iot-sensor-processor` invoke'u
- IAM Role: `iot-to-lambda-role`

### Adım 7: AWS Lambda Function Yazılması
Lambda function (`lambda_function.py`) yazılmıştır. AWS Console'da `iot-sensor-processor` adıyla oluşturulmuştur.
- IoT Core'dan gelen mesajı alır
- Sensör verilerini (sensor_id, temperature, humidity, timestamp) validate eder
- DynamoDB tablosuna (`iot-sensor-data`) veriyi yazma işlemini gerçekleştirir
- Comprehensive error handling ve Türkçe loglama özelliği vardır
- DynamoDB erişim izni (IAM Policy) verilmiştir

---

## Kurulum Talimatları

(Sonraki adımlarla doldurulacak)

## Mimarinin Detaylı Açıklaması

(Sonraki adımlarla doldurulacak)

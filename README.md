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

### Adım 8: DynamoDB Tablosu ve IAM Yapılandırması
DynamoDB tablosu (`iot-sensor-data`) oluşturulmuştur:
- Partition Key: `sensor_id` (String)
- Sort Key: `timestamp` (String)
- Billing Mode: On-demand (Free Tier uyumlu)

Lambda Execution Role (`iot-sensor-processor-role-y4oq4s7m`) yetkilendirilmiştir:
- DynamoDB PutItem, GetItem, UpdateItem, Query izinleri verilmiştir
- IoT Core Rule ile Lambda entegrasyonu tamamlanmıştır

### Adım 9: Sistem Testi ve End-to-End Doğrulama
Sensör simülatörü çalıştırılarak tüm sistem test edilmiştir:
- IoT sensörü AWS IoT Core'a başarıyla bağlanmıştır
- Sensör verileri MQTT aracılığıyla gönderilmektedir
- IoT Core Rule, gelen mesajları Lambda'ya yönlendirmektedir
- Lambda function DynamoDB'ye veri yazmaktadır
- CloudWatch Logs'ta tüm işlemler izlenmektedir

**Sistem Mimarisi Tamam ve Çalışıyor!**

---

## Kurulum ve Çalıştırma Talimatları

### Python Ortamı Kurulması

```bash
# Virtual environment oluştur
python -m venv venv

# Activate et (Windows)
.\venv\Scripts\Activate.ps1

# Kütüphaneleri kur
pip install -r requirements.txt
```

### Sensör Simülatörünü Çalıştır

```bash
cd src
python sensor_sim.py
```

Sensör 10 adet MQTT mesajı gönderecek (her 2 saniyede bir).

### Verileri DynamoDB'de Kontrol Et

AWS Console → DynamoDB → Tables → iot-sensor-data → Explore table items

### Lambda Logs'ları Kontrol Et

AWS Console → CloudWatch → Log groups → /aws/lambda/iot-sensor-processor

---

## Mimarinin Detaylı Açıklaması

### Veri Akışı

1. **IoT Sensör Simülatörü** (sensor_sim.py)
   - Sıcaklık (°C) ve nem (%) verilerini simüle eder
   - Her 2 saniyede 1 veri oluşturur
   - MQTT protokolü ile AWS IoT Core'a gönderir
   - Topic formatı: `sensors/{sensor_id}/data`

2. **AWS IoT Core**
   - MQTT mesajlarını alır
   - Gelen mesajları kurallar (Rules) ile işler
   - SQL Select ile `sensors/+/data` topic'ini filtreler

3. **IoT Rule** (iot_to_lambda_rule)
   - Gelen MQTT mesajlarını Lambda function'a yönlendirir
   - Topic: `sensors/+/data` (wildcard ile tüm sensörler)

4. **AWS Lambda** (iot-sensor-processor)
   - IoT Core'dan gelen JSON verisini alır
   - Veri doğrulaması yapar (temperature, humidity sayısal mı?)
   - DynamoDB tablosuna PutItem işlemi ile yazıyor
   - Hatalar durumunda CloudWatch Logs'ta kaydeder

5. **AWS DynamoDB** (iot-sensor-data)
   - Sensör verilerini kalıcı olarak saklar
   - Partition Key: sensor_id
   - Sort Key: timestamp
   - Query yaparak geçmiş verileri analiz etme imkanı sağlar

### Teknolojiler ve Servisleri

- **Python 3.12+**: Sensör simülatörü ve Lambda function
- **paho-mqtt**: MQTT protokolü üzerinden bağlantı
- **boto3**: AWS servisleri ile etkileşim (Lambda için)
- **AWS IoT Core**: IoT cihazları için merkezi hub
- **AWS Lambda**: Serverless compute (event-driven)
- **AWS DynamoDB**: Fully managed NoSQL veritabanı
- **AWS IAM**: Erişim kontrolü ve yetkilendirme
- **AWS CloudWatch**: Logging ve monitoring

### Güvenlik

- **TLS 1.2 Encryption**: MQTT bağlantısı şifrelenmiş
- **X.509 Sertifikaları**: IoT Thing'in dijital sertifikası
- **IAM Roles & Policies**: Least privilege principle ile sınırlandırılmıştır
- **.gitignore**: Sertifika dosyaları GitHub'a çıkmazsa engel vardır

---

## Dosya Yapısı

```
Project2/
├── .gitignore                 # Git ignore kuralları (sertifikalar hariç)
├── README.md                  # Bu dosya
├── requirements.txt           # Python kütüphaneleri
├── src/
│   ├── sensor_sim.py         # IoT sensör simülatörü (MQTT)
│   └── lambda_function.py    # AWS Lambda function kodu
├── config/                    # AWS konfigürasyonları
├── certificates/              # AWS sertifikaları (gitignore'da)
│   ├── iot-sensor-001.cert.pem
│   ├── iot-sensor-001.private.key
│   └── AmazonRootCA1.pem
└── reports/                   # Proje raporları
```

---

## Ücretlendirme Notları

- **AWS IoT Core**: Free Tier (250.000 mesaj/ay)
- **AWS Lambda**: Free Tier (1.000.000 çağrı/ay)
- **AWS DynamoDB**: On-demand (Free Tier kapsamı)
- **CloudWatch Logs**: Free Tier (5GB ingestion/month)

**Toplam Ücret: Free Tier kapsamında (ücretli değil)**

---

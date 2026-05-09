# 🏙️ IoT Akıllı Şehir Uygulaması

## Proje Açıklaması
Bu proje, AWS IoT Core ve MQTT protokolü kullanarak sanal IoT sensörlerinden veri toplayıp, işleyen ve gerçek zamanlı olarak görselleştiren bir akıllı şehir uygulamasıdır.

### Sensörler:
- 🚦 **Smart Traffic Light**: Trafik yoğunluğu ölçümü
- 💨 **Air Quality Sensor**: Hava kalitesi parametreleri
- 🗑️ **Trash Bin Fill Level**: Çöp kutusu doluluk oranı

## Teknoloji Stack
- **IoT Simülasyonu**: Python 3.11+
- **MQTT Broker**: AWS IoT Core
- **Backend**: AWS Lambda + DynamoDB
- **Frontend**: HTML5 + JavaScript + Chart.js
- **Protokol**: MQTT over TLS/SSL

## Klasör Yapısı
```
Project 4/
├── src/
│   ├── devices/          # IoT cihaz simülatörleri
│   ├── lambda/           # AWS Lambda fonksiyonları
│   └── utils/            # Utility fonksiyonlar
├── frontend/             # Web dashboard
├── config/               # Konfigürasyon & Sertifikalar
├── docs/                 # Proje raporları
├── requirements.txt      # Python dependencies
├── .env.example          # Environment değişkenler template
└── README.md
```

## Kurulum (Adım 1)

### 1. Virtual Environment Oluştur
```bash
python -m venv venv

# Windows'da activate:
venv\Scripts\activate

# Linux/macOS'da activate:
source venv/bin/activate
```

### 2. Dependencies Kur
```bash
pip install -r requirements.txt
```

### 3. Environment Değişkenlerini Ayarla
```bash
cp .env.example .env
# .env dosyasını düzenle ve AWS credentials'ını ekle
```

## Yol Haritası
- [ ] Adım 1: Proje Kurulumu & AWS Ortam Hazırlığı ✅ (BURADA)
- [ ] Adım 2: AWS IoT Core Konfigürasyonu
- [ ] Adım 3: Python IoT Cihaz Simülatörü
- [ ] Adım 4: AWS Lambda & DynamoDB
- [ ] Adım 5: Frontend Dashboard & REST API

## Geliştirme Notları
Her commit öncesinde:
```bash
black src/          # Code formatting
pylint src/         # Code linting
git add .
git commit -m "feat/fix/docs: açıklamalı mesaj"
```

---
**Son Güncelleme**: Adım 1 - Proje Kurulumu (9 Mayıs 2026)

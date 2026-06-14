# Müşteri Kaybı (Churn) Tahmini - Bulut Bilişim Projesi

Telco müşteri verisi üzerinde makine öğrenmesi modeli eğitilerek,
bir müşterinin abonelikten ayrılma (churn) olasılığı tahmin edilir.
Model AWS Lambda üzerine dağıtılır ve bulut üzerinden tahmin alınır.

## Kullanılan Teknolojiler
- **Dil:** Python
- **ML Kütüphanesi:** Scikit-learn
- **Bulut:** AWS Lambda
- **Veri Seti:** Telco Customer Churn

## Mimari
Veri seti → Bilgisayarda model eğitimi → Model AWS Lambda'ya yüklenir → Bulut üzerinden tahmin

## İçindekiler
- notebooks/ : Eğitim kodu
- model/ : Eğitilmiş model dosyası
- lambda/ : Bulut tahmin fonksiyonu
- docs/ : Adım adım dokümantasyon
# Müşteri Kaybı (Churn) Tahmini — Bulut Bilişim Projesi

Telco müşteri verisi üzerinde bir makine öğrenmesi modeli eğitilerek, bir
müşterinin abonelikten ayrılma (churn) olasılığı tahmin edilmektedir. Eğitilen
model AWS Lambda üzerine dağıtılmış ve bulut üzerinden tahmin alınmıştır.

## Kullanılan Teknolojiler
- Dil: Python 3
- ML Kütüphanesi: Scikit-learn (Lojistik Regresyon)
- Veri İşleme: Pandas, NumPy
- Bulut: AWS Lambda, AWS S3, AWS CloudShell, Lambda Layers
- Veri Seti: IBM Telco Customer Churn (~7000 müşteri)

## Mimari
Veri seti → Bilgisayarda model eğitimi → Model AWS Lambda'ya dağıtılır →
Bulut üzerinden tahmin alınır

## Proje Yapısı
- `notebooks/` : Veri keşfi, temizleme, model eğitimi kodları
- `model/` : Eğitilmiş model ve sütun listesi
- `lambda/` : Bulut tahmin fonksiyonu (AWS Lambda)
- `docs/` : Her aşamanın adım adım dokümantasyonu
- `screenshots/` : AWS ekran görüntüleri
- `RAPOR.md` : Projenin tam raporu

## Sonuç
Model %79 doğrulukla çalışmakta ve AWS Lambda üzerinden gönderilen müşteri
verisine göre churn tahmini üretmektedir. Bulut üzerinden alınan tahmin,
yerel ortamdaki sonuçla birebir aynıdır.

## Çalıştırma
Detaylı kurulum ve çalıştırma adımları `docs/` klasöründeki belgelerde
aşama aşama açıklanmıştır.
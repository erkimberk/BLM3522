# 6. AWS Lambda'ya Dağıtım

## Amaç
Eğitilen model, AWS Lambda üzerine dağıtılarak bulut üzerinden tahmin
yapabilen bir servise dönüştürüldü.

## Yapılan İşlemler
1. **Lambda Layer hazırlandı:** scikit-learn, scipy, numpy, joblib ve
   narwhals kütüphaneleri AWS CloudShell ortamında Linux uyumlu olarak
   kuruldu, gereksiz test dosyaları temizlenerek boyut sınırının altına
   indirildi, S3 üzerinden Layer olarak yayınlandı.
2. **Lambda fonksiyonu oluşturuldu:** Model dosyaları (churn_model.pkl,
   sutunlar.pkl) ve tahmin kodu (lambda_function.py) bir zip içinde
   AWS CLI ile yüklendi. Fonksiyon Python 3.13 çalışma ortamıyla oluşturuldu.
3. **Layer bağlandı:** Hazırlanan kütüphane katmanı fonksiyona eklendi.
4. **Test edildi:** Örnek bir müşteri verisi gönderilerek bulut üzerinden
   tahmin alındı. Sonuç, yerel ortamda alınan tahminle birebir aynı çıktı.

## Karşılaşılan Zorluklar ve Çözümleri
- **numpy sürüm uyumsuzluğu:** Kütüphaneler Python 3.13 için derlendiğinden,
  Lambda çalışma ortamı da 3.13'e geçirilerek çözüldü.
- **Eksik modüller (narwhals, scipy.spatial.transform):** Layer boyutunu
  küçültmek için yapılan agresif temizlikte, scikit-learn'ün ihtiyaç duyduğu
  bazı modüller yanlışlıkla silinmişti. Bu modüller geri yüklenerek ve sadece
  gerçekten gereksiz olan test/cache klasörleri silinerek çözüldü.

## Sonuç
Model AWS Lambda üzerinde başarıyla çalışmakta ve gönderilen müşteri
verisine göre churn tahmini üretmektedir.
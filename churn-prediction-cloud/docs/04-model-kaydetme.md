# 4. Modelin Kaydedilmesi

Eğitilen model, bulut ortamına taşınabilmesi için diske kaydedildi.

## Yapılan İşlemler
1. Model, joblib kütüphanesi ile `model/churn_model.pkl` dosyasına
   serileştirilerek kaydedildi. Bu sayede model her seferinde yeniden
   eğitilmeden, doğrudan yüklenip tahmin için kullanılabilir.
2. Modelin beklediği girdi sütunlarının isim ve sırası `model/sutunlar.pkl`
   dosyasına kaydedildi. Tahmin aşamasında gelen verinin doğru sütun
   sırasına yerleştirilmesi için bu liste gereklidir.

## Sonuç
Model ve sütun bilgisi, AWS Lambda üzerine yüklenmeye hazır hale getirildi.
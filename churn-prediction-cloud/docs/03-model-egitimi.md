# 3. Model Eğitimi

## Yöntem
Temizlenmiş veri seti, girdiler (X) ve hedef değişken (Churn) olarak ayrıldı.
Veri %80 eğitim, %20 test olacak şekilde bölündü. Sonuçların tekrarlanabilir
olması için sabit bir random_state kullanıldı.

## Model
Sınıflandırma problemi için Lojistik Regresyon (Logistic Regression) modeli
kullanıldı. Bu model, evet/hayır türündeki ikili sınıflandırma problemleri
için yaygın, hızlı ve yorumlanabilir bir yöntemdir.

## Değerlendirme
Model, eğitimde görmediği test verisi üzerinde değerlendirildi. Doğruluk
(accuracy) değerinin yanında, sınıf dengesizliği nedeniyle kesinlik
(precision) ve duyarlılık (recall) metrikleri de incelendi.

## Sonuçlar
- Doğruluk (Accuracy): [çıktındaki değeri yaz, ~0.80 civarı]
- Ayrılan müşterileri (Churn=1) yakalama oranı (recall), kalan müşterilere
  göre daha düşüktür. Bunun nedeni veri setindeki sınıf dengesizliğidir.
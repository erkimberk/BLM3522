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
Model, eğitimde görmediği test verisi (1407 müşteri) üzerinde değerlendirildi.
Doğruluk değerinin yanında, sınıf dengesizliği nedeniyle kesinlik (precision)
ve duyarlılık (recall) metrikleri de incelendi.

## Sonuçlar
- Doğruluk (Accuracy): 0.7875 (yaklaşık %79)
- Kalan müşteriler (Churn=0): precision 0.83, recall 0.89, f1-score 0.86
- Ayrılan müşteriler (Churn=1): precision 0.62, recall 0.52, f1-score 0.56

## Karmaşıklık Matrisi
|                | Tahmin: Kaldı | Tahmin: Ayrıldı |
|----------------|---------------|------------------|
| Gerçek: Kaldı  | 915           | 118              |
| Gerçek: Ayrıldı| 181           | 193              |

## Yorum
Model %79 doğrulukla çalışmaktadır. Kalan müşterileri yüksek başarıyla
(recall 0.89) tahmin ederken, ayrılan müşterileri yakalama oranı daha
düşüktür (recall 0.52). Bunun temel nedeni, veri setindeki sınıf
dengesizliğidir: veride kalan müşteri sayısı, ayrılan müşteri sayısının
yaklaşık üç katıdır. Karmaşıklık matrisine göre model, gerçekte ayrılan
374 müşterinin 193'ünü doğru tahmin etmiş, 181'ini kaçırmıştır. Bu sonuç,
churn tahmini problemleri için kabul edilebilir bir başlangıç performansıdır.
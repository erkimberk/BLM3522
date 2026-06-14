# 1. Veri Keşfi

## Veri Seti
Bu projede IBM Telco Customer Churn veri seti kullanılmıştır. Veri seti,
bir telekomünikasyon şirketinin müşterilerine ait abonelik bilgilerini ve
her müşterinin hizmetten ayrılıp ayrılmadığı (churn) bilgisini içerir.

## Genel Yapı
- Satır sayısı: 7043 müşteri
- Sütun sayısı: 21
- Hedef değişken: `Churn` (Yes = ayrıldı, No = kaldı)

## Sütunlar
Veri setinde müşteriye ait demografik bilgiler (cinsiyet, yaşlı vatandaş mı,
partneri var mı), hizmet bilgileri (telefon, internet, online güvenlik,
teknik destek vb.), sözleşme tipi, ödeme yöntemi ve ücret bilgileri
(aylık ücret, toplam ücret) bulunmaktadır.

## Hedef Değişken Dağılımı
- Kalan müşteriler (No): 5174 (~%73)
- Ayrılan müşteriler (Yes): 1869 (~%27)

Sınıf dağılımı dengesizdir. Bu durum, model değerlendirmesinde yalnızca
doğruluk (accuracy) değil, kesinlik (precision) ve duyarlılık (recall)
metriklerinin de dikkate alınmasını gerektirir.

## Eksik Veri Notu
`isnull()` kontrolünde eksik veri görünmemektedir. Ancak `TotalCharges`
sütunu sayısal olması gerekirken metin (object) tipinde okunmuştur ve
içinde boşluk karakterinden oluşan birkaç geçersiz değer bulunmaktadır.
Bu değerler veri temizleme aşamasında ele alınacaktır.
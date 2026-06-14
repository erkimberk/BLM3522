# 7. Veritabanı Entegrasyonu (DynamoDB)

## Amaç
Yapılan her tahminin saklanması ve geçmiş tahminlerin sorgulanabilmesi için
AWS DynamoDB veritabanı entegre edilmiştir. Böylece sistem yalnızca tahmin
üretmekle kalmaz, ürettiği bilgiyi kalıcı olarak da saklar.

## Yapılan İşlemler
1. **Tablo oluşturuldu:** `churn-tahminleri` adında, benzersiz `id` anahtarına
   sahip bir DynamoDB tablosu oluşturuldu. Talep başına ödeme (PAY_PER_REQUEST)
   modu seçildi; bu mod Free Tier kapsamında küçük kullanımlar için ücretsizdir.
2. **Yetkilendirme:** Lambda fonksiyonunun role'üne DynamoDB yazma izni eklendi.
3. **Kod entegrasyonu:** Lambda fonksiyonu, her tahminden sonra boto3 kütüphanesi
   ile tabloya bir kayıt eklemektedir. Kayıtta benzersiz id, zaman damgası, gelen
   müşteri verisi, tahmin sonucu ve ayrılma olasılığı tutulur.

## Teknik Not
DynamoDB ondalık sayıları Decimal tipinde sakladığından, ayrılma olasılığı
değeri kayıt öncesinde Decimal tipine dönüştürülmüştür. Ayrıca boto3
kütüphanesi AWS Lambda ortamında hazır geldiği için ek bir kütüphane
katmanına ihtiyaç duyulmamıştır.

## Sonuç
Her tahmin sonucu DynamoDB tablosuna başarıyla kaydedilmektedir. Tablo
içeriği `scan` komutu ile sorgulanarak doğrulanmıştır.
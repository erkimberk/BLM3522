# 2. Veri Temizleme ve Ön İşleme

Modelin veriyi doğru işleyebilmesi için aşağıdaki temizleme adımları uygulanmıştır.

## Yapılan İşlemler
1. **customerID sütunu çıkarıldı:** Her müşteriye özel kimlik bilgisi olduğu
   için tahmin açısından anlamsızdır.
2. **TotalCharges düzeltildi:** Sütun metin tipinde okunmuştu. Sayısal tipe
   çevrildi ve çevrilemeyen boş değerler (11 satır) veri setinden çıkarıldı.
3. **Hedef değişken sayısallaştırıldı:** Churn sütunundaki Yes/No değerleri
   1/0 olarak kodlandı.
4. **Kategorik sütunlar sayısallaştırıldı:** Cinsiyet, sözleşme tipi, ödeme
   yöntemi gibi metin sütunları one-hot encoding yöntemiyle sayısal sütunlara
   dönüştürüldü.

## Sonuç
Temizlenmiş veri seti modelin eğitilebileceği tamamen sayısal bir yapıya
getirildi ve `data/churn_temiz.csv` dosyasına kaydedildi.
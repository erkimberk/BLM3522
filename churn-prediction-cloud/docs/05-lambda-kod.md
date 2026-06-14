# 5. Tahmin Fonksiyonunun Yazılması ve Yerel Testi

## Amaç
Modelin bulut üzerinde tahmin yapabilmesi için AWS Lambda formatında bir
tahmin fonksiyonu yazıldı. Bulut ortamına yüklemeden önce fonksiyon yerel
ortamda test edilerek doğru çalıştığı doğrulandı.

## lambda_function.py
Fonksiyon, AWS Lambda'nın beklediği `lambda_handler(event, context)` yapısında
yazıldı. İşleyiş şu şekildedir:
1. Dışarıdan gelen müşteri verisi okunur.
2. Veri, modelin beklediği sütun yapısına dönüştürülür; eksik sütunlar 0 ile
   doldurulur ve sütun sırası modele göre düzenlenir.
3. Model tahmini ve ayrılma olasılığı hesaplanır.
4. Sonuç JSON formatında döndürülür.

## Yerel Test
Örnek bir müşteri profili ile fonksiyon yerelde çalıştırıldı ve tahmin
sonucu başarıyla alındı. Bu sayede kod, buluta yüklenmeden önce doğrulanmış oldu.

## Sonuç
Tahmin fonksiyonu yerelde doğru çalışmaktadır ve AWS Lambda'ya yüklenmeye hazırdır.
from lambda_function import lambda_handler

# Örnek bir müşteri (birkaç özellik veriyoruz, gerisi otomatik 0 olur)
ornek_musteri = {
    "tenure": 2,                          # 2 aydır müşteri (yeni)
    "MonthlyCharges": 85.0,               # yüksek aylık ücret
    "TotalCharges": 170.0,
    "Contract_Two year": 0,               # uzun sözleşmesi yok
    "InternetService_Fiber optic": 1      # fiber kullanıyor
}

# Lambda fonksiyonunu yerelde çağır
sonuc = lambda_handler(ornek_musteri, None)
print("Sonuç:")
print(sonuc["body"])
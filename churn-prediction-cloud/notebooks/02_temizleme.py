import pandas as pd

# Veriyi oku
df = pd.read_csv("data/churn.csv")
print("Başlangıç boyutu:", df.shape)

# 1) customerID sütununu at (tahmin için anlamsız, her müşteriye özel kimlik)
df = df.drop("customerID", axis=1)

# 2) TotalCharges tuzağını çöz: metni sayıya çevir, çevrilemeyenler NaN olur
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
print("\nTotalCharges içindeki boş (NaN) değer sayısı:", df["TotalCharges"].isnull().sum())

# Bu boş satırları at (sadece 11 tane, veri setinin çok küçük bir kısmı)
df = df.dropna()
print("Temizlik sonrası boyut:", df.shape)

# 3) Hedef değişkeni sayıya çevir: Yes -> 1, No -> 0
df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

# 4) Diğer tüm metin (kategorik) sütunları sayıya çevir (one-hot encoding)
df = pd.get_dummies(df, drop_first=True)

print("\nSon boyut (sütunlar sayıya çevrildikten sonra):", df.shape)
print("\nSon sütunların bir kısmı:")
print(df.columns.tolist()[:15])

# Temizlenmiş veriyi kaydet (bir sonraki fazda kullanacağız)
df.to_csv("data/churn_temiz.csv", index=False)
print("\nTemizlenmiş veri 'data/churn_temiz.csv' olarak kaydedildi.")
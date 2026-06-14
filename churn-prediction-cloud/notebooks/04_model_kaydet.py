import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# Temizlenmiş veriyi oku
df = pd.read_csv("data/churn_temiz.csv")

# Girdi ve hedef ayır
X = df.drop("Churn", axis=1)
y = df["Churn"]

# Eğitim/test böl (öncekiyle aynı ayar)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modeli eğit
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)
print("Model eğitildi.")

# Modeli diske kaydet
joblib.dump(model, "model/churn_model.pkl")
print("Model 'model/churn_model.pkl' olarak kaydedildi.")

# Sütun isimlerini de kaydet (Lambda tahmin sırasında doğru sırayı bilmeli)
sutunlar = X.columns.tolist()
joblib.dump(sutunlar, "model/sutunlar.pkl")
print("Sütun listesi 'model/sutunlar.pkl' olarak kaydedildi.")
print("Toplam sütun sayısı:", len(sutunlar))
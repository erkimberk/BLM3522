import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Temizlenmiş veriyi oku
df = pd.read_csv("data/churn_temiz.csv")

# Girdiler (X) ve hedef (y) ayır
X = df.drop("Churn", axis=1)   # Churn dışındaki tüm sütunlar = girdiler
y = df["Churn"]                # Churn = tahmin edeceğimiz hedef

# Eğitim (%80) ve test (%20) olarak böl
# random_state=42 -> her çalıştırmada aynı bölme, sonuçlar tekrarlanabilir olsun
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Eğitim seti boyutu:", X_train.shape)
print("Test seti boyutu:", X_test.shape)

# Modeli oluştur ve eğit
# max_iter=1000 -> modelin yeterince öğrenmesi için iterasyon sayısı
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Test seti üzerinde tahmin yap
y_pred = model.predict(X_test)

# Sonuçları ölç
print("\n=== SONUÇLAR ===")
print("Doğruluk (Accuracy):", round(accuracy_score(y_test, y_pred), 4))
print("\nDetaylı rapor:")
print(classification_report(y_test, y_pred, target_names=["Kaldı (0)", "Ayrıldı (1)"]))
print("Karmaşıklık Matrisi:")
print(confusion_matrix(y_test, y_pred))
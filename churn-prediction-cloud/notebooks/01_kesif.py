import pandas as pd

# Veriyi oku
df = pd.read_csv("data/churn.csv")

# İlk bakış
print("Satır ve sütun sayısı:", df.shape)
print("\nİlk 5 satır:")
print(df.head())

print("\nSütun isimleri:")
print(df.columns.tolist())

print("\nHedef değişken (Churn) dağılımı:")
print(df["Churn"].value_counts())

print("\nEksik veri kontrolü:")
print(df.isnull().sum())
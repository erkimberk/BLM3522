import json
import joblib
import pandas as pd
import os

# Model ve sütun listesini yükle (fonksiyon dışında: bir kez yüklenir, hızlı olur)
KLASOR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(KLASOR, "..", "model", "churn_model.pkl"))
sutunlar = joblib.load(os.path.join(KLASOR, "..", "model", "sutunlar.pkl"))

def lambda_handler(event, context):
    """
    AWS Lambda'nın çağıracağı ana fonksiyon.
    event: dışarıdan gelen veri (müşteri bilgileri)
    """
    try:
        # Gelen veriyi al (Lambda'da JSON string olarak gelir)
        if "body" in event:
            veri = json.loads(event["body"])
        else:
            veri = event

        # Gelen veriyi modelin beklediği sütun yapısına çevir
        df = pd.DataFrame([veri])
        # Eksik sütunları 0 ile doldur, sırayı modele göre düzenle
        df = df.reindex(columns=sutunlar, fill_value=0)

        # Tahmin yap
        tahmin = int(model.predict(df)[0])
        olasilik = float(model.predict_proba(df)[0][1])

        sonuc = {
            "churn_tahmini": tahmin,           # 1 = ayrılır, 0 = kalır
            "ayrilma_olasiligi": round(olasilik, 4),
            "aciklama": "Ayrılır" if tahmin == 1 else "Kalır"
        }

        return {
            "statusCode": 200,
            "body": json.dumps(sonuc)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"hata": str(e)})
        }
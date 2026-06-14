import json
import joblib
import numpy as np
import os

# Model ve sütun listesini yükle
KLASOR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(KLASOR, "churn_model.pkl"))
sutunlar = joblib.load(os.path.join(KLASOR, "sutunlar.pkl"))

def lambda_handler(event, context):
    try:
        # Gelen veriyi al
        if "body" in event:
            veri = json.loads(event["body"])
        else:
            veri = event

        # Sütun sırasına göre numpy array oluştur (pandas yerine)
        # Gönderilmeyen her özellik 0 kabul edilir
        satir = [float(veri.get(sutun, 0)) for sutun in sutunlar]
        X = np.array([satir])

        # Tahmin yap
        tahmin = int(model.predict(X)[0])
        olasilik = float(model.predict_proba(X)[0][1])

        sonuc = {
            "churn_tahmini": tahmin,
            "ayrilma_olasiligi": round(olasilik, 4),
            "aciklama": "Ayrilir" if tahmin == 1 else "Kalir"
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
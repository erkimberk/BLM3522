import json
import joblib
import numpy as np
import os
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

# Model ve sütun listesini yükle
KLASOR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(KLASOR, "churn_model.pkl"))
sutunlar = joblib.load(os.path.join(KLASOR, "sutunlar.pkl"))

# DynamoDB bağlantısı
dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")
tablo = dynamodb.Table("churn-tahminleri")

def lambda_handler(event, context):
    try:
        if "body" in event:
            veri = json.loads(event["body"])
        else:
            veri = event

        # Sütun sırasına göre numpy array oluştur
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

        # Sonucu DynamoDB'ye kaydet
        tablo.put_item(Item={
            "id": str(uuid.uuid4()),                    # benzersiz kayıt no
            "zaman": datetime.utcnow().isoformat(),     # tahmin zamanı
            "girdi": json.dumps(veri),                  # gelen müşteri verisi
            "churn_tahmini": tahmin,
            "ayrilma_olasiligi": Decimal(str(round(olasilik, 4))),  # DynamoDB Decimal ister
            "aciklama": sonuc["aciklama"]
        })

        return {
            "statusCode": 200,
            "body": json.dumps(sonuc)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"hata": str(e)})
        }
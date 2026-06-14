import boto3
from decimal import Decimal

# DynamoDB kaynağını başlat
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('VideoAnalizSonuclari')

def save_analysis(video_id, result):
    """Rekognition analiz sonuçlarını DynamoDB'ye kaydeder."""
    if not result:
        print("Kaydedilecek sonuç yok.")
        return

    # Etiketleri sadeleştirip listeye çeviriyoruz
    labels = []
    for item in result['Labels']:
        labels.append({
            'isim': item['Label']['Name'],
            'guven': Decimal(str(round(item['Label']['Confidence'], 1))),
            'zaman_ms': item['Timestamp']
        })

    # Tabloya yaz
    table.put_item(
        Item={
            'VideoId': video_id,
            'etiket_sayisi': len(labels),
            'etiketler': labels
        }
    )
    print(f"Kaydedildi: {video_id} ({len(labels)} etiket)")
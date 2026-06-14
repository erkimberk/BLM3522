import boto3
import json
from decimal import Decimal

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('VideoAnalizSonuclari')

def lambda_handler(event, context):
    # SNS mesajını çöz
    sns_message = event['Records'][0]['Sns']['Message']
    data = json.loads(sns_message)

    job_id = data['JobId']
    status = data['Status']
    video_key = data.get('JobTag', 'bilinmiyor')

    print(f"SNS bildirimi alındı. JobId: {job_id}, Durum: {status}, Video: {video_key}")

    if status != 'SUCCEEDED':
        print("Analiz başarılı değil, işlem durduruldu.")
        return

    # Rekognition'dan sonuçları çek
    response = rekognition.get_label_detection(JobId=job_id, SortBy='TIMESTAMP')

    labels = []
    for item in response['Labels']:
        labels.append({
            'isim': item['Label']['Name'],
            'guven': Decimal(str(round(item['Label']['Confidence'], 1))),
            'zaman_ms': item['Timestamp']
        })

    # DynamoDB'ye yaz
    table.put_item(
        Item={
            'VideoId': video_key,
            'etiket_sayisi': len(labels),
            'etiketler': labels
        }
    )
    print(f"DynamoDB'ye kaydedildi: {video_key} ({len(labels)} etiket)")
    return {'kaydedilen_etiket': len(labels)}
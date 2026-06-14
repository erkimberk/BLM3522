import boto3
import urllib.parse

rekognition = boto3.client('rekognition')

# Rekognition'ın bildirim göndereceği SNS topic ve kullanacağı rol
SNS_TOPIC_ARN = 'arn:aws:sns:eu-central-1:271003694403:RekognitionTamamlandi'
ROLE_ARN = 'arn:aws:iam::271003694403:role/RekognitionSNSRole'

def lambda_handler(event, context):
    # S3 olayından bucket ve dosya adını al
    record = event['Records'][0]['s3']
    bucket = record['bucket']['name']
    key = urllib.parse.unquote_plus(record['object']['key'])

    print(f"Yeni video algılandı: s3://{bucket}/{key}")

    # Sadece uploads/ klasöründeki ve video uzantılı dosyaları işle
    if not key.startswith('uploads/') or not key.lower().endswith(('.mp4', '.mov', '.avi')):
        print("Video değil veya uploads/ dışında, atlanıyor.")
        return

    # Rekognition analizini başlat
    response = rekognition.start_label_detection(
        Video={'S3Object': {'Bucket': bucket, 'Name': key}},
        MinConfidence=70,
        NotificationChannel={
            'SNSTopicArn': SNS_TOPIC_ARN,
            'RoleArn': ROLE_ARN
        },
        JobTag=key  # hangi videoya ait olduğunu sonra anlamak için
    )

    print(f"Analiz başlatıldı. JobId: {response['JobId']}")
    return {'JobId': response['JobId']}
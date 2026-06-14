import boto3
import time
import sys
from save_results import save_analysis

# Rekognition istemcisini başlat
rekognition = boto3.client('rekognition')

BUCKET = 'video-analiz-projesi-23291218'

def start_label_detection(video_key):
    """Video için etiket (nesne) tespit işini başlatır, JobId döner."""
    response = rekognition.start_label_detection(
        Video={'S3Object': {'Bucket': BUCKET, 'Name': video_key}},
        MinConfidence=70  # %70'in altındaki tahminleri eleriz
    )
    job_id = response['JobId']
    print(f"Analiz başlatıldı. Job ID: {job_id}")
    return job_id

def get_results(job_id):
    """İş bitene kadar bekler, sonra sonuçları döner."""
    print("Sonuçlar bekleniyor...")
    while True:
        response = rekognition.get_label_detection(
            JobId=job_id,
            SortBy='TIMESTAMP'  # sonuçları zamana göre sırala
        )
        status = response['JobStatus']

        if status == 'SUCCEEDED':
            print("Analiz tamamlandı!")
            return response
        elif status == 'FAILED':
            print("Analiz başarısız oldu.")
            return None
        else:
            print("  İşleniyor... 5 saniye bekleniyor")
            time.sleep(5)

def print_labels(result):
    """Tespit edilen etiketleri zaman damgalarıyla yazdırır."""
    if not result:
        return
    print("\n--- TESPİT EDİLEN NESNELER ---")
    for item in result['Labels'][:30]:  # ilk 30 tanesi
        label = item['Label']
        timestamp_sn = item['Timestamp'] / 1000  # ms -> saniye
        print(f"{timestamp_sn:6.1f}s | {label['Name']:20s} | %{label['Confidence']:.1f}")

if __name__ == "__main__":
    video_key = sys.argv[1] if len(sys.argv) > 1 else "uploads/test.mp4"
    job = start_label_detection(video_key)
    result = get_results(job)
    print_labels(result)
    # Sonuçları DynamoDB'ye kaydet
    save_analysis(video_key, result)
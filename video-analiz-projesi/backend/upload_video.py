import boto3
import os
import sys

# S3 istemcisini başlat
s3 = boto3.client('s3')

BUCKET = 'video-analiz-projesi-23291218'

def upload_video(local_path, s3_key):
    """Yerel bir video dosyasını S3 bucket'ına yükler."""
    if not os.path.exists(local_path):
        print(f"HATA: Dosya bulunamadı -> {local_path}")
        return

    print(f"Yükleniyor: {local_path} ...")
    s3.upload_file(local_path, BUCKET, s3_key)
    print(f"Başarılı! Konum: s3://{BUCKET}/{s3_key}")

if __name__ == "__main__":
    # Komut satırından dosya yolu verilebilir, verilmezse varsayılan kullanılır
    local_file = sys.argv[1] if len(sys.argv) > 1 else "test.mp4"
    s3_key = "uploads/" + os.path.basename(local_file)
    upload_video(local_file, s3_key)
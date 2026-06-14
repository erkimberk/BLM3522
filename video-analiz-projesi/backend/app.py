from flask import Flask, render_template, request, redirect, url_for
import boto3
import os

app = Flask(__name__)

BUCKET = 'video-analiz-projesi-23291218'
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('VideoAnalizSonuclari')

# Geçici yükleme klasörü
UPLOAD_DIR = 'temp_uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route('/')
def index():
    """Tüm analiz edilmiş videoları listeler."""
    response = table.scan()
    videolar = response.get('Items', [])
    return render_template('index.html', videolar=videolar)


@app.route('/upload', methods=['POST'])
def upload():
    """Yüklenen videoyu S3'e gönderir (otomasyon analizi başlatır)."""
    file = request.files.get('video')
    if not file or file.filename == '':
        return redirect(url_for('index'))

    # Geçici kaydet, sonra S3'e yükle
    local_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(local_path)

    s3_key = 'uploads/' + file.filename
    s3.upload_file(local_path, BUCKET, s3_key)
    os.remove(local_path)

    return redirect(url_for('index'))


@app.route('/detay/<path:video_id>')
def detay(video_id):
    """Bir videonun tüm etiketlerini gösterir."""
    response = table.get_item(Key={'VideoId': video_id})
    video = response.get('Item')
    return render_template('detay.html', video=video)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
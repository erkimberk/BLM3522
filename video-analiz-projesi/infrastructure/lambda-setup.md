# Otomasyon Kurulumu (Lambda + SNS + Rekognition)

Bu doküman, S3'e yüklenen videoların otomatik olarak analiz edilmesi için
kurulan altyapıyı adım adım açıklar.

## Mimari Akış
1. Kullanıcı videoyu S3 bucket'ındaki `uploads/` klasörüne yükler.
2. S3, yeni dosya olayını (event) Lambda fonksiyonunu tetikleyerek bildirir.
3. Lambda, AWS Rekognition'ın asenkron Label Detection işini başlatır.
4. Rekognition iş bitince sonucu SNS topic'e ("RekognitionTamamlandi") bildirir.
5. İkinci bir Lambda, SNS bildirimini dinler; sonucu çekip DynamoDB'ye yazar.

## Kullanılan Kaynaklar
- S3 Bucket: video-analiz-projesi-23291218
- DynamoDB Tablosu: VideoAnalizSonuclari
- SNS Topic ARN: arn:aws:sns:eu-central-1:271003694403:RekognitionTamamlandi
- Bölge (Region): eu-central-1

## Adım 1: SNS Topic Oluşturuldu
Rekognition'ın analiz tamamlandığında bildirim göndereceği topic oluşturuldu.

Komut:
    aws sns create-topic --name RekognitionTamamlandi --region eu-central-1

Çıktı (TopicArn):
    arn:aws:sns:eu-central-1:271003694403:RekognitionTamamlandi

## Adım 2: IAM Rolü (Rekognition -> SNS)
Rekognition'ın analiz tamamlandığında SNS topic'e bildirim gönderebilmesi için
bir IAM rolü oluşturuldu. Rol yalnızca ilgili SNS topic'e mesaj yayınlama
(sns:Publish) yetkisine sahiptir (en az yetki prensibi).

Trust policy (rekognition-trust-policy.json): Rolü rekognition.amazonaws.com
servisinin üstlenmesine izin verir.

Rol oluşturma:
    aws iam create-role --role-name RekognitionSNSRole \
      --assume-role-policy-document file://infrastructure/rekognition-trust-policy.json

Oluşan Rol ARN:
    arn:aws:iam::271003694403:role/RekognitionSNSRole

SNS yayınlama izni eklendi (rekognition-sns-policy.json):
    aws iam put-role-policy --role-name RekognitionSNSRole \
      --policy-name RekognitionSNSPublish \
      --policy-document file://infrastructure/rekognition-sns-policy.json

Not: video-project-user kullanıcısına başlangıçta IAM yetkisi verilmediği için
rol oluşturma sırasında AccessDenied hatası alındı. Çözüm olarak kullanıcıya
IAMFullAccess ve AWSLambda_FullAccess izinleri eklendi.

## Adım 3: Lambda Rolü (VideoLambdaRole)
Lambda fonksiyonunun çalışması için IAM rolü oluşturuldu. İzinler: CloudWatch
log yazma, S3'ten video okuma, Rekognition başlatma/sorgulama ve Rekognition'a
SNS rolünü geçirme (iam:PassRole).

    aws iam create-role --role-name VideoLambdaRole \
      --assume-role-policy-document file://infrastructure/lambda-trust-policy.json
    aws iam put-role-policy --role-name VideoLambdaRole \
      --policy-name VideoLambdaPermissions \
      --policy-document file://infrastructure/lambda-permissions-policy.json

## Adım 4: Birinci Lambda (VideoAnalizBaslat)
S3'e yüklenen videoyu algılayıp Rekognition analizini başlatan fonksiyon.
NotificationChannel ile sonuç SNS'e yönlendiriliyor (asenkron, beklemesiz).

    aws lambda create-function --function-name VideoAnalizBaslat \
      --runtime python3.12 --role arn:aws:iam::271003694403:role/VideoLambdaRole \
      --handler lambda_function.lambda_handler

      ## Adım 6: İkinci Lambda (VideoSonucKaydet)
Rekognition analizi bitince SNS'in tetiklediği fonksiyon. JobId ile sonuçları
çekip DynamoDB'ye yazar. VideoLambdaRole'a dynamodb:PutItem izni eklendi.

    aws lambda create-function --function-name VideoSonucKaydet \
      --runtime python3.12 --role arn:aws:iam::271003694403:role/VideoLambdaRole \
      --handler lambda_function.lambda_handler --timeout 60 \
      --zip-file fileb://save_results.zip --region eu-central-1

## Adım 7: SNS Aboneliği
İkinci Lambda, SNS topic'e abone edildi ve SNS'e çağırma izni verildi.

    aws lambda add-permission --function-name VideoSonucKaydet \
      --statement-id sns-invoke-izni --action lambda:InvokeFunction \
      --principal sns.amazonaws.com \
      --source-arn arn:aws:sns:eu-central-1:271003694403:RekognitionTamamlandi

    aws sns subscribe \
      --topic-arn arn:aws:sns:eu-central-1:271003694403:RekognitionTamamlandi \
      --protocol lambda \
      --notification-endpoint arn:aws:lambda:eu-central-1:271003694403:function:VideoSonucKaydet

## Uçtan Uca Test Sonucu
Video yüklendi -> birinci Lambda analizi başlattı -> Rekognition işledi ->
SNS tetiklendi -> ikinci Lambda 983 etiketi DynamoDB'ye yazdı. Tamamen
otomatik akış doğrulandı.

## Tam Mimari
S3 (uploads/) -> Lambda (VideoAnalizBaslat) -> Rekognition -> SNS
(RekognitionTamamlandi) -> Lambda (VideoSonucKaydet) -> DynamoDB
(VideoAnalizSonuclari)
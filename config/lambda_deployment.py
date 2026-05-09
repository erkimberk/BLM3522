"""
AWS Lambda Deployment Guide
Lambda fonksiyonunun AWS'ye yüklenmesi

Step 1: Lambda Execution Role oluştur
Step 2: Lambda fonksiyonunu oluştur ve deploy et
Step 3: IoT Core Rule Engine'ini konfigüre et
"""

# ============================================================
# ADIM 1: IAM Role Oluştur
# ============================================================

IAM_ROLE_CREATION = """
# 1. Trust policy (Lambda'nın bu role'ü kullanabileceğini tanımlar)
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# 2. Role oluştur
aws iam create-role \\
  --role-name iot-to-dynamodb-role \\
  --assume-role-policy-document file://trust-policy.json \\
  --region eu-central-1

# 3. DynamoDB yazma izni verecek policy oluştur
cat > dynamodb-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:eu-central-1:*:table/smart-city-sensor-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:eu-central-1:*:*"
    }
  ]
}
EOF

# 4. Policy'i role'e attach et
aws iam put-role-policy \\
  --role-name iot-to-dynamodb-role \\
  --policy-name DynamoDBAccess \\
  --policy-document file://dynamodb-policy.json \\
  --region eu-central-1
"""

# ============================================================
# ADIM 2: Lambda Fonksiyonunu Deploy Et
# ============================================================

LAMBDA_DEPLOYMENT = """
# 1. Lambda kodu için zip oluştur
# Windows:
cd src\\lambda
zip -r ..\\..\\lambda_function.zip iot_to_dynamodb.py

# 2. Lambda fonksiyonunu oluştur
aws lambda create-function \\
  --function-name iot-to-dynamodb \\
  --runtime python3.11 \\
  --role arn:aws:iam::ACCOUNT_ID:role/iot-to-dynamodb-role \\
  --handler iot_to_dynamodb.lambda_handler \\
  --zip-file fileb://lambda_function.zip \\
  --timeout 60 \\
  --memory-size 256 \\
  --environment Variables='{LOG_LEVEL=INFO}' \\
  --region eu-central-1

# 3. Fonksiyonu kontrol et
aws lambda get-function \\
  --function-name iot-to-dynamodb \\
  --region eu-central-1

# 4. Update etmek için (kodu değiştirdikten sonra):
aws lambda update-function-code \\
  --function-name iot-to-dynamodb \\
  --zip-file fileb://lambda_function.zip \\
  --region eu-central-1
"""

# ============================================================
# ADIM 3: Lambda Permission Ekle
# ============================================================

LAMBDA_PERMISSION = """
# IoT Core Rule Engine'in Lambda'yı invoke edebilmesi için
aws lambda add-permission \\
  --function-name iot-to-dynamodb \\
  --statement-id AllowIoTRuleInvoke \\
  --action lambda:InvokeFunction \\
  --principal iot.amazonaws.com \\
  --region eu-central-1

# Kontrol et
aws lambda get-policy \\
  --function-name iot-to-dynamodb \\
  --region eu-central-1
"""

# ============================================================
# ADIM 4: IoT Core Rule'u Oluştur ve Test Et
# ============================================================

IOT_RULE_SETUP = """
# 1. Rule oluştur
aws iot create-topic-rule \\
  --rule-name SmartCitySensorToDatabase \\
  --topic-rule-payload file://iot-rule-payload.json \\
  --region eu-central-1

# iot-rule-payload.json içeriği:
{
  "sql": "SELECT timestamp() as ts, clientId() as device, topic(2) as sensor_type, topic(3) as device_id, topic(4) as metric, * FROM 'smart-city/+/+/+'",
  "actions": [
    {
      "lambda": {
        "functionArn": "arn:aws:lambda:eu-central-1:ACCOUNT_ID:function:iot-to-dynamodb"
      }
    }
  ],
  "ruleDisabled": false
}

# 2. Rule'u test et (MQTT mesaj gönder)
# sensor_simulator.py çalıştır:
python sensor_simulator.py --duration 30 --interval 5

# 3. CloudWatch Logs'ta sonuçları kontrol et
aws logs tail /aws/lambda/iot-to-dynamodb --follow --region eu-central-1

# 4. DynamoDB'de verileri kontrol et
aws dynamodb scan \\
  --table-name smart-city-sensor-readings \\
  --limit 5 \\
  --region eu-central-1
"""

# ============================================================
# Deployment Checklist
# ============================================================

DEPLOYMENT_CHECKLIST = """
✅ Lambda Deployment Checklist

Phase 1: Pre-deployment
  [ ] AWS credentials konfigüre edildi
  [ ] AWS CLI yüklü ve çalışıyor
  [ ] DynamoDB tabloları oluşturuldu
  [ ] Lambda kod bittibildir

Phase 2: IAM Setup
  [ ] Trust policy oluşturuldu
  [ ] IAM Role oluşturuldu (iot-to-dynamodb-role)
  [ ] DynamoDB access policy attach edildi
  [ ] CloudWatch logs policy attach edildi

Phase 3: Lambda Creation
  [ ] Lambda kodu zip'lendi
  [ ] Lambda fonksiyonu oluşturuldu (iot-to-dynamodb)
  [ ] Runtime: Python 3.11 ✓
  [ ] Memory: 256 MB
  [ ] Timeout: 60 saniye
  [ ] Environment variables set

Phase 4: Permissions
  [ ] Lambda permission eklendi (IoT Core)
  [ ] Policy test edildi

Phase 5: IoT Rule Engine
  [ ] IoT Rule oluşturuldu (SmartCitySensorToDatabase)
  [ ] Rule SQL test edildi
  [ ] Lambda action attach edildi
  [ ] Rule enabled

Phase 6: End-to-End Test
  [ ] sensor_simulator.py çalıştırıldı
  [ ] MQTT mesajlar gönderildi
  [ ] Lambda logs kontrol edildi
  [ ] DynamoDB'de veriler görüldü
  [ ] Uyarılar (alerts) oluşturuldu

Phase 7: Monitoring
  [ ] CloudWatch dashboard oluşturuldu
  [ ] Lambda metric'leri monitore ediliyor
  [ ] DynamoDB metric'leri monitore ediliyor
  [ ] Error logs ayarlandı
"""

# ============================================================
# Troubleshooting
# ============================================================

TROUBLESHOOTING = """
🔧 Sorun Giderme

Sorun: "Lambda fonksiyonu not found"
→ Function ARN'inin doğru olduğundan emin ol (ACCOUNT_ID değiştir)

Sorun: "Permission denied" DynamoDB yazarken
→ IAM Role policy'yi kontrol et, DynamoDB table ARN'i doğru mu?

Sorun: "Rule not triggering"
→ IoT Rule'ın enabled olduğunu kontrol et
→ Topic pattern'inin doğru olduğundan emin ol
→ MQTT mesaj format'ını kontrol et

Sorun: "Lambda timeout"
→ Timeout değerini 60→120 saniyeye çıkar
→ DynamoDB yazma hızını kontrol et (on-demand mode)

Debug:
1. CloudWatch Logs'u kontrol et:
   aws logs tail /aws/lambda/iot-to-dynamodb --follow

2. Lambda test et (manual):
   aws lambda invoke \\
     --function-name iot-to-dynamodb \\
     --payload file://test-event.json \\
     response.json

3. DynamoDB'de verileri sorgula:
   aws dynamodb query \\
     --table-name smart-city-sensor-readings \\
     --key-condition-expression "pk = :pk" \\
     --expression-attribute-values '{":pk":{"S":"traffic_light#traffic-light-001"}}'
"""

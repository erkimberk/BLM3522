#!/bin/bash
# S3 bucket oluşturma
aws s3 mb s3://video-analiz-projesi-23291218 --region eu-central-1
aws s3api put-object --bucket video-analiz-projesi-23291218 --key uploads/
aws s3api put-object --bucket video-analiz-projesi-23291218 --key results/
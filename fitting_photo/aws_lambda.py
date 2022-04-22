from __future__ import print_function
import boto3
import os
import sys
import uuid
from PIL import Image
import PIL.Image

s3_client = boto3.client(
                's3',
                aws_access_key_id='AKIASTC6ZIOY27B5I2WO',
                aws_secret_access_key='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'
            )

def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        image.thumbnail(tuple(192, 256))
        image.save(resized_path)

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/media/image/my_photo/{}'.format(key)
        upload_path = '/media/image/my_photo/resized-{}'.format(key)

        s3_client.download_file(bucket, key, download_path)
        resize_image(download_path, upload_path)
        s3_client.upload_file(upload_path, '{}-resized'.format(bucket), key)
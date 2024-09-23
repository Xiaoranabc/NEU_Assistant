# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NeuCrawlerPipeline:
    def process_item(self, item, spider):
        return item
    

import os
import boto3
from scrapy.exporters import JsonLinesItemExporter
from botocore.exceptions import ClientError
import json

class S3ExportPipeline:
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region, s3_bucket):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region
        self.s3_bucket = s3_bucket
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            aws_access_key_id=crawler.settings.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=crawler.settings.get('AWS_SECRET_ACCESS_KEY'),
            aws_region=crawler.settings.get('AWS_REGION'),
            s3_bucket=crawler.settings.get('S3_BUCKET_NAME')
        )

    def open_spider(self, spider):
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )

    def process_item(self, item, spider):
        url = item['url']
        filename = url.replace('https://', '').replace('/', '_') + '.json'
        s3_path = f"{self.s3_bucket}/{filename}"
        self.client.put_object(Body=json.dumps(item), Bucket=self.s3_bucket, Key=s3_path)
        return item

    def close_spider(self, spider):
        pass
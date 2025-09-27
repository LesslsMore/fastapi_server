import logging
import os

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

from config.env import S3Config


class S3Service:
    def __init__(self):
        # 初始化 OBS 客户端
        self.s3_client: boto3.session.Session.client = boto3.client(
            's3',
            aws_access_key_id=S3Config.S3_AK,
            aws_secret_access_key=S3Config.S3_SK,
            endpoint_url=S3Config.S3_URL,
            # config=boto3.session.Config(signature_version='s3v4')  # 指定签名版本
        )
        self.s3_resource: boto3.session.Session.resource = boto3.resource(
            's3',
            aws_access_key_id=S3Config.S3_AK,
            aws_secret_access_key=S3Config.S3_SK,
            endpoint_url=S3Config.S3_URL,
        )
        self.bucket = S3Config.S3_BUCKET  # 替换为你的 bucket 名称
        self.static = S3Config.S3_STATIC

    def list_buckets(self):
        try:
            # 这里可以进行S3的操作，例如列出所有桶
            response = self.s3_client.list_buckets()
            logging.info(response)
        except NoCredentialsError:
            logging.info("No credentials provided.")
    @staticmethod
    def get_static_url(object_name, file_name=None):
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)
        return f"{S3Config.S3_STATIC}/{object_name}"

    def upload_file(self, file_name, extra_args={
        'ACL': 'public-read',  # 核心：设置访问控制列表
        'ContentType': 'image/jpeg'  # 建议同时设置正确的ContentType
    }, object_name=None):

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        try:
            response = self.s3_client.upload_file(file_name, self.bucket, object_name, extra_args)
            logging.info(response)
        except ClientError as e:
            logging.error(e)

    def upload_fileobj(self, file_name, object_name=None):
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        with open(file_name, "rb") as file:
            response = self.s3_client.upload_fileobj(file, self.bucket, object_name)
            logging.info(response)

    def put_acl(self, object_name, acl='public-read'):
        res = self.s3_resource.Object(self.bucket, object_name).Acl().put(ACL=acl)
        logging.info(res)

    def copy_from(self, object_name, content_type, acl='public-read'):

        res = self.s3_resource.Object(self.bucket, object_name).copy_from(CopySource={'Bucket': self.bucket,
                                                                                      'Key': object_name},
                                                                          MetadataDirective="REPLACE",
                                                                          ContentType=content_type,
                                                                          ACL=acl)

        logging.info(res)

    def copy_object(self, object_key, content_type):
        api_client = self.s3_resource.meta.client
        res = api_client.copy_object(Bucket=self.bucket,
                                     Key=object_key,
                                     ContentType=content_type,
                                     MetadataDirective="REPLACE",
                                     CopySource=self.bucket + "/" + object_key,
                                     ACL='public-read')
        logging.info(res)

    def generate_presigned_url(self, object_name, operation_name='get_object', expiration=3600):

        try:
            response = self.s3_client.generate_presigned_url(
                operation_name,
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expiration,
            )
            logging.info(response)
        except ClientError as e:
            logging.error(e)
            return None

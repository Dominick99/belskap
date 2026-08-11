from functools import lru_cache
from typing import BinaryIO

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from app.config import get_settings


@lru_cache
def get_s3_client() -> BaseClient:
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


def ensure_media_bucket() -> None:
    client = get_s3_client()
    bucket = get_settings().s3_bucket
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError:
        client.create_bucket(Bucket=bucket)


def upload_object(file: BinaryIO, key: str, content_type: str) -> None:
    ensure_media_bucket()
    get_s3_client().upload_fileobj(
        file,
        get_settings().s3_bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )


def get_object(key: str):
    return get_s3_client().get_object(Bucket=get_settings().s3_bucket, Key=key)


def delete_object(key: str) -> None:
    get_s3_client().delete_object(Bucket=get_settings().s3_bucket, Key=key)

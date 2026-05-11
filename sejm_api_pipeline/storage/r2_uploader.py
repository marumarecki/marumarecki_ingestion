import json
import os
import boto3
from botocore.client import Config


def upload_payload_to_r2(payload, bucket, key, account_id=None, access_key=None, secret_key=None):
    """Upload JSON payload directly to Cloudflare R2 bucket."""
    # Load from environment if not provided
    account_id = account_id or os.environ.get("R2_ACCOUNT_ID")
    access_key = access_key or os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = secret_key or os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket = bucket or os.environ.get("R2_BUCKET_NAME")

    if not all([account_id, access_key, secret_key, bucket]):
        raise ValueError("R2 credentials and bucket must be provided via parameters or environment variables")

    connection_url = f"https://{account_id}.r2.cloudflarestorage.com"

    s3_client = boto3.client(
        's3',
        endpoint_url=connection_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    # Convert payload to JSON string
    json_data = json.dumps(payload, indent=2, ensure_ascii=False)

    response = s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json_data,
        ContentType="application/json"
    )

    return response


def upload_file_to_r2(file_path, bucket, key, account_id=None, access_key=None, secret_key=None, content_type="application/json"):
    """Upload a file to Cloudflare R2 bucket."""
    # Load from environment if not provided
    account_id = account_id or os.environ.get("R2_ACCOUNT_ID")
    access_key = access_key or os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = secret_key or os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket = bucket or os.environ.get("R2_BUCKET_NAME")

    if not all([account_id, access_key, secret_key, bucket]):
        raise ValueError("R2 credentials and bucket must be provided via parameters or environment variables")

    connection_url = f"https://{account_id}.r2.cloudflarestorage.com"

    s3_client = boto3.client(
        's3',
        endpoint_url=connection_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    with open(file_path, 'rb') as f:
        response = s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=f,
            ContentType=content_type
        )

    return response
import os

AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
AWS_S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT_URL[8:]}" if AWS_S3_ENDPOINT_URL else ""
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "images"
AWS_DEFAULT_ACL = "public-read"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

CDN_ENDPOINT = os.getenv("CDN_ENDPOINT", "")

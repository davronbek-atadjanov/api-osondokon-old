# schema.py
import graphene
from graphene_file_upload.scalars import Upload
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from datetime import datetime
import magic  # For file type validation

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
]


class UploadImage(graphene.Mutation):
    class Arguments:
        image = Upload(required=True, description="Image file (max 10MB)")

    success = graphene.Boolean()
    image_url = graphene.String()
    errors = graphene.List(graphene.String)

    def validate_image(self, file):
        errors = []
        if file.size > MAX_IMAGE_SIZE:
            errors.append(
                f"Image too large. Max size is {MAX_IMAGE_SIZE/1024/1024}MB")

        file_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)

        if file_type not in ALLOWED_IMAGE_TYPES:
            errors.append(
                f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}")
        return errors

    @classmethod
    def mutate(cls, root, info, image, **kwargs):
        if image is None:
            return cls(success=False, errors=["No file provided"])

        upload = cls()
        validation_errors = upload.validate_image(image)
        if validation_errors:
            return cls(success=False, errors=validation_errors)

        try:
            session = boto3.session.Session()
            client = session.client('s3',
                                    region_name='nyc3',
                                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            original_name = image.name
            ext = original_name.split(
                '.')[-1].lower() if '.' in original_name else 'jpg'
            filename = f"{timestamp}.{ext}"

            if hasattr(settings, 'AWS_LOCATION'):
                filename = f"{settings.AWS_LOCATION}/{filename}"

            client.upload_fileobj(
                image,
                settings.AWS_STORAGE_BUCKET_NAME,
                filename,
                ExtraArgs={
                    'ACL': settings.AWS_DEFAULT_ACL,
                    'ContentType': image.content_type
                }
            )

            url = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{filename}"
            return cls(success=True, image_url=url, errors=[])

        except ClientError as e:
            return cls(success=False, errors=[str(e)])
        except Exception as e:
            return cls(success=False, errors=[str(e)])


class Mutation(graphene.ObjectType):
    upload_image = UploadImage.Field()

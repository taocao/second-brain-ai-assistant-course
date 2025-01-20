from pathlib import Path

from zenml import step

from second_brain.config import settings
from second_brain.infrastructure.aws.s3 import S3Client


@step
def upload_to_s3(
    folder_path: Path,
) -> None:
    s3_client = S3Client(
        bucket_name=settings.AWS_S3_BUCKET_NAME,
        aws_s3_no_sign_request=settings.AWS_S3_NOSIGN_REQUEST,
    )
    s3_client.upload_folder(local_path=folder_path)

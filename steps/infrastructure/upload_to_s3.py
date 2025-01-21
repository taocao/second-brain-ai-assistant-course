from pathlib import Path

from zenml import get_step_context, step

from second_brain.config import settings
from second_brain.infrastructure.aws.s3 import S3Client


@step
def upload_to_s3(
    folder_path: Path,
    s3_prefix: str = "",
) -> None:
    s3_client = S3Client(bucket_name=settings.AWS_S3_BUCKET_NAME)
    s3_client.upload_folder(local_path=folder_path, s3_prefix=s3_prefix)

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="uploaded_to_s3",
        metadata={
            "folder_path": str(folder_path),
            "s3_prefix": s3_prefix,
        },
    )

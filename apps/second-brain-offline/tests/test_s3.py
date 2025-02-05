from pathlib import Path

from second_brain_offline.infrastructure.aws.s3 import S3Client


def test_download_from_public_bucket() -> None:
    """
    Test downloading from a public S3 bucket using unsigned requests.

    This test uses the AWS COVID-19 data lake as an example public bucket.
    """

    # Setup
    bucket_name = "covid19-lake"  # This is a real public AWS bucket
    s3_client = S3Client(
        bucket_name=bucket_name,
        no_sign_request=True,  # This is key for public bucket access
    )

    # Test downloading a small known file
    s3_key = "query.html"  # This file exists in the covid19-lake bucket
    local_path = Path("test_download")

    try:
        # Download the file
        s3_client.download_file(s3_key, local_path)

        # Verify the file was downloaded
        downloaded_file = local_path / "query.html"
        assert downloaded_file.exists()
        assert downloaded_file.stat().st_size > 0

    finally:
        if local_path.exists():
            for file in local_path.glob("**/*"):
                if file.is_file():
                    file.unlink()
            local_path.rmdir()

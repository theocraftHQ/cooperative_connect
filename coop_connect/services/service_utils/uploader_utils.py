from aiobotocore.config import AioConfig
from aiobotocore.session import get_session

from theocraft_coop.root.settings import Settings

settings = Settings()

BUCKET_ACCESS_KEY = settings.aws_access_key
BUCKET_SECRET_KEY = settings.aws_secret_key
BUCKET = settings.aws_bucket
REGION_NAME = settings.aws_region_name

# asyncer non-blocking code in a sperate thread


async def file_uploader(file_name: str, data: any):
    session = get_session()

    async with session.create_client(
        "s3",
        config=AioConfig(s3={"addressing_style": "virtual"}),
        region_name=REGION_NAME,
        aws_access_key_id=BUCKET_ACCESS_KEY,
        aws_secret_access_key=BUCKET_SECRET_KEY,
    ) as client:
        try:
            await client.create_bucket(
                Bucket=BUCKET,
                CreateBucketConfiguration={"LocationConstraint": REGION_NAME},
            )
        except client.exceptions.BucketAlreadyOwnedByYou:
            pass
        except client.exceptions.BucketAlreadyExists:
            pass

        await client.put_object(
            Bucket=BUCKET,
            Key=file_name,
            Body=await data.read(),
            # ACL="public-read",  # Optional
        )

    return {"file_name": f"https://{BUCKET}.s3.{REGION_NAME}.amazonaws.com/{file_name}"}


async def destroy_file(file_name: str):
    session = get_session()

    async with session.create_client(
        "s3",
        config=AioConfig(s3={"addressing_style": "virtual"}),
        region_name=REGION_NAME,
        aws_access_key_id=BUCKET_ACCESS_KEY,
        aws_secret_access_key=BUCKET_SECRET_KEY,
    ) as client:
        await client.delete_object(Bucket=BUCKET, Key=file_name)
    return


async def get_presigned_url(file_name: str, expires_in: int = 72000):
    """Generate a presigned URL for temporary file access."""
    session = get_session()

    async with session.create_client(
        "s3",
        config=AioConfig(s3={"addressing_style": "virtual"}),
        region_name=REGION_NAME,
        aws_access_key_id=BUCKET_ACCESS_KEY,
        aws_secret_access_key=BUCKET_SECRET_KEY,
    ) as client:
        url = await client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": file_name},
            ExpiresIn=expires_in,  # time in seconds
        )
        return url

from minio import Minio
from app.core.config import Config


class MinIO:
    def __init__(self):
        endpoint = Config.MINIO_ENDPOINT
        access_key = Config.MINIO_ACCESS_KEY
        secret_key = Config.MINIO_SECRET_KEY

        self.bucket_name = "salary-management"
        self.profile_prefix = "profile/"

        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )

        found = self.client.bucket_exists("salary-management")
        if not found:
            self.client.make_bucket("salary-management")
            print("Bucket 'asiatrip' created successfully")
        else:
            print("Bucket 'asiatrip' already exists")

    async def get_presigned_url(self, employee_id):
        # object_name = self.client.get_b
        presigned_url = self.client.presigned_get_object(
            self.bucket_name, object_name, expires=60 * 60 * 24 * 7
        )

        return presigned_url

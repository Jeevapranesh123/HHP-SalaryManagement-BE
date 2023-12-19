from minio import Minio
from app.core.config import Config
from dotenv import load_dotenv
import os

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT")


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
            secure=True
            if ENVIRONMENT == "prod" or ENVIRONMENT == "staging"
            else False,
        )

        try:
            found = self.client.bucket_exists("salary-management")
            if not found:
                self.client.make_bucket("salary-management")
            else:
                pass

        except Exception as e:
            print(e)

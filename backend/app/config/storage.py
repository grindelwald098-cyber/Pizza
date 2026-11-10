from os import getenv


class StorageSettings:
    endpoint: str = getenv("MINIO_ENDPOINT", "localhost:4566")
    access_key: str = getenv("MINIO_ACCESS_KEY", "test")
    secret_key: str = getenv("MINIO_SECRET_KEY", "test")
    bucket: str = getenv("MINIO_BUCKET", "pizza-media")
    region: str = getenv("MINIO_REGION", "us-east-1")
    secure: bool = getenv("MINIO_SECURE", "false").lower() in {"1", "true", "yes"}
    public_url: str = getenv("MINIO_PUBLIC_URL", "http://localhost:4566")
    max_upload_bytes: int = int(getenv("MINIO_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))


storage_settings = StorageSettings()

from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
from uuid import uuid4

from minio import Minio
from minio.error import S3Error

from app.config.storage import storage_settings
from app.exceptions import BadRequestError, InternalError


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


@dataclass(frozen=True)
class UploadedObject:
    key: str
    url: str
    content_type: str
    size: int


class StorageService:
    def __init__(self) -> None:
        self._settings = storage_settings
        self._client = Minio(
            self._settings.endpoint,
            access_key=self._settings.access_key,
            secret_key=self._settings.secret_key,
            secure=self._settings.secure,
            region=self._settings.region,
        )

    def ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self._settings.bucket):
                self._client.make_bucket(self._settings.bucket)
        except S3Error as exc:
            raise InternalError(f"MinIO bucket error: {exc}") from exc

    def build_public_url(self, key: str) -> str:
        base = self._settings.public_url.rstrip("/")
        return f"{base}/{self._settings.bucket}/{key}"

    def upload(
        self,
        *,
        data: bytes,
        filename: str | None,
        content_type: str | None,
        folder: str = "uploads",
    ) -> UploadedObject:
        if not data:
            raise BadRequestError("Empty file")

        if len(data) > self._settings.max_upload_bytes:
            max_mb = self._settings.max_upload_bytes // (1024 * 1024)
            raise BadRequestError(f"File is too large. Max size is {max_mb} MB")

        normalized_type = (content_type or "").split(";")[0].strip().lower()
        if normalized_type not in ALLOWED_CONTENT_TYPES:
            allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
            raise BadRequestError(f"Unsupported content type. Allowed: {allowed}")

        extension = ALLOWED_CONTENT_TYPES[normalized_type]
        original_suffix = PurePosixPath(filename or "").suffix.lower()
        if original_suffix and original_suffix == extension:
            suffix = original_suffix
        else:
            suffix = extension

        safe_folder = self._normalize_folder(folder)
        key = f"{safe_folder}/{uuid4().hex}{suffix}"

        try:
            self.ensure_bucket()
            self._client.put_object(
                self._settings.bucket,
                key,
                BytesIO(data),
                length=len(data),
                content_type=normalized_type,
            )
        except S3Error as exc:
            raise InternalError(f"Failed to upload file to MinIO: {exc}") from exc

        return UploadedObject(
            key=key,
            url=self.build_public_url(key),
            content_type=normalized_type,
            size=len(data),
        )

    def delete(self, key: str) -> None:
        normalized_key = key.lstrip("/")
        if not normalized_key:
            raise BadRequestError("Object key is required")

        try:
            self._client.remove_object(self._settings.bucket, normalized_key)
        except S3Error as exc:
            raise InternalError(f"Failed to delete file from MinIO: {exc}") from exc

    @staticmethod
    def _normalize_folder(folder: str) -> str:
        cleaned = folder.strip().strip("/")
        if not cleaned:
            return "uploads"

        parts = [
            part
            for part in PurePosixPath(cleaned).parts
            if part not in {"", ".", ".."}
        ]
        if not parts:
            return "uploads"
        return "/".join(parts)


_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service

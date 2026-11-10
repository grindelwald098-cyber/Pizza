from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.schemas.media import MediaDeleteRequest, MediaUploadResponse
from app.services.storage import StorageService, get_storage_service

router = APIRouter(
    prefix="/media",
    tags=["Media"],
)


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    folder: str = Form(default="uploads"),
    storage: StorageService = Depends(get_storage_service),
) -> MediaUploadResponse:
    payload = await file.read()
    uploaded = storage.upload(
        data=payload,
        filename=file.filename,
        content_type=file.content_type,
        folder=folder,
    )
    return MediaUploadResponse(
        key=uploaded.key,
        url=uploaded.url,
        content_type=uploaded.content_type,
        size=uploaded.size,
    )


@router.delete("/")
async def delete_media(
    data: MediaDeleteRequest,
    storage: StorageService = Depends(get_storage_service),
) -> dict[str, str]:
    storage.delete(data.key)
    return {"status": "deleted", "key": data.key}

from pydantic import BaseModel, Field


class MediaUploadResponse(BaseModel):
    key: str
    url: str
    content_type: str
    size: int = Field(ge=0)


class MediaDeleteRequest(BaseModel):
    key: str

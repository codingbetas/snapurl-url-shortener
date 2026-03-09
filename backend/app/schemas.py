from pydantic import BaseModel, HttpUrl
from typing import Optional

class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_code: Optional[str] = None
    expires_in_days: Optional[int] = None


class URLResponse(BaseModel):
    short_code: str
    short_url: str
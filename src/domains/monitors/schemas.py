from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field

class CreateMonitorDTO(BaseModel):
    #Hа место Name поменять на то что будет у вас отображатся в swagger
    name: str = Field(..., min_length=1, max_length=100, example="Name")
    url: HttpUrl = Field(..., example="https://google.com")
    interval_seconds: int = Field(default=60, ge=10, le=3600)

class MonitorResponseDTO(BaseModel):
    id: UUID
    name: str
    url: str
    interval_seconds: int
    is_active: bool
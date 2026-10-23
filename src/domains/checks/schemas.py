from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CheckResultResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    site_id: UUID
    status_code: int | None = None
    response_time_ms: float | None = None
    is_successful: bool
    error_message: str | None = None
    checked_at: datetime
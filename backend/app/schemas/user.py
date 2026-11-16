import uuid
from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    created_at: datetime

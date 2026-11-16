from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    created_at: datetime
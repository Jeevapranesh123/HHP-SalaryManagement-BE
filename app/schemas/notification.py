from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import List


class NotificationBase(BaseModel):
    id: str = str(uuid.uuid4()).replace("-", "")
    title: str
    description: str
    payload: dict
    notifier: List[str] = []
    priority: str = "low"
    source: str
    status: str = "pending"
    created_at: datetime = datetime.now()

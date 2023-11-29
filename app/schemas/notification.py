from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import List
from enum import Enum
from typing import Optional


class NotificationPayload(BaseModel):
    url: str


class NotificationType(str, Enum):
    EMPLOYEE = "employee"
    LEAVE = "leave"
    ATTENDANCE = "attendance"
    SALARY = "salary"
    REIMBURSEMENT = "reimbursement"
    EXPENSE = "expense"
    RECRUITMENT = "recruitment"
    TASK = "task"
    ANNOUNCEMENT = "announcement"
    DOCUMENT = "document"
    OTHER = "other"


class UIAction(str, Enum):
    READ = "read"
    ACTION = "action"


class NotificationMeta(BaseModel):
    to: List[str]
    cc: Optional[List[str]] = None
    from_: str


class NotificationBase(BaseModel):
    id: str = str(uuid.uuid4()).replace("-", "")
    title: str
    description: str
    payload: dict
    ui_action: UIAction = UIAction.READ
    type: NotificationType
    priority: str = "low"
    source: str
    status: str = "pending"
    target: str
    created_at: datetime = datetime.now()
    meta: NotificationMeta


class SendNotification(BaseModel):
    notifier: List[NotificationBase]

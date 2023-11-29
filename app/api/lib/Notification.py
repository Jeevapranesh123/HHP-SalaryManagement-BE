from app.database import AsyncIOMotorClient
from fastapi import HTTPException
from app.core.config import Config
from app.api.lib.RabbitMQ import RabbitMQ

from app.schemas.notification import NotificationBase, SendNotification


MONGO_DATABASE = Config.MONGO_DATABASE
NOTIFICATION_COLLECTION = Config.NOTIFICATION_COLLECTION

exchange_meta = {
    "HR": {
        "exchange_name": "hr_notification",
    },
    "MD": {
        "exchange_name": "md_notification",
    },
}


class Notification(object):
    def __init__(self, sender_id, source, mongo_client: AsyncIOMotorClient):
        self.sender_id = sender_id
        self.source = source
        self.mongo_client = mongo_client
        self.mq = RabbitMQ()

    async def create_notification(self, notification: NotificationBase):
        notification_in_db = notification.model_dump()
        if await self.mongo_client[MONGO_DATABASE][NOTIFICATION_COLLECTION].insert_one(
            notification_in_db
        ):
            return notification_in_db

    async def get_all_notifications(self):
        return (
            await self.mongo_client[MONGO_DATABASE][NOTIFICATION_COLLECTION]
            .find({}, {"_id": 0})
            .to_list(None)
        )

    async def get_notification(self, notification_id):
        notification = await self.mongo_client[MONGO_DATABASE][
            NOTIFICATION_COLLECTION
        ].find_one({"id": notification_id}, {"_id": 0})
        if notification:
            return notification
        else:
            raise HTTPException(status_code=404, detail="Notification not found")

    async def update_notification(
        self, notification_id, notification: NotificationBase
    ):
        if await self.mongo_client[MONGO_DATABASE][NOTIFICATION_COLLECTION].update_one(
            {"id": notification_id}, {"$set": notification.model_dump()}
        ):
            return notification
        else:
            raise HTTPException(status_code=404, detail="Notification not found")

    async def delete_notification(self, notification_id):
        if await self.mongo_client[MONGO_DATABASE][NOTIFICATION_COLLECTION].delete_one(
            {"id": notification_id}
        ):
            return True
        else:
            raise HTTPException(status_code=404, detail="Notification not found")

    async def notify():
        pass

    async def send_notification(self, send: SendNotification):
        recipients = send.notifier

        for recipient in recipients:
            await self.create_notification(recipient)
            recipient.title = recipient.description

            print("recipient", recipient)

            self.mq.publish(
                exchange="employee_notification",
                routing_key=recipient.target,
                data=recipient.model_dump(),
            )

        return True

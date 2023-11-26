import json
import logging
from datetime import datetime

import pika
from bson import ObjectId

from app.core.config import Config

logger = logging.getLogger(__name__)


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles ObjectId and datetime objects"""

    def default(self, obj):
        if isinstance(obj, ObjectId):
            # Convert ObjectId to string
            return str(obj)
        elif isinstance(obj, datetime):
            # Format datetime objects as strings
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


# FIXME: Define the exchange and routing_key in a config file


class RabbitMQ:
    def __init__(self, **kwargs) -> None:
        self.credentials = pika.PlainCredentials(
            Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST, credentials=self.credentials
            )
        )

        queue = kwargs.get("queue", None)
        exchange = kwargs.get("exchange", None)
        binding_key = kwargs.get("binding_key", None)

        self.channel = self.connection.channel()

        if queue:
            self.ensure_queue(queue)

        if exchange:
            self.ensure_exchange(exchange)

        if queue and exchange and binding_key:
            self.bind_queue(queue, exchange, binding_key)

    def reconnect_channel(self):
        # Attempt to reopen the connection if closed
        if self.connection.is_closed:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST, credentials=self.credentials
                )
            )

        # Re-establish the channel
        self.channel = self.connection.channel()

    def ensure_queue(self, queue, queue_type="durable"):
        if queue_type == "durable":
            # Declare a durable queue
            return self.channel.queue_declare(queue=queue, durable=True)
        elif queue_type == "transient":
            # Declare a transient queue
            return self.channel.queue_declare(queue=queue, durable=False)
        elif queue_type == "exclusive":
            # Declare an exclusive queue
            return self.channel.queue_declare(queue=queue, exclusive=True)
        else:
            # Handle other types or raise an error
            raise ValueError("Unsupported queue type")

    def delete_queue(self, queue):
        return self.channel.queue_delete(queue=queue)

    def ensure_exchange(self, exchange, type="topic"):
        return self.channel.exchange_declare(
            exchange=exchange, exchange_type=type, durable=True
        )

    def bind_queue(self, queue, exchange, binding_key):
        return self.channel.queue_bind(
            exchange=exchange, queue=queue, routing_key=binding_key
        )

    def publish(self, data, exchange, routing_key):
        try:
            # Check if the channel is open
            if self.channel.is_closed:
                # Handle channel reconnection
                logger.warning("Channel is closed. Reconnecting...")
                self.reconnect_channel()

            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(data, cls=CustomEncoder),
                properties=pika.BasicProperties(
                    delivery_mode=2
                ),  # make message persistent
            )
        except Exception as e:
            logger.error("Error while publishing message to RabbitMQ: {}".format(e))

    def consume(self, queue, callback):
        try:
            # Check if the channel is open
            if self.channel.is_closed:
                # Handle channel reconnection
                logger.warning("Channel is closed. Reconnecting...")
                self.reconnect_channel()

            self.channel.basic_consume(queue=queue, on_message_callback=callback)
            self.channel.start_consuming()
        except Exception as e:
            logger.error("Error while consuming message from RabbitMQ: {}".format(e))

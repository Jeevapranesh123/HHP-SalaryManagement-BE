# socketio_app.py
import socketio
import pprint
import asyncio
import redis


redis_client = redis.Redis(host="localhost", port=6379)  # Adjust parameters as needed


from socketio_manager.auth import validate_connection

from app.api.lib.RabbitMQ import RabbitMQ
from app.schemas.notification import NotificationBase
from app.api.lib.Notification import Notification

rabbitmq_instances = {}

# Create a Socket.IO server instance
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Wrap with ASGI application
app = socketio.ASGIApp(sio)


async def async_consume(mq_instance, queue, sio, sid):
    loop = asyncio.get_running_loop()
    # Using to_thread to run the synchronous consume method in a separate thread
    # Adjust the arguments as per your consume method's signature
    await loop.run_in_executor(None, mq_instance.consume, queue, sio, sid)


async def ack(mq_instance, delivery_tag):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, mq_instance.ack_message, delivery_tag)


# Event handler for new connections
@sio.event
async def connect(sid, environ):
    print("Connected", sid)

    # Validate the connection
    payload = await validate_connection(sid, environ, sio)

    if not payload:
        return await sio.disconnect(sid)

    loop = asyncio.get_running_loop()

    queue_name = "notifications_employee_{}".format(payload["uuid"])
    exchange_name = "employee_notification"
    binding_key = payload["employee_id"]

    mq = RabbitMQ(
        queue_name=queue_name,
        exchange_name=exchange_name,
        binding_key=binding_key,
        loop=loop,
    )

    rabbitmq_instances[sid] = mq

    sio.start_background_task(async_consume, mq, queue_name, sio, sid)


@sio.event
async def disconnect(sid):
    mq = rabbitmq_instances.get(sid)

    if mq:
        mq.should_stop.set()
        print(mq.should_stop.is_set())

    print("Disconnected", sid)


@sio.event
async def notification(sid, data):
    print("Received notification", data)


# @sio.event
# async def mark_as_read(sid, data):
#     """
#     Handle 'mark_as_read' event from frontend.
#     'data' should contain necessary information like message ID or delivery tag.
#     """
#     print(f"Received mark_as_read from {sid}: {data}")
#     delivery_tag = data

#     mq = rabbitmq_instances.get(sid)

#     if mq:
#         await ack(mq, delivery_tag)

import sys

sys.dont_write_bytecode = True

import socketio
import asyncio

from socketio_manager.auth import validate_connection
from socketio_manager.utils import async_consume

from app.api.lib.RabbitMQ import RabbitMQ

rabbitmq_instances = {}

# Create a Socket.IO server instance
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Wrap with ASGI application
app = socketio.ASGIApp(sio)


# Event handler for new connections
@sio.event
async def connect(sid, environ):
    payload = await validate_connection(sid, environ, sio)

    if not payload:
        return await sio.disconnect(sid)

    loop = asyncio.get_running_loop()

    queue_name = "notifications_employee_{}".format(payload["uuid"])
    exchange_name = "employee_notification"
    binding_key = payload["employee_id"]

    print(
        "Client connected with sid: {}, Employee ID: {}, queue_name: {}".format(
            sid, payload["employee_id"], queue_name
        )
    )

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

    print("Disconnected", sid)


@sio.event
async def mark_as_read(sid, data):
    print("Received notification", data)


# async def mark_as_read_worker(sid, data):
#     notification_id = data["id"]
#     delivery_tag = data["delivery_tag"]

#     should_stop = False

#     mq = RabbitMQ()

#     def callback(ch, method, properties, body):
#         print(delivery_tag)
#         print(" [x] Received %r" % body)
#         if 1 == 2:
#             should_stop = True
#         # ch.basic_ack(delivery_tag=method.delivery_tag)

#     mq.channel.basic_consume(
#         queue="notifications_employee_8ceaf1d97507430199549f51b742ca4c",
#         on_message_callback=callback,
#         auto_ack=False,
#     )

#     while not should_stop:
#         print(" [x] Waiting for messages. To exit press CTRL+C")
#         mq.connection.process_data_events(time_limit=1)


# @sio.event
# async def mark_as_read(sid, data):
#     """
#     Handle 'mark_as_read' event from frontend.
#     'data' should contain necessary information like message ID or delivery tag.
#     """
#     print(f"Received mark_as_read from {sid}: {data}\n")

#     await mark_as_read_worker(sid, data)

# mq = rabbitmq_instances.get(sid)

# if mq:
#     try:
#         if mq.channel.is_closed:
#             mq.reconnect_channel()
#         print(mq.channel.basic_ack(delivery_tag=data))
#     except Exception as e:
#         mq.reconnect_channel()

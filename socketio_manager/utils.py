import sys

sys.dont_write_bytecode = True

import asyncio


async def async_consume(mq_instance, queue, sio, sid):
    loop = asyncio.get_running_loop()
    # Using to_thread to run the synchronous consume method in a separate thread
    # Adjust the arguments as per your consume method's signature
    await loop.run_in_executor(None, mq_instance.consume, queue, sio, sid)


async def ack(mq_instance, delivery_tag):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, mq_instance.ack_message, delivery_tag)

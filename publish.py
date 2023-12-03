import pika
import json

# RabbitMQ server connection parameters
credentials = pika.PlainCredentials("root", "zuvaLabs")

# Establish a connection with RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", credentials=credentials)
)
channel = connection.channel()


queue_name = "notifications_employee_30eee43cccec4290af2dcf4453f245f2"
# Declare a queue (creates it if it doesn't already exist)
channel.queue_declare(queue=queue_name, durable=True)

# Your message
message = "Hello World!"

body = {
    "title": "Your loan request have been approved",
    "payload": {"url": "/loan/history"},
    "ui_action": "action",
}

body = json.dumps(body)

# Publish the message to the queue
channel.basic_publish(
    exchange="",
    routing_key=queue_name,
    body=str(body),
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
    ),
)


print(f" [x] Sent '{body}'")

# Close the connection
connection.close()

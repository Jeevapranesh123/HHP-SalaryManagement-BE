import pika
import json

# RabbitMQ server connection parameters
credentials = pika.PlainCredentials("root", "zuvaLabs")

# Establish a connection with RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="lab.zuvatech.com", credentials=credentials)
)
channel = connection.channel()


queue_name = "notifications_employee_c94aa1eb90524966b6a805d8e16eb385"
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

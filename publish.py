import pika

# RabbitMQ server connection parameters
credentials = pika.PlainCredentials("root", "zuvaLabs")

# Establish a connection with RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="lab.zuvatech.com", credentials=credentials)
)
channel = connection.channel()


queue_name = "notifications_employee_a349d57692ca4a4f83b6496ceacf9eba"
# Declare a queue (creates it if it doesn't already exist)
channel.queue_declare(queue=queue_name, durable=True)

# Your message
message = "Hello World!"

body = {
    "message": "Hello World!",
}

# Publish the message to the queue
channel.basic_publish(
    exchange="",
    routing_key="notifications_employee_a349d57692ca4a4f83b6496ceacf9eba",
    body=str(body),
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
    ),
)


print(f" [x] Sent '{body}'")

# Close the connection
connection.close()

import requests
import pika

# RabbitMQ connection parameters
rabbitmq_host = "localhost"
rabbitmq_port = 5672
rabbitmq_user = "root"
rabbitmq_pass = "zuvaLabs"

# Management API URL (Change if needed)
management_api_url = f"http://{rabbitmq_host}:15672/api/queues"

# Establish connection
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbitmq_host, port=rabbitmq_port, credentials=credentials
    )
)
channel = connection.channel()

# Fetching queue names using RabbitMQ Management API
response = requests.get(management_api_url, auth=(rabbitmq_user, rabbitmq_pass))
queues = response.json()

# Delete all queues
for queue in queues:
    queue_name = queue["name"]
    channel.queue_delete(queue=queue_name)
    print(f"Deleted queue: {queue_name}")

# Close connection
connection.close()

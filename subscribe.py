import pika
import sys
import pymongo
import pprint
import json

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["hhp-esm"]
collection = db["users"]


def callback(ch, method, properties, body):
    print(f"\nReceived Message:")
    pprint.pprint(json.loads(body))


# Check if the queue name is passed as an argument
if len(sys.argv) < 2:
    print("Usage: python script_name.py [queue_name]")
    sys.exit(1)

employee_id = sys.argv[1]

user = collection.find_one({"employee_id": employee_id})

queue_name = "notifications_employee_{}".format(user["uuid"])


credentials = pika.PlainCredentials("root", "zuvaLabs")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        credentials=credentials,
    )
)


channel = connection.channel()

# Specify the queue to listen to
channel.queue_declare(queue=queue_name, durable=True)

# Tell RabbitMQ that this callback function should receive messages from the specified queue
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Waiting for messages. To exit press CTRL+C")
try:
    # Start consuming messages
    channel.start_consuming()
except KeyboardInterrupt:
    # Close the connection gracefully on interruption
    channel.stop_consuming()

connection.close()

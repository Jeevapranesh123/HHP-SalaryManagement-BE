import socketio
import pprint
import time
import json

sio = socketio.Client()


@sio.event
def connect():
    print("Connected to the server")


@sio.event
def disconnect():
    print("Disconnected from the server")
    sio.disconnect()


@sio.event
def notification(data):
    print("New notification:", data)
    time.sleep(5)
    # sio.emit("mark_as_read", data["data"]["delivery_tag"])


def mark_message_as_read(message_id):
    sio.emit("mark_as_read", message_id)


if __name__ == "__main__":
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiMzBlZWU0M2NjY2VjNDI5MGFmMmRjZjQ0NTNmMjQ1ZjIiLCJlbWFpbCI6ImVtbWFqb2huc29uQHRlY2hjb3JwLmNvbSIsImJyYW5jaCI6ImhlYWRfb2ZmaWNlIiwiY2hhbmdlZF9wYXNzd29yZF9hdF9maXJzdF9sb2dpbiI6dHJ1ZSwiZW1wbG95ZWVfaWQiOiJNRDQwMDQiLCJwcmltYXJ5X3JvbGUiOiJNRCIsInNlY29uZGFyeV9yb2xlcyI6WyJlbXBsb3llZSJdLCJqdGkiOiIxOTYzOTViN2IyYzc0M2Y1OWViOWIzMjE4YTI4N2U5YyIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3MDE3MDg5MTN9.j3w7UFTzZtEnpX_QwqJ-KiRUK7a4uNAvBX7NrEKrS1o"
    sio.connect(
        "http://localhost:9003", headers={"Authorization": f"Bearer {jwt_token}"}
    )
    try:
        sio.wait()
    except KeyboardInterrupt:
        sio.disconnect()

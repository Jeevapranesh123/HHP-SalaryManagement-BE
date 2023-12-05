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
    print(data)
    new_data = {
        "id": data["data"],
        "delivery_tag": data["data"]["payload"]["delivery_tag"],
    }
    sio.emit("mark_as_read", new_data)


def mark_message_as_read(message_id):
    sio.emit("mark_as_read", message_id)


if __name__ == "__main__":
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiOGNlYWYxZDk3NTA3NDMwMTk5NTQ5ZjUxYjc0MmNhNGMiLCJlbWFpbCI6ImVtbWFqb2huc29uQHRlY2hjb3JwLmNvbSIsImJyYW5jaCI6ImhlYWRfb2ZmaWNlIiwiY2hhbmdlZF9wYXNzd29yZF9hdF9maXJzdF9sb2dpbiI6dHJ1ZSwiZW1wbG95ZWVfaWQiOiJNRDQwMDQiLCJwcmltYXJ5X3JvbGUiOiJNRCIsInNlY29uZGFyeV9yb2xlcyI6WyJlbXBsb3llZSJdLCJqdGkiOiI2NThhYzJkZTc3ZWU0Mjk0YmM0Yzg0YmQ4OGIzYWM1MSIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3MDE3MjEyMjR9.e2NkSRXcSuak_MkU5LuVLGQ9J2F5vXhKttiWgS1mdXY"
    sio.connect(
        "http://localhost:9003", headers={"Authorization": f"Bearer {jwt_token}"}
    )
    try:
        sio.wait()
    except KeyboardInterrupt:
        sio.disconnect()

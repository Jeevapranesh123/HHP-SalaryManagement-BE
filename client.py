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
    jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiZjNlYTZmODM1YjMyNGZkMmFiMzdhODRmZDgyZWRmMmIiLCJlbWFpbCI6ImVtbWFqb2huc29uQHRlY2hjb3JwLmNvbSIsImNoYW5nZWRfcGFzc3dvcmRfYXRfZmlyc3RfbG9naW4iOnRydWUsImVtcGxveWVlX2lkIjoiTUQ0MDA0IiwicHJpbWFyeV9yb2xlIjoiTUQiLCJzZWNvbmRhcnlfcm9sZXMiOlsiZW1wbG95ZWUiXSwianRpIjoiM2Y0YTFjZTA4OTAzNDE1YTgxMzc0OTYxZjdmYWNhMGEiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzAxMTA5Mjk2fQ.72_ETdgDhscTE2Kn6VGsR6BOyxsR3tWm3n1uqeCkEWg"
    sio.connect(
        "http://lab.zuvatech.com:9000", headers={"Authorization": f"Bearer {jwt_token}"}
    )
    try:
        sio.wait()
    except KeyboardInterrupt:
        sio.disconnect()

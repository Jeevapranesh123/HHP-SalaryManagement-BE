import socketio

sio = socketio.Client()


@sio.event
def connect():
    print("Connected to the server")


@sio.event
def disconnect():
    print("Disconnected from the server")


@sio.event
def notification(data):
    print("New notification:", data)


if __name__ == "__main__":
    sio.connect("http://localhost:8000/")
    try:
        sio.wait()
    except KeyboardInterrupt:
        sio.disconnect()

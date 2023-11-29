import jwt
from datetime import datetime
from jwt.exceptions import InvalidTokenError

from app.core.config import Config

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM


async def verify_login_token_for_socketio(token: str) -> (bool, str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            return False, "Invalid authentication type"

        if payload.get("exp") < int(datetime.utcnow().timestamp()):
            return False, "Token has expired"

        # FIXME: Check if a user with the uuid exists in the database

        return True, payload  # Return True and the payload or specific user data

    except InvalidTokenError as e:
        print(e)
        return False, "Could not validate credentials"  # Invalid token


async def validate_connection(sid, environ, sio):
    token = environ.get("HTTP_AUTHORIZATION")

    if token:
        try:
            token = token.split(" ")[1]  # Assuming 'Bearer TOKEN' format
            success, response = await verify_login_token_for_socketio(token)
            if success:
                # print("Connected", sid, "User data:", response)
                return response
            else:
                print("Authentication failed for", sid, "Reason:", response)
                await sio.emit("auth_error", {"error": response}, room=sid)
                await sio.disconnect(sid)

        except Exception as e:
            print("Error while verifying token for", sid, "Reason:", e)
            await sio.emit("auth_error", {"error": "Invalid token"}, room=sid)
            await sio.disconnect(sid)
    else:
        print("No token provided, disconnecting", sid)
        await sio.disconnect(sid)

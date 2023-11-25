from fastapi import HTTPException, Depends
from functools import wraps
from typing import List


def role_required(required_roles: List[str]):
    """
    Decorator to restrict access based on user roles.
    """

    def role_checker(func):
        @wraps(func)  # This line is added to copy metadata from func to wrapper
        async def wrapper(*args, **kwargs):
            # Extract the payload from the kwargs
            payload = kwargs.get("payload")

            # Check if the user's role matches any of the required roles
            user_roles = {payload.get("primary_role")} | set(
                payload.get("secondary_roles", [])
            )
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(status_code=403, detail="Not enough permissions")

            return await func(*args, **kwargs)

        return wrapper

    return role_checker

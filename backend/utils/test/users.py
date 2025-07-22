"""User utils for test fixtures."""
from typing import Any

from starlette.testclient import TestClient


def get_access_token(username: str, password: str, client: TestClient) -> Any:
    """Login and get access token.

    Arguments:
        username -- username
        password -- password
        client -- starlette test client

    Returns:
        return a access token
    """
    login = {
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    response = client.post("/token", data=login)
    json_response = response.json()
    return json_response.get("access_token")

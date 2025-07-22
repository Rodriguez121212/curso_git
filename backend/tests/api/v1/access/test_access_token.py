"""Unit test for users functionalities."""
from http import HTTPStatus
from typing import Any, Dict, List

from starlette.testclient import TestClient


def test_incorrect_username(mock_client: TestClient) -> None:
    """Test incorrect username."""
    login = {
        "username": "username_no_existente",
        "password": "no_importa_password",
        "grant_type": "password",
    }
    expected_status_code = HTTPStatus.UNAUTHORIZED
    expected_error = {
        "detail": "incorrect username or password",
        "status": expected_status_code,
    }
    response = mock_client.post("/token", data=login)
    assert response.status_code == expected_status_code
    json_response = response.json()
    assert "access_token" not in json_response
    assert json_response == expected_error


def test_incorrect_password(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]]
) -> None:
    """Test incorrect passsword."""
    user = mock_usuarios[0]
    login = {
        "username": user["username"],
        "password": "incorrect_password",
        "grant_type": "password",
    }
    expected_status_code = HTTPStatus.UNAUTHORIZED
    expected_error = {
        "detail": "incorrect username or password",
        "status": expected_status_code,
    }
    response = mock_client.post("/token", data=login)
    assert response.status_code == expected_status_code
    json_response = response.json()
    assert "access_token" not in json_response
    assert json_response == expected_error


def test_token_usuario_vacio(
    mock_client: TestClient, mock_empty_username_token: str
) -> None:
    """Test token con usuario vacio."""
    response = mock_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {mock_empty_username_token}"},
    )
    expected_status_code = HTTPStatus.UNAUTHORIZED
    expeced_error = {
        "detail": "Could not validate credentials",
        "status": expected_status_code,
    }
    assert response.status_code == expected_status_code
    json_response = response.json()
    assert "access_token" not in json_response
    assert json_response == expeced_error


def test_token_invalido(mock_client: TestClient, mock_invalid_token: str) -> None:
    """Test token invalido."""
    response = mock_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {mock_invalid_token}"},
    )
    expected_status_code = HTTPStatus.UNAUTHORIZED
    expeced_error = {
        "detail": "Could not validate credentials",
        "status": expected_status_code,
    }
    assert response.status_code == expected_status_code
    json_response = response.json()
    assert "access_token" not in json_response
    assert json_response == expeced_error


def test_token_usuario_no_existe(
    mock_client: TestClient, mock_username_doesnt_exist_token: str
) -> None:
    """Test token usuario de usuario no existente."""
    response = mock_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {mock_username_doesnt_exist_token}"},
    )
    expected_status_code = HTTPStatus.UNAUTHORIZED
    expeced_error = {
        "detail": "Could not validate credentials",
        "status": expected_status_code,
    }
    assert response.status_code == expected_status_code
    json_response = response.json()
    assert "access_token" not in json_response
    assert json_response == expeced_error


def test_disabled_user(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], secret_password: str
) -> None:
    """Test token de usuario desabilitado."""
    user = mock_usuarios[1]
    login = {
        "username": user["username"],
        "password": secret_password,
        "grant_type": "password",
    }

    response = mock_client.post("/token", data=login)
    assert response.status_code == HTTPStatus.OK
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["access_token"]
    access_token = json_response["access_token"]
    assert json_response == {"access_token": access_token, "token_type": "bearer"}

    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {"detail": "inactive user", "status": expected_status_code}
    response = mock_client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == expected_status_code
    json_response = response.json()
    assert "access_token" not in json_response
    assert json_response == expected_error


def test_successful_login(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_usuarios: List[Dict[str, Any]],
    secret_password: str,
) -> None:
    """Test successful login."""
    user = mock_usuarios[5]  # user from mock_authorized_user_access_token
    login = {
        "username": user["username"],
        "password": secret_password,
        "grant_type": "password",
    }

    response = mock_client.post("/token", data=login)
    assert response.status_code == HTTPStatus.OK
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["access_token"]
    access_token = json_response["access_token"]
    assert json_response == {"access_token": access_token, "token_type": "bearer"}

    response = mock_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    json_response = response.json()
    assert "id" in json_response
    assert json_response["id"]
    id = json_response["id"]
    assert json_response == {
        "id": id,
        "username": user["username"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "disabled": False,
    }

"""Unit test for users functionalities."""
from http import HTTPStatus
from typing import Any, Dict, List
from uuid import UUID

from starlette.testclient import TestClient

from utils.test.common import is_valid_uuid
from utils.test.fixtures import key_with_str_value
from utils.test.users import get_access_token


def test_get_user_actual(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test get user actual with permission."""
    expected_results = mock_usuarios[5].copy()
    expected_results["id"] = str(expected_results["id"])
    expected_results.pop("hashed_password")
    response = mock_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_get_user(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test get user by id with permission."""
    expected_results = mock_usuarios[0].copy()
    expected_results.pop("hashed_password")
    user_id = expected_results["id"] = str(expected_results["id"])
    response = mock_client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_user_not_found(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test user not found with permission."""
    user_id = str(random_uuid)
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"user {user_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_user_without_permission(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], mock_access_token: str
) -> None:
    """Test get user by id without_permission."""
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    user_id = str(mock_usuarios[0]["id"])
    response = mock_client.get(
        f"/users/{user_id}", headers={"Authorization": f"Bearer {mock_access_token}"}
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_user_when_user_not_login(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]]
) -> None:
    """Test get user by id when user isn't logged in."""
    user_id = str(mock_usuarios[0]["id"])
    response = mock_client.get(f"/users/{user_id}")
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_create_user_without_permission(
    mock_client: TestClient, mock_access_token: str
) -> None:
    """Test create user with permission without permission."""
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    user = {
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "email": "string@gmail.com",
        "password": "string",
    }
    response = mock_client.post(
        "/users",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        json=user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_create_user(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test create user with permission."""
    user = {
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "email": "string@gmail.com",
        "password": "string",
    }
    response = mock_client.post(
        "/users",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=user,
    )
    assert response.status_code == HTTPStatus.CREATED
    result = response.json()
    assert type(result) == dict
    assert set(result.keys()) == {"detail", "id"}
    assert result["detail"] == "user created successfully"
    user_id = result["id"]
    assert is_valid_uuid(user_id)

    expected_results = {
        "id": user_id,
        "username": user["username"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "disabled": False,
    }
    response = mock_client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.json() == expected_results


def test_repeat_username(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test create user with username already in use with permission."""
    user = {
        "username": mock_usuarios[0]["username"],
        "first_name": "string",
        "last_name": "string",
        "email": "string@email.com",
        "password": "string",
    }
    expected_status_code = HTTPStatus.CONFLICT
    expected_error = {
        "detail": "actually username exist",
        "status": expected_status_code,
    }
    response = mock_client.post(
        "/users",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_repeat_email(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test create user with email already in use with permission."""
    user = {
        "username": "new_string",
        "first_name": "string",
        "last_name": "string",
        "email": mock_usuarios[0]["email"],
        "password": "string",
    }
    expected_status_code = HTTPStatus.CONFLICT
    expected_error = {"detail": "actually email exist", "status": expected_status_code}
    response = mock_client.post(
        "/users",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_invalid_format_email(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test create user with email with incorrect format with permission."""
    user = {
        "username": "new_string",
        "first_name": "string",
        "last_name": "string",
        "email": "emailgmailcom",
        "password": "string",
    }
    expected_status_code = HTTPStatus.BAD_REQUEST
    expected_error = {
        "detail": "The email address is not valid. It must have exactly one @-sign.",
        "status": expected_status_code,
    }
    response = mock_client.post(
        "/users",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_password_whithout_login(
    mock_client: TestClient, secret_password: str
) -> None:
    """Test update user by id when user isn't logged in."""
    update_password_body = {
        "current_password": secret_password,
        "new_password": "secret_password2",
    }
    response = mock_client.put(
        "/users/me/password",
        json=update_password_body,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_update_password_incorrect_format(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    secret_password: str,
) -> None:
    """Test update user password with new password with incorrect format."""
    update_password_body = {
        "current_password": secret_password,
        "new_password": "secret_password2",
        # the format only allows: a-z A-Z 0-9 @$!%*?&# in range [8-24]
    }
    expected_status_code = HTTPStatus.BAD_REQUEST
    expected_error = {
        "detail": "incorrect password format, please check and try again",
        "status": expected_status_code,
    }
    response = mock_client.put(
        "/users/me/password",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_password_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_password_with_incorrect_current_password(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test update user password with incorrect current password."""
    update_password_body = {
        "current_password": "secret_pass",  # incorrect password
        "new_password": "secret#pass",
    }
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "Incorrect password, please check and try again",
        "status": expected_status_code,
    }
    response = mock_client.put(
        "/users/me/password",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_password_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_password_successfully(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], secret_password: str
) -> None:
    """Test successful update password."""
    update_password_body = {
        "current_password": secret_password,
        "new_password": "secret#pass",
    }
    user = mock_usuarios[6]
    access_token = get_access_token(
        user["username"], update_password_body["current_password"], mock_client
    )
    response = mock_client.put(
        "/users/me/password",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_password_body,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "password updated successfully"}
    access_token = get_access_token(
        user["username"], update_password_body["current_password"], mock_client
    )
    assert access_token is None
    access_token = get_access_token(
        user["username"], update_password_body["new_password"], mock_client
    )
    assert access_token
    response = mock_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == HTTPStatus.OK


def test_get_all_users_without_permission(
    mock_client: TestClient, mock_access_token: str
) -> None:
    """Test get all users."""
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.get(
        "/users", headers={"Authorization": f"Bearer {mock_access_token}"}
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_all_users(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_usuarios: List[Dict[str, Any]],
) -> None:
    """Test get all users."""
    expected_results = mock_usuarios.copy()
    key_with_str_value(expected_results, "id")
    response = mock_client.get(
        "/users",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    response_results = {user["username"]: user for user in response.json()}
    ignored_keys = ["hashed_password"]
    for usuario in expected_results:
        result = response_results[usuario["username"]]
        for key in usuario:
            if key not in ignored_keys:
                assert usuario[key] == result[key]


def test_get_all_users_skip_limit(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_usuarios: List[Dict[str, Any]],
) -> None:
    """Test get all users."""
    skip = 1
    limit = len(mock_usuarios) - 2
    stop = skip + limit
    expected_results = mock_usuarios[skip:stop].copy()
    key_with_str_value(expected_results, "id")
    response = mock_client.get(
        "/users",
        params={"skip": skip, "limit": limit},
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    response_results = {user["username"]: user for user in response.json()}
    ignored_keys = ["hashed_password"]
    assert len(response_results) == len(expected_results)
    for usuario in expected_results:
        result = response_results[usuario["username"]]
        for key in usuario:
            if key not in ignored_keys:
                assert usuario[key] == result[key]


def test_user_update_without_permission(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], mock_access_token: str
) -> None:
    """Test user update without permission."""
    update_user = {
        "first_name": "newuser",
        "last_name": "newuserlastmod",
        "email": "newuser@gmail.com",
        "disabled": False,
    }
    user_id = str(mock_usuarios[3]["id"])
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        json=update_user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_user_update(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test user update with permission."""
    update_user = {
        "first_name": "newuser",
        "last_name": "newuserlastmod",
        "email": "newuser@gmail.com",
        "disabled": False,
    }
    user_id = str(mock_usuarios[3]["id"])
    expected_results = update_user.copy()
    expected_results["id"] = user_id
    expected_results["username"] = mock_usuarios[3]["username"]
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_user,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "role updated successfully"}

    response = mock_client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.json() == expected_results


def test_user_update_with_empty_data(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test user update when data is empty with permission."""
    user_id = str(mock_usuarios[2]["id"])
    expected_results = {
        "id": user_id,
        "username": mock_usuarios[2]["username"],
        "first_name": mock_usuarios[2]["first_name"],
        "last_name": mock_usuarios[2]["last_name"],
        "email": mock_usuarios[2]["email"],
        "disabled": mock_usuarios[2]["disabled"],
    }
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json={},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "role updated successfully"}

    response = mock_client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.json() == expected_results


def test_user_update_a_value_is_blank_string(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test update a user with empty data fields with permission."""
    update_user = {
        "first_name": " ",
        "last_name": None,
        "email": "user@gmail.com",
        "disabled": False,
    }
    user_id = str(mock_usuarios[3]["id"])
    expected_status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    expected_error = {
        "detail": ["String should have at least 1 character"],
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_enable_a_disabled_user(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test enable a disabled user with permission."""
    update_user = {
        "disabled": False,
    }
    user_id = str(mock_usuarios[4]["id"])
    assert mock_usuarios[4]["disabled"]
    expected_results = {
        "id": user_id,
        "username": mock_usuarios[4]["username"],
        "first_name": mock_usuarios[4]["first_name"],
        "last_name": mock_usuarios[4]["last_name"],
        "email": mock_usuarios[4]["email"],
        "disabled": False,
    }
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_user,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "role updated successfully"}

    response = mock_client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.json() == expected_results


def test_user_update_when_id_not_exist(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test update an user with an non existent user id with permission."""
    update_user = {
        "first_name": "newuser",
        "last_name": "newuserlastmod",
        "email": "user@gmail.com",
        "disabled": False,
    }
    user_id = str(random_uuid)
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"user {user_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_user_update_when_email_exist(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test update user with an email already used with permission."""
    update_user = {
        "first_name": "newuser",
        "last_name": "newuserlastmod",
        "email": mock_usuarios[0]["email"],
        "disabled": False,
    }
    user_id = str(mock_usuarios[3]["id"])
    expected_status_code = HTTPStatus.CONFLICT
    expected_error = {"detail": "actually email exist", "status": expected_status_code}
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_user_update_when_email_invalid(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test update with email have an non existent domain with permission."""
    update_user = {
        "first_name": "newuser",
        "last_name": "newuserlastmod",
        "email": "newuser@kadasoftware.com.mx",
        "disabled": False,
    }
    user_id = str(mock_usuarios[3]["id"])
    expected_status_code = HTTPStatus.BAD_REQUEST
    expected_error = {
        "detail": "The domain name kadasoftware.com.mx does not exist.",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_user_update_when_email_format_invalid(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test update user with email have an incorrect format with permission."""
    update_user = {
        "first_name": "newuser",
        "last_name": "newuserlastmod",
        "email": "newuser",
        "disabled": False,
    }
    user_id = str(mock_usuarios[3]["id"])
    expected_status_code = HTTPStatus.BAD_REQUEST
    expected_error = {
        "detail": "The email address is not valid. It must have exactly one @-sign.",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_user,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_user_password_whithout_login(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
) -> None:
    """Test update user password when user isn't logged in."""
    update_password_body = {
        "new_password": "secret#pass",
    }
    user_id = str(mock_usuarios[0]["id"])
    response = mock_client.put(
        f"/users/{user_id}/password",
        json=update_password_body,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_update_user_password_incorrect_format(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
    secret_password: str,
) -> None:
    """Test update user password with new password with incorrect format."""
    update_password_body = {
        "new_password": secret_password,
    }
    user_id = str(mock_usuarios[0]["id"])
    expected_status_code = HTTPStatus.BAD_REQUEST
    expected_error = {
        "detail": "incorrect password format, please check and try again",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}/password",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_password_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_password_when_id_not_exist(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test update user password when id not exist."""
    update_password_body = {
        "new_password": "secret#pass",
    }
    user_id = str(random_uuid)
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"user {user_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}/password",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_password_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_user_password_without_permission(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], mock_access_token: str
) -> None:
    """Test update user password without permission."""
    update_password_body = {
        "new_password": "secret#pass",
    }
    user_id = str(mock_usuarios[0]["id"])
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}/password",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        json=update_password_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_user_password(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test update user password with permission."""
    update_password_body = {
        "new_password": "secret#pass",
    }
    user_id = str(mock_usuarios[0]["id"])
    response = mock_client.put(
        f"/users/{user_id}/password",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=update_password_body,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "password updated successfully"}

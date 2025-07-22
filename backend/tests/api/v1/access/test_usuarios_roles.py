"""Unit test for user roles functionalities."""
from http import HTTPStatus
from typing import Any, Callable, Dict, List
from uuid import UUID

from starlette.testclient import TestClient


def test_get_roles_user(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test get user roles by user id with permission."""
    current_user = mock_usuarios[6].copy()
    current_user.pop("hashed_password")
    expected_results = {
        "usuario": current_user,
        "roles": [
            {
                "role": {"id": str(mock_roles[0]["id"]), "role_name": "usuario"},
                "permissions": [
                    {
                        "id": "get_current_user_info",
                        "module": "usuarios",
                        "description": "Obtiene la información de usuario actual",
                    },
                    {
                        "id": "update_current_user_password",
                        "module": "usuarios",
                        "description": "Actualiza la contraseña de usuario actual",
                    },
                ],
            }
        ],
    }
    user_id = current_user["id"] = str(current_user["id"])
    response = mock_client.get(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_get_roles_user_without_permission(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], mock_access_token: str
) -> None:
    """Test get user roles by user id without permission."""
    user_id = str(mock_usuarios[0]["id"])
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.get(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_user_does_not_have_role(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test get user roles when user haven't roles with permission."""
    current_user = mock_usuarios[2].copy()
    current_user.pop("hashed_password")
    expected_results = {
        "usuario": current_user,
        "roles": [],
    }
    user_id = current_user["id"] = str(current_user["id"])
    response = mock_client.get(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_user_roles_not_found(
    mock_client: TestClient, mock_authorized_user_access_token: str, random_uuid: UUID
) -> None:
    """Test get user roles when user doesn't exists with permission."""
    user_id = random_uuid
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"user {user_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.get(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_assign_role_to_non_existent_user(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
    random_uuid: UUID,
) -> None:
    """Test assign user roles to a non existent user with permission."""
    non_existent_user_id = str(random_uuid)
    assign_role_body = [str(mock_roles[0]["id"])]
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"user {non_existent_user_id} not found",
        "status": expected_status_code,
    }

    response = mock_client.put(
        f"/users/{non_existent_user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_role_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_assign_non_existent_role_to_user(
    mock_usuarios: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test assign non existent user role to an user with permission."""
    user_id = str(mock_usuarios[0]["id"])
    non_existent_role = str(random_uuid)
    assign_role_body = [non_existent_role]

    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"roles not found: {non_existent_role}",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_role_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_assign_assigned_roles(
    mock_usuarios: List[Dict[str, Any]],
    mock_assigned_roles: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
) -> None:
    """Test assign already assigned roles to the user with permission."""
    user_id = str(mock_usuarios[0]["id"])
    assigned_roles = mock_assigned_roles(user_id)
    assign_role_body = [role["id"] for role in assigned_roles]

    response = mock_client.put(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_role_body,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "user roles already exist"}


def test_assign_non_assigned_roles_without_permission(
    mock_usuarios: List[Dict[str, Any]],
    mock_assigned_roles: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_all_roles: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_access_token: str,
) -> None:
    """Test non assign assigned roles to the user without permission."""
    user_id = str(mock_usuarios[0]["id"])
    assigned_roles = mock_assigned_roles(user_id)
    assigned_roles_id = {str(role["id"]) for role in assigned_roles}
    assign_role_body = [
        str(role["id"])
        for role in mock_all_roles
        if str(role["id"]) not in assigned_roles_id
    ]
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        json=assign_role_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_assign_non_assigned_roles(
    mock_usuarios: List[Dict[str, Any]],
    mock_assigned_roles: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_all_roles: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
) -> None:
    """Test non assign assigned roles to the user with permission."""
    user_id = str(mock_usuarios[0]["id"])
    assigned_roles = mock_assigned_roles(user_id)
    assigned_roles_id = {str(role["id"]) for role in assigned_roles}
    assign_role_body = [
        str(role["id"])
        for role in mock_all_roles
        if str(role["id"]) not in assigned_roles_id
    ]

    response = mock_client.put(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_role_body,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "user roles updated successfully"}


def test_delete_role_from_non_existent_user(
    mock_roles: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test delete role from non existent user with permission."""
    non_existent_user_id = str(random_uuid)
    assign_role_body = [str(mock_roles[0]["id"])]
    assign_role_params = {"role_ids": assign_role_body}
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"user {non_existent_user_id} not found",
        "status": expected_status_code,
    }

    response = mock_client.delete(
        f"/users/{non_existent_user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=assign_role_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_non_existent_role_to_user(
    mock_usuarios: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test delete non existent role to an user with permission."""
    user_id = str(mock_usuarios[0]["id"])
    non_existent_role = str(random_uuid)
    assign_role_params = {"role_ids": [non_existent_role]}
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"roles not found: {non_existent_role}",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=assign_role_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_non_assigned_roles(
    mock_usuarios: List[Dict[str, Any]],
    mock_all_roles: List[Dict[str, Any]],
    mock_assigned_roles: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
) -> None:
    """Test delete non assigned role from an user with permission."""
    user_id = str(mock_usuarios[1]["id"])
    assigned_roles = mock_assigned_roles(user_id)
    assigned_roles_id = {str(role["id"]) for role in assigned_roles}
    unassigned_roles_body = [
        str(role["id"])
        for role in mock_all_roles
        if str(role["id"]) not in assigned_roles_id
    ]
    unassigned_roles_params = {"role_ids": unassigned_roles_body}
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": "roles not assigned to user: "
        + ", ".join(sorted(unassigned_roles_body)),
        "status": expected_status_code,
    }

    response = mock_client.delete(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=unassigned_roles_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_assigned_roles(
    mock_assigned_roles: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_usuarios: List[Dict[str, Any]],
    mock_all_roles: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
) -> None:
    """Test delete assigned roles from an user with permission."""
    user_id = str(mock_usuarios[0]["id"])
    assigned_roles = mock_assigned_roles(user_id)
    assigned_roles_id = {role["id"] for role in assigned_roles}
    assign_role_body = [
        role["id"] for role in mock_all_roles if role["id"] in assigned_roles_id
    ]
    assign_role_params = {"role_ids": assign_role_body}

    response = mock_client.delete(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=assign_role_params,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "roles deleted successfully"}


def test_delete_assigned_roles_whitout_permission(
    mock_assigned_roles: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_usuarios: List[Dict[str, Any]],
    mock_all_roles: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_access_token: str,
) -> None:
    """Test delete assigned roles from an user without permission."""
    user_id = str(mock_usuarios[0]["id"])
    assigned_roles = mock_assigned_roles(user_id)
    assigned_roles_id = {role["id"] for role in assigned_roles}
    assign_role_body = [
        role["id"] for role in mock_all_roles if role["id"] in assigned_roles_id
    ]
    assign_role_params = {"role_ids": assign_role_body}
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        params=assign_role_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_my_user_roles(
    mock_client: TestClient,
    mock_usuarios: List[Dict[str, Any]],
    mock_permissions: List[Dict[str, Any]],
    mock_authorized_user_access_token: str,
) -> None:
    """Test get current user roles."""
    current_user = mock_usuarios[5].copy()
    current_user.pop("hashed_password")
    current_user["id"] = str(current_user["id"])
    expected_results = {
        "usuario": current_user,
        "roles": [{"role": {"role_name": "admin"}, "permissions": mock_permissions}],
    }
    response = mock_client.get(
        "/users/me/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )

    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["usuario"] == expected_results["usuario"]

    role_permissions_response = {
        role["role"]["role_name"]: {
            permission["id"]: permission for permission in role["permissions"]
        }
        for role in response_json["roles"]
    }
    role_permissions_expected = {
        "admin": {permission["id"]: permission for permission in mock_permissions}
    }

    assert role_permissions_response == role_permissions_expected


def test_get_my_roles_user_without_permission(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], mock_access_token: str
) -> None:
    """Test get user roles by user id without permission."""
    current_user = mock_usuarios[0].copy()
    current_user.pop("hashed_password")
    current_user["id"] = str(current_user["id"])
    expected_results = {
        "usuario": current_user,
        "roles": [],
    }
    response = mock_client.get(
        "/users/me/roles",
        headers={"Authorization": f"Bearer {mock_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["usuario"] == expected_results["usuario"]
    assert response_json["roles"] == expected_results["roles"]

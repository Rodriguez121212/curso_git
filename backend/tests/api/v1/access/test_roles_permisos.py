"""Unit test for roles permissions functionalities."""
from http import HTTPStatus
from typing import Any, Callable, Dict, List
from uuid import UUID

from starlette.testclient import TestClient


def test_assign_role_to_non_existent_user(
    mock_client: TestClient, mock_authorized_user_access_token: str, random_uuid: UUID
) -> None:
    """Test assign a role to a non existent user with permission."""
    non_existent_role_id = str(random_uuid)
    assign_permision_body = ["get_all_users"]
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"role {non_existent_role_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/roles/{non_existent_role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_permision_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_assign_non_existent_permission_to_user(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test assign a non existent permission to an user with permission."""
    role_id = str(mock_roles[2]["id"])
    assign_permission_body = ["non_existent_permission"]
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"permissions not found: {', '.join(assign_permission_body)}",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_permission_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_assign_assigned_permissions(
    mock_assigned_permissions: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test assign an already assigned permissions to the same user.

    With permission.
    """
    role_id = str(mock_roles[2]["id"])
    assigned_roles = mock_assigned_permissions(role_id)
    assign_role_body = [role["id"] for role in assigned_roles]
    response = mock_client.put(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_role_body,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "permissions already exist"}


def test_assign_non_assigned_permissions_without_permission(
    mock_assigned_permissions: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_all_permissions: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test assign a non assigned permissions to an user without permission."""
    role_id = str(mock_roles[0]["id"])
    assigned_permissions = mock_assigned_permissions(role_id)
    assigned_permissions_id = {permission["id"] for permission in assigned_permissions}
    assign_permission_body = [
        permission["id"]
        for permission in mock_all_permissions
        if permission["id"] not in assigned_permissions_id
    ]
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        json=assign_permission_body,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_assign_non_assigned_permissions(
    mock_assigned_permissions: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_all_permissions: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test assign a non assigned permissions to an user with permission."""
    role_id = str(mock_roles[0]["id"])
    assigned_permissions = mock_assigned_permissions(role_id)
    assigned_permissions_id = {permission["id"] for permission in assigned_permissions}
    assign_permission_body = [
        permission["id"]
        for permission in mock_all_permissions
        if permission["id"] not in assigned_permissions_id
    ]
    response = mock_client.put(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=assign_permission_body,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "permissions updated successfully"}


def test_delete_permissions_assign_roles(
    mock_assigned_permissions: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_all_permissions: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test permissions delete assigned to role with permission."""
    role_id = str(mock_roles[0]["id"])
    permissions_roles = mock_assigned_permissions(role_id)
    delete_permissions_ids = {permission["id"] for permission in permissions_roles}
    delete_permissions = [
        permission["id"]
        for permission in mock_all_permissions
        if permission["id"] in delete_permissions_ids
    ]
    permissions_params = {"permission_ids": delete_permissions}
    response = mock_client.delete(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=permissions_params,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "permissions deleted successfully"}


def test_delete_permissions_assign_roles_without_permission(
    mock_assigned_permissions: Callable[[UUID | str], List[Dict[str, Any]]],
    mock_all_permissions: List[Dict[str, Any]],
    mock_client: TestClient,
    mock_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test permissions delete assigned to role without permission."""
    role_id = str(mock_roles[0]["id"])
    permissions_roles = mock_assigned_permissions(role_id)
    delete_permissions_ids = {permission["id"] for permission in permissions_roles}
    delete_permissions = [
        permission["id"]
        for permission in mock_all_permissions
        if permission["id"] in delete_permissions_ids
    ]
    permissions_params = {"permission_ids": delete_permissions}
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        params=permissions_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_permissions_assign_roles_when_id_role_not_found(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test permissions delete assigned to role no found with permission."""
    role_id = str(random_uuid)
    delete_permissions = ["get_all_users"]
    permissions_params = {"permission_ids": delete_permissions}
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"role {role_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=permissions_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_permissions_assign_roles_when_permissions_list_empty(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test param of list empty permissions to delete of role.

    With permission.
    """
    role_id = str(mock_roles[2]["id"])
    permissions_params: Dict[str, Any] = {"permission_ids": []}
    expected_status_code = HTTPStatus.BAD_REQUEST
    expected_error = {
        "detail": "permission list is empty",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=permissions_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_permissions_of_role_when_permissions_not_assign(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test permissions ids delete not assigned to role with permission."""
    role_id = str(mock_roles[1]["id"])
    delete_permissions = ["get_all_users"]
    permissions_params = {"permission_ids": delete_permissions}
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"permissions not assigned to role: {', '.join(delete_permissions)}",
        "status": expected_status_code,
    }

    response = mock_client.delete(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=permissions_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_permissions_assign_roles_when_id_permissions_not_found(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test permissions id delete not found in role with permission."""
    role_id = str(mock_roles[2]["id"])
    existing_permissions = ["get_all_users"]
    non_existing_permissions = ["string"]
    delete_permissions = existing_permissions + non_existing_permissions
    permissions_params = {"permission_ids": delete_permissions}
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"permissions not found: {', '.join(non_existing_permissions)}",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/roles/{role_id}/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        params=permissions_params,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error

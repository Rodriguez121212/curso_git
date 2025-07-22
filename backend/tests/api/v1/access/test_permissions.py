"""Unit test for permissions functionalities."""
from http import HTTPStatus
from typing import Any, Dict, List
from uuid import UUID

from starlette.testclient import TestClient

from utils.test.common import sort_dict_list


def test_get_permissions(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_all_permissions: List[Dict[str, Any]],
) -> None:
    """Test get permissions with permission."""
    expected_results = sort_dict_list(data=mock_all_permissions)
    response = mock_client.get(
        "/permissions",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    response_json = sort_dict_list(data=response.json())
    assert response_json == expected_results


def test_get_permissions_without_permission(
    mock_client: TestClient,
    mock_access_token: str,
) -> None:
    """Test get permissions without permission."""
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.get(
        "/permissions",
        headers={"Authorization": f"Bearer {mock_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_assign_role_permission_without_permission(
    mock_client: TestClient, mock_access_token: str, mock_roles: List[Dict[str, Any]]
) -> None:
    """Test get permissions by id of the role without permission."""
    role_id = str(mock_roles[1]["id"])
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }

    response = mock_client.get(
        f"/permissions/role/{role_id}",
        headers={"Authorization": f"Bearer {mock_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_assign_role_permission(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_permissions: List[Dict[str, Any]],
    mock_roles_permissions: List[Dict[str, Any]],
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test get permissions by id of the role with permission."""
    role_id = str(mock_roles[1]["id"])
    nombre_rol = next(
        (role["role_name"] for role in mock_roles if str(role["id"]) == role_id),
        None,
    )
    # Buscar permisos asignados a rol en la lista mock_role_permission
    permisos_rol = [
        permiso
        for permiso in mock_permissions
        for asignacion in mock_roles_permissions
        if asignacion["permission_id"] == permiso["id"]
        and str(asignacion["role_id"]) == role_id
    ]
    expected_results = {
        "role_name": nombre_rol,
        "permissions": [
            {"module": permiso["module"], "description": permiso["description"]}
            for permiso in permisos_rol
        ],
    }
    response = mock_client.get(
        f"/permissions/role/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_get_assign_role_permission_not_exist_permission_for_role(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
    mock_roles_permissions: List[Dict[str, Any]],
) -> None:
    """Test get empty list of permissions by id of the role with permission."""
    id_rol_sin_permisos = next(
        (
            role["id"]
            for role in mock_roles
            if not any(rp["role_id"] == role["id"] for rp in mock_roles_permissions)
        ),
        None,
    )
    nombre_rol = next(
        (role["role_name"] for role in mock_roles if role["id"] == id_rol_sin_permisos),
        None,
    )
    expected_results: Dict[str, Any] = {"role_name": nombre_rol, "permissions": []}
    role_id = id_rol_sin_permisos
    response = mock_client.get(
        f"/permissions/role/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_get_assign_role_permission_not_exist_role(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    random_uuid: UUID,
) -> None:
    """Test_get_assign_role_permission_not_exist_role with permission."""
    role_id = str(random_uuid)
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"role {role_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.get(
        f"/permissions/role/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error

"""Unit test for roles functionalities."""
from http import HTTPStatus
from typing import Any, Dict, List
from uuid import UUID

from starlette.testclient import TestClient

from utils.test.common import is_valid_uuid


def test_role_name_with_only_spaces(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test a role name with only space characters with permission."""
    new_role = {"role_name": "          "}
    expected_status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    expected_error = {
        "detail": ["String should have at least 5 characters"],
        "status": expected_status_code,
    }
    response = mock_client.post(
        "/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=new_role,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_role_name_with_len_min_five(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test role name with less than five characters with permission."""
    new_role = {"role_name": "role"}
    expected_status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    expected_error = {
        "detail": ["String should have at least 5 characters"],
        "status": expected_status_code,
    }
    response = mock_client.post(
        "/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=new_role,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_role_name_already_exist(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test a role name that already exists with permission."""
    new_role = {"role_name": "usuario"}
    expected_status_code = HTTPStatus.CONFLICT
    expected_error = {
        "detail": f"role name {new_role['role_name']} is already taken",
        "status": expected_status_code,
    }
    response = mock_client.post(
        "/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=new_role,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_role_name_with_spaces(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test a valid role name with spaces with permission."""
    new_role = {"role_name": "          administrador          "}
    response = mock_client.post(
        "/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=new_role,
    )
    assert response.status_code == HTTPStatus.CREATED
    result = response.json()
    assert type(result) == dict
    assert set(result.keys()) == {"detail", "id"}
    assert result["detail"] == "role created successfully"
    role_id = result["id"]
    assert is_valid_uuid(role_id)

    expected_results = {"id": role_id, "role_name": new_role["role_name"].strip()}
    response = mock_client.get(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_create_role_without_permission(
    mock_client: TestClient, mock_access_token: str
) -> None:
    """Test a valid role name without permission."""
    new_role = {"role_name": "profesor"}
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.post(
        "/roles",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        json=new_role,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_valid_role_name(
    mock_client: TestClient, mock_authorized_user_access_token: str
) -> None:
    """Test a valid role name with permission."""
    new_role = {"role_name": "profesor"}
    response = mock_client.post(
        "/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=new_role,
    )
    assert response.status_code == HTTPStatus.CREATED
    result = response.json()
    assert type(result) == dict
    assert set(result.keys()) == {"detail", "id"}
    assert result["detail"] == "role created successfully"
    role_id = result["id"]
    assert is_valid_uuid(role_id)

    expected_results = {"id": role_id, "role_name": new_role["role_name"]}
    response = mock_client.get(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_update_role_name_without_permission(
    mock_client: TestClient,
    mock_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test update a role name without permission."""
    updateRoleName = {"role_name": "role_prueba"}
    role_id = str(mock_roles[0]["id"])
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_access_token}"},
        json=updateRoleName,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_role_name_successful(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test update a role name success with permission."""
    updateRoleName = {"role_name": "role_prueba"}
    role_id = str(mock_roles[0]["id"])
    response = mock_client.put(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=updateRoleName,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "role updated successfully"}


def test_update_role_name_id_not_exist(
    mock_client: TestClient, mock_authorized_user_access_token: str, random_uuid: UUID
) -> None:
    """Test update role name id that doesn't exist with permission."""
    updateRoleName = {"role_name": "role_prueba"}
    role_id = str(random_uuid)
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"role {role_id} not found",
        "status": expected_status_code,
    }
    response = mock_client.put(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=updateRoleName,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_role_name_exist(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test update a role with name already taken."""
    updateRoleName = {"role_name": "dont_assign_this_role"}
    expected_status_code = HTTPStatus.CONFLICT
    expected_error = {
        "detail": f"role name {updateRoleName['role_name']} is already taken",
        "status": expected_status_code,
    }
    role_id = str(mock_roles[0]["id"])
    response = mock_client.put(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=updateRoleName,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_update_role_name_unprocessable_entity(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test_update_role_name_unprocessable_entity with permission."""
    updateRoleName = {"role_name": "x"}
    expected_status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    expected_error = {
        "detail": ["String should have at least 5 characters"],
        "status": expected_status_code,
    }
    role_id = str(mock_roles[0]["id"])
    response = mock_client.put(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
        json=updateRoleName,
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_roles_without_permission(
    mock_client: TestClient,
    mock_access_token: str,
) -> None:
    """Test get roles without permission."""
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.get(
        "/roles",
        headers={"Authorization": f"Bearer {mock_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_get_roles(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_all_roles: List[Dict[str, Any]],
) -> None:
    """Test get roles with permission."""
    expected_results = [
        {"id": str(role["id"]), "role_name": role["role_name"]}
        for role in mock_all_roles
    ]
    response = mock_client.get(
        "/roles",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_results


def test_delete_role_without_permission(
    mock_client: TestClient,
    mock_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test delete role by id of the role without permission."""
    role_id = str(mock_roles[0]["id"])
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": "user does not have permission",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_role(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test delete role by id of the role with permission."""
    role_id = str(mock_roles[0]["id"])
    response = mock_client.delete(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"detail": "role deleted successfully"}


def test_delete_role_to_current_user(
    mock_client: TestClient,
    mock_authorized_user_access_token: str,
    mock_roles: List[Dict[str, Any]],
) -> None:
    """Test delete role from current user asigned."""
    role_id = str(mock_roles[2]["id"])
    expected_status_code = HTTPStatus.FORBIDDEN
    expected_error = {
        "detail": f"cannot remove role {role_id}, is assigned to logged user",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error


def test_delete_role_when_id_role_not_found(
    mock_client: TestClient, mock_authorized_user_access_token: str, random_uuid: UUID
) -> None:
    """Test delete role by id when id role not found with permission."""
    non_existent_role = str(random_uuid)
    expected_status_code = HTTPStatus.NOT_FOUND
    expected_error = {
        "detail": f"role {non_existent_role} not found",
        "status": expected_status_code,
    }
    response = mock_client.delete(
        f"/roles/{non_existent_role}",
        headers={"Authorization": f"Bearer {mock_authorized_user_access_token}"},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_error

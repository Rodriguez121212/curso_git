"""Providing fixtures for usuarios tests."""
import pathlib
import uuid
from typing import Any, Callable, Dict, Generator, List, Literal
from unittest.mock import patch

import pytest
from argon2 import PasswordHasher
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from starlette.testclient import TestClient

from app.main import app
from app.models import Base
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole
from app.services.user import UserService
from utils.test.database import MockDatabase
from utils.test.fixtures import get_fixture_data, key_with_uuids
from utils.test.users import get_access_token


@pytest.fixture(scope="module")
def secret_password() -> Literal["secret_password"]:
    """Secret password for test."""
    return "secret_password"


@pytest.fixture(scope="module")
def hashed_password(secret_password: str) -> str:
    """Hashed password for test."""
    password_hasher = PasswordHasher()
    return password_hasher.hash(secret_password)


@pytest.fixture(scope="module")
def path() -> str:
    """Get the current path for test."""
    return str(pathlib.Path(__file__).parent.resolve())


@pytest.fixture(scope="module")
def mock_usuarios(path: str, hashed_password: str) -> List[Dict[str, Any]]:
    """Usuarios para pruebas."""
    users = get_fixture_data(path, "usuarios")
    for user in users:
        user["hashed_password"] = hashed_password
    key_with_uuids(users, "id")
    return users


@pytest.fixture(scope="module")
def mock_roles(path: str) -> List[Dict[str, Any]]:
    """Roles para pruebas."""
    roles = get_fixture_data(path, "roles")
    key_with_uuids(roles, "id")
    return roles


@pytest.fixture(scope="module")
def mock_permissions(path: str) -> List[Dict[str, Any]]:
    """Permisos para pruebas."""
    return get_fixture_data(path, "permissions")


@pytest.fixture(scope="module")
def mock_users_roles(path: str) -> List[Dict[str, Any]]:
    """Roles de usuario para pruebas."""
    users_roles = get_fixture_data(path, "users_roles")
    key_with_uuids(users_roles, "user_id")
    key_with_uuids(users_roles, "role_id")
    return users_roles


@pytest.fixture(scope="module")
def mock_roles_permissions(path: str) -> List[Dict[str, Any]]:
    """Permisos de roles para pruebas."""
    roles_permissions = get_fixture_data(path, "roles_permissions")
    key_with_uuids(roles_permissions, "role_id")
    return roles_permissions


@pytest.fixture(scope="module")
def mock_data(
    mock_usuarios: List[Dict[str, Any]],
    mock_roles: List[Dict[str, Any]],
    mock_permissions: List[Dict[str, Any]],
    mock_users_roles: List[Dict[str, Any]],
    mock_roles_permissions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Datos para cargar en la base de datos de pruebas."""
    return [
        {
            "class": User,
            "json": mock_usuarios,
        },
        {
            "class": Role,
            "json": mock_roles,
        },
        {
            "class": Permission,
            "json": mock_permissions,
        },
        {
            "class": UserRole,
            "json": mock_users_roles,
        },
        {
            "class": RolePermission,
            "json": mock_roles_permissions,
        },
    ]


@pytest.fixture(scope="module")
def mock_database(
    path: str, mock_data: List[Dict[str, Any]]
) -> Generator[MockDatabase, None, None]:
    """Get the database for access testing."""
    mock_database: MockDatabase = MockDatabase(
        db_name="test_db.sql", path=path, Base=Base
    )
    for data in mock_data:
        mock_database.load_rows(data["class"], data["json"])
    yield mock_database
    del mock_database


@pytest.fixture
def mock_client(
    mock_database: MockDatabase,
) -> Generator[TestClient, None, None]:
    """Cliente de pruebas."""
    with patch(
        "app.dependencies.DbSession",
        mock_database.Session,
    ):
        yield TestClient(app)


@pytest.fixture
def mock_access_token(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], secret_password: str
) -> Any:
    """Access token de pruebas."""
    user = mock_usuarios[0]
    return get_access_token(
        username=user["username"], password=secret_password, client=mock_client
    )


@pytest.fixture
def mock_authorized_user_access_token(
    mock_client: TestClient, mock_usuarios: List[Dict[str, Any]], secret_password: str
) -> Any:
    """Access token de pruebas."""
    user = mock_usuarios[5]  # user with all permissions from fixtures
    return get_access_token(
        username=user["username"], password=secret_password, client=mock_client
    )


@pytest.fixture
def mock_empty_username_token() -> str:
    """Token con nombre de usuario vacio para pruebas."""
    return UserService.encode_access_token(data={})


@pytest.fixture
def mock_invalid_token() -> Literal["mock_invalid_access_token"]:
    """Get a invalid access token for testing."""
    return "mock_invalid_access_token"


@pytest.fixture
def mock_username_doesnt_exist_token() -> str:
    """Token con nombre de usuario no existente para pruebas."""
    return UserService.encode_access_token(data={"sub": "username_no_existe"})


@pytest.fixture
def mock_session(
    mock_database: MockDatabase,
) -> Generator[Session, None, None]:
    """Session de base de datos de pruebas."""
    with Session(mock_database.engine) as session:
        yield session


@pytest.fixture
def mock_assigned_roles(
    mock_session: Session,
) -> Callable[[uuid.UUID | str], List[Dict[str, Any]]]:
    """Roles asignados para pruebas."""

    def _method(user_id: uuid.UUID | str) -> List[Dict[str, Any]]:
        if type(user_id) == str:
            user_id = uuid.UUID(user_id)
        user = mock_session.get(User, user_id)
        if user:
            return [
                {"id": user_role.role_id, "role_name": user_role.role.role_name}
                for user_role in user.user_roles
            ]
        return []

    return _method


@pytest.fixture
def mock_all_roles(mock_session: Session) -> List[Dict[str, Any]]:
    """Lista de todos los roles para pruebas."""
    roles = mock_session.scalars(select(Role)).all()
    return [{"id": role.id, "role_name": role.role_name} for role in roles]


@pytest.fixture
def mock_all_users(mock_session: Session) -> List[Dict[str, Any]]:
    """Lista de todos los usuarios para pruebas."""
    users = mock_session.scalars(select(User)).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "disabled": user.disabled,
        }
        for user in users
    ]


@pytest.fixture
def mock_assigned_permissions(
    mock_session: Session,
) -> Callable[[uuid.UUID | str], List[Dict[str, Any]]]:
    """Return a method to get all permissions assigned to a role by id."""

    def _method(role_id: uuid.UUID | str) -> List[Dict[str, Any]]:
        if type(role_id) == str:
            role_id = uuid.UUID(role_id)
        role = mock_session.get(Role, role_id)
        if role:
            return [
                {"id": role_permission.permission_id}
                for role_permission in role.role_permissions
            ]
        return []

    return _method


@pytest.fixture
def mock_all_permissions(mock_session: Session) -> List[Dict[str, Any]]:
    """Lista de todos los permisos para pruebas."""
    permissions = mock_session.scalars(select(Permission)).all()
    return [
        {
            "id": permission.id,
            "module": permission.module,
            "description": permission.description,
        }
        for permission in permissions
    ]


@pytest.fixture
def random_uuid() -> uuid.UUID:
    """Genera uuid4 random."""
    return uuid.uuid4()

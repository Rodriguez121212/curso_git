"""Providing fixtures for consultas tests."""
import pathlib
from typing import Any, Callable, Dict, List

import pytest

from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from utils.test.fixtures import get_fixture_data


@pytest.fixture(scope="module")
def path() -> str:
    """Get module folder path."""
    return str(pathlib.Path(__file__).parent.resolve())


@pytest.fixture(scope="module")
def mock_users(path: str) -> List[Dict[str, Any]]:
    """Get mock users from fixture file."""
    return get_fixture_data(path, "users")


@pytest.fixture
def mock_non_authorized_user() -> Callable[[], User]:
    """Mock user without permissions."""

    def non_authorized_user() -> User:
        """Get non authorized user."""
        return User(
            id=1,
            username="fake_username",
            first_name="fake_first_name",
            last_name="fake_last_name",
            email="fake_email@emai.com",
            disabled=False,
        )

    return non_authorized_user


@pytest.fixture
def mock_authorized_user() -> Callable[[], User]:
    """Mock user with permissions."""

    def authorized_user() -> User:
        """Get authorized user."""
        user = User(
            id=1,
            username="fake_username",
            first_name="fake_first_name",
            last_name="fake_last_name",
            email="fake_email@emai.com",
            disabled=False,
        )
        role = Role(id=1, role_name="admin")
        UserRole(user=user, role=role)
        return user

    return authorized_user

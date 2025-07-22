"""Configuration for api v1 test module."""
import sqlite3
import uuid

import pytest


@pytest.fixture(scope="session", autouse=True)
def register_sqlite3_uuid4_adapter() -> None:
    """Register sqlite3 uuid4 adapter."""
    sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

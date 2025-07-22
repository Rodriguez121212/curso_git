"""Modelo ORM de role."""
from typing import List
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.role_permission import RolePermission


class Role(Base):
    """Modelo ORM de role."""

    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    role_name: Mapped[str] = mapped_column(unique=True)

    role_permissions: Mapped[List["RolePermission"]] = relationship()

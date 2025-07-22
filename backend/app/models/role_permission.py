"""Modelo ORM de relación de roles y sus permisos."""
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Annotated

from app.models import Base
from app.models.permission import Permission

role_fk = Annotated[UUID, mapped_column(ForeignKey("roles.id"), primary_key=True)]
permission_fk = Annotated[
    str, mapped_column(ForeignKey("permissions.id"), primary_key=True)
]


class RolePermission(Base):
    """Modelo ORM de relación roles y sus permiso."""

    __tablename__ = "roles_permissions"
    role_id: Mapped[role_fk]
    permission_id: Mapped[permission_fk]
    permission: Mapped["Permission"] = relationship()

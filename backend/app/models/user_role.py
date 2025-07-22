"""Modelo ORM de relación de usuarios y sus roles."""
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Annotated

from app.models import Base
from app.models.role import Role

user_fk = Annotated[UUID, mapped_column(ForeignKey("users.id"), primary_key=True)]
role_fk = Annotated[UUID, mapped_column(ForeignKey("roles.id"), primary_key=True)]


class UserRole(Base):
    """Modelo ORM de relación usuarios y sus roles."""

    __tablename__ = "users_roles"
    user_id: Mapped[user_fk]
    role_id: Mapped[role_fk]

    role: Mapped["Role"] = relationship()

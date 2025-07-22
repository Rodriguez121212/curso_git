"""Modelo ORM de usuario."""
from typing import List
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.user_role import UserRole


class User(Base):
    """Modelo ORM de user."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    disabled: Mapped[bool] = mapped_column(default=False)

    user_roles: Mapped[List["UserRole"]] = relationship()

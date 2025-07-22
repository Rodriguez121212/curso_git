"""Modelo ORM de permiso."""
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Permission(Base):
    """Modelo ORM de permiso."""

    __tablename__ = "permissions"
    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    module: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

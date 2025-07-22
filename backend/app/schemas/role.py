"""Esquemas de rol."""
from typing import List

from pydantic import UUID4, BaseModel, ConfigDict, Field

from app.schemas.permission import Permission


class RoleBase(BaseModel):
    """Esquema para actualización de rol de usuario."""

    role_name: str = Field(min_length=5)
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class Role(RoleBase):
    """Esquema para rol de usuario."""

    id: UUID4


class RoleDetail(BaseModel):
    """Esquema para Roles con permisos."""

    role: Role
    permissions: List[Permission]

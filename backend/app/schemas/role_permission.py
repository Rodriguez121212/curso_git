"""Esquemas de relación role y permiso."""
from typing import List

from pydantic import UUID4, BaseModel, ConfigDict

from app.schemas.permission import Permission
from app.schemas.role import Role


class RolePermissionBase(BaseModel):
    """Esquema para la relación de Role y Permiso."""

    role_id: UUID4
    permission_id: str
    model_config = ConfigDict(from_attributes=True)


class RolePermission(RolePermissionBase):
    """Esquema para la relación de Role y Permiso."""

    permission: Permission


class RolePermissions(Role):
    """Esquema para rol de usuario."""

    role_permissions: List[RolePermission]


class RolePermissionDetail(BaseModel):
    """Esquema para permisos asignados a rol."""

    role_name: str
    permissions: List[Permission]

"""Esquemas de relación usuario y rol."""
from pydantic import UUID4, BaseModel, ConfigDict

from app.schemas.role_permission import RolePermissions


class UserRoleBase(BaseModel):
    """Esquema para la relación de Role y Permiso."""

    user_id: UUID4
    role_id: UUID4
    model_config = ConfigDict(from_attributes=True)


class UserRole(UserRoleBase):
    """User role schema."""

    role: RolePermissions

"""Esquemas de usuario."""
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

from app.schemas.role import RoleDetail
from app.schemas.user_role import UserRole


class UserBase(BaseModel):
    """Esquema para usuario con información básica."""

    username: str = Field(min_length=5)
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: str = Field(min_length=5)
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class UserCreate(UserBase):
    """Esquema para creación de usuario."""

    password: str = Field(min_length=5)


class UserUpdate(BaseModel):
    """Esquema para actualización de usuario."""

    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    email: Optional[str] = Field(None, min_length=5)
    disabled: Optional[bool] = None
    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class UserPublic(UserBase):
    """Esquema para información publica de usuario."""

    id: UUID4
    disabled: bool = Field(default=False)


class User(UserPublic):
    """Esquema para información privada de usuario."""

    user_roles: List[UserRole]


class NewUser(UserPublic):
    """Esquema para información privada de usuario."""

    hashed_password: str


class UserPrivate(User):
    """Esquema para información privada de usuario."""

    hashed_password: str


class UserNewPassword(BaseModel):
    """Esquema para actualización de contraseña."""

    new_password: str = Field(min_length=5)


class UpdatePassword(UserNewPassword):
    """Esquema para actualización de contraseña."""

    current_password: str = Field(min_length=5)


class UserDetail(BaseModel):
    """Esquema para Usuario con roles y permisos."""

    usuario: UserPublic
    roles: List[RoleDetail]

    @classmethod
    def build(cls, user: UserPublic, user_roles: List[UserRole]) -> "UserDetail":
        """Construir objeto de tipo UserRoles.

        Keyword Arguments:
            user -- objeto usuario (default: {None})
            user_roles -- lista de objeto de roles de usuario (default: {None})
        """
        roles = [
            RoleDetail(
                role=user_role.role,
                permissions=[
                    role_permission.permission
                    for role_permission in user_role.role.role_permissions
                    if role_permission.permission
                ],
            )
            for user_role in user_roles
        ]
        return UserDetail(usuario=user, roles=roles)

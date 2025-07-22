"""Router para endpoints de roles."""
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.data.roles import initial_roles
from app.dependencies import (
    get_authorized_user,
    get_current_active_user,
    get_role_service,
    get_user_role_service,
    get_user_service,
)
from app.enums.permission import Permission
from app.schemas.common import Created, Success
from app.schemas.role import Role
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserDetail,
    UserNewPassword,
    UserPublic,
    UserUpdate,
)
from app.services.role import RoleService
from app.services.user import UserService
from app.services.user_role import UserRoleService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/me")
async def get_current_user(
    current_user: UserPublic = Depends(get_current_active_user),
) -> UserPublic:
    """Obtener usuario actual.

    Returns:
        Información de usuario actual
    """
    return current_user


@router.get(
    "/{user_id}",
    dependencies=[Depends(get_authorized_user(Permission.GET_USER_INFO))],
)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Obtener usuario.

    Arguments:
        user_id -- identificador de usuario

    Returns:
        Información de usuario
    """
    user: UserPublic = user_service.get_by(user_id)
    return user


@router.get("/me/roles")
async def get_current_user_roles(
    current_user: UserPublic = Depends(get_current_active_user),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> UserDetail:
    """Obtener roles y permisos de usuario actual.

    Returns:
        Roles y permisos de usuario actual
    """
    user_roles = user_role_service.get_by(current_user)
    return UserDetail.build(user=current_user, user_roles=user_roles)


@router.get(
    "/{user_id}/roles",
    dependencies=[
        Depends(get_authorized_user(Permission.GET_USER_INFO_WITH_ACCESS_DATA))
    ],
)
async def get_user_roles(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> UserDetail:
    """Obtener roles y permisos de usuario.

    Arguments:
        user_id -- identificador de usuario

    Returns:
        Roles y permisos de usuario
    """
    user = user_service.get_by(user_id)
    user_roles = user_role_service.get_by(user)
    return UserDetail.build(user=user, user_roles=user_roles)


@router.post(
    "/",
    dependencies=[Depends(get_authorized_user(Permission.CREATE_NEW_USER))],
    status_code=HTTPStatus.CREATED,
)
async def post_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> Created:
    """Crear usuario.

    Arguments:
        user_create -- información de usuario

    Returns:
        Mensaje de creación de usuario
    """
    user_id = user_service.insert(user_create)
    return Created(detail="user created successfully", id=user_id)


@router.post(
    "/newUser",
    status_code=HTTPStatus.CREATED,
)
async def post_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> Created:
    """Crear usuario con rol de Usuario para registros nuevos.

    Arguments:
        user_create -- información de usuario

    Returns:
        Mensaje de creación de usuario
    """
    user_id = user_service.insert(user_create)
    user = user_service.get_by(user_id)
    role = initial_roles[1]
    user_role_service.insert(
        user, [Role(role_name=role.get("role_name"), id=role.get("id"))]
    )
    return Created(detail="user created successfully", id=user_id)


@router.put("/me/password")
async def put_current_user_password(
    update_password: UpdatePassword,
    current_user: UserPublic = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> Success:
    """Actualizar contraseña de usuario actual.

    Arguments:
        update_password -- información con actualización de contraseña

    Returns:
        Mensaje de operación exitosa
    """
    user_service.update(current_user.id, update_password)
    return Success(detail="password updated successfully")


@router.get(
    "/",
    dependencies=[Depends(get_authorized_user(Permission.GET_ALL_USERS))],
)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
) -> List[UserPublic]:
    """Obtener usuarios.

    Keyword Arguments:
        skip -- numero de registros omitidos (default: {0})
        limit -- límite de registros entregados (default: {100})

    Returns:
        Lista de usuarios
    """
    return user_service.list(skip, limit)


@router.put(
    "/{user_id}/roles",
    dependencies=[Depends(get_authorized_user(Permission.ASSIGN_USER_ROLES))],
)
async def put_user_roles(
    user_id: UUID,
    role_ids: List[UUID],
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> Success:
    """Actualizar roles de usuario.

    Arguments:
        user_id -- identificador de usuario
        role_ids -- identificadores de roles a asignar a usuario

    Returns:
        Mensaje de operación exitosa
    """
    user = user_service.get_by(user_id)
    roles = role_service.filter_by(role_ids)
    created_user_roles = user_role_service.insert(user, roles)
    if created_user_roles:
        return Success(detail="user roles updated successfully")
    return Success(detail="user roles already exist")


@router.put(
    "/{user_id}",
    dependencies=[Depends(get_authorized_user(Permission.UPDATE_USER_INFO))],
)
async def put_user(
    user_id: UUID,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> Success:
    """Actualizar usuario.

    Arguments:
        user_id -- identificador de usuario
        user_update -- información base de usuario

    Returns:
        Mensaje de operación exitosa
    """
    user_service.update(user_id, user_update)
    return Success(detail="role updated successfully")


@router.delete(
    "/{user_id}/roles",
    dependencies=[Depends(get_authorized_user(Permission.UNASSIGN_USER_ROLES))],
)
async def delete_user_roles(
    user_id: UUID,
    role_ids: List[UUID] = Query(default=[]),
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> Success:
    """Borra roles de usuario.

    Arguments:
        user_id -- identificador de usuario
        role_ids -- identificadores de roles a borrar de usuario

    Returns:
        Mensaje de operación exitosa
    """
    user = user_service.get_by(user_id)
    roles = role_service.filter_by(role_ids)
    user_role_service.delete(user, roles)
    return Success(detail="roles deleted successfully")


@router.put(
    "/{user_id}/password",
    dependencies=[Depends(get_authorized_user(Permission.UPDATE_USER_PRIVATE))],
)
async def put_user_password(
    user_id: UUID,
    update_new_password: UserNewPassword,
    user_service: UserService = Depends(get_user_service),
) -> Success:
    """Actualizar contraseña usuario.

    Arguments:
        user_id -- identificador de usuario
        update_new_password -- información con nueva contraseña de usuario

    Returns:
        Mensaje de operación exitosa
    """
    user: UserPublic = user_service.get_by(user_id)
    user_service.update(user.id, update_new_password)
    return Success(detail="password updated successfully")

"""Router para endpoints de roles."""
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.dependencies import (
    get_authorized_user,
    get_permission_service,
    get_role_permission_service,
    get_role_service,
    get_user_role_service,
)
from app.enums.permission import Permission
from app.routers import RouterException
from app.schemas.common import Created, Success
from app.schemas.role import Role, RoleBase
from app.schemas.user import UserPublic
from app.services.permission import PermissionService
from app.services.role import RoleService
from app.services.role_permission import RolePermissionService
from app.services.user_role import UserRoleService

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
)


@router.get(
    "/{role_id}",
    dependencies=[Depends(get_authorized_user(Permission.GET_ROLE))],
)
async def get_role(
    role_id: UUID, role_service: RoleService = Depends(get_role_service)
) -> Role:
    """Obtiene rol.

    Arguments:
        role_id -- id de role

    Keyword Arguments:
        current_role -- Usuario activo logeado y con permisos.
            (default: {Depends(Permission.get_role_info)})

    Returns:
        Información de usuario
    """
    role: Role = role_service.get_by(role_id)
    return role


@router.post(
    "/",
    dependencies=[Depends(get_authorized_user(Permission.CREATE_NEW_ROLE))],
    status_code=HTTPStatus.CREATED,
)
async def post_role(
    role_base: RoleBase,
    role_service: RoleService = Depends(get_role_service),
) -> Created:
    """Crear rol.

    Arguments:
        role_base -- información base de rol

    Returns:
        Mensaje de operación exitosa con el identificador de rol creado
    """
    role_id = role_service.insert(role_base)
    return Created(detail="role created successfully", id=role_id)


@router.put(
    "/{role_id}",
    dependencies=[Depends(get_authorized_user(Permission.UPDATE_ROLE))],
)
async def put_role(
    role_id: UUID,
    role_base: RoleBase,
    role_service: RoleService = Depends(get_role_service),
) -> Success:
    """Actualizar rol.

    Arguments:
        role_id -- identificador de rol
        role_base -- información base de rol

    Returns:
        Mensaje de operación exitosa
    """
    role_service.update(role_id, role_base)
    return Success(detail="role updated successfully")


@router.get(
    "/",
    dependencies=[Depends(get_authorized_user(Permission.GET_ALL_ROLES))],
)
async def get_roles(
    role_service: RoleService = Depends(get_role_service),
) -> List[Role]:
    """Obtener lista de roles disponibles.

    Returns:
        Lista de roles disponibles
    """
    return role_service.list()


@router.put(
    "/{role_id}/permissions",
    dependencies=[Depends(get_authorized_user(Permission.ASSIGN_ROLE_PERMISSIONS))],
)
async def put_role_permission(
    role_id: UUID,
    permission_ids: List[str],
    role_service: RoleService = Depends(get_role_service),
    permission_service: PermissionService = Depends(get_permission_service),
    role_permission_service: RolePermissionService = Depends(
        get_role_permission_service
    ),
) -> Success:
    """Agregar permisos a rol.

    Arguments:
        role_id -- identificador de rol
        permission_ids -- Lista de identificadores de permisos a agregar a rol

    Returns:
        Mensaje de operación exitosa
    """
    role = role_service.get_by(role_id)
    permissions = permission_service.filter_by(set(permission_ids))
    role_permissions_created = role_permission_service.insert(role, permissions)
    if role_permissions_created:
        return Success(detail="permissions updated successfully")
    return Success(detail="permissions already exist")


@router.delete(
    "/{role_id}/permissions",
    tags=["roles"],
    dependencies=[Depends(get_authorized_user(Permission.UNASSIGN_ROLE_PERMISSIONS))],
)
async def delete_role_permissions(
    role_id: UUID,
    permission_ids: List[str] = Query(default=[]),
    role_service: RoleService = Depends(get_role_service),
    permission_service: PermissionService = Depends(get_permission_service),
    role_permission_service: RolePermissionService = Depends(
        get_role_permission_service
    ),
) -> Success:
    """Borrar permisos a rol.

    Arguments:
        role_id -- identificador de rol
        permission_ids -- Lista de identificadores de permisos a borrar a rol

    Returns:
        Mensaje de operación exitosa
    """
    role = role_service.get_by(role_id)
    permissions = permission_service.filter_by(set(permission_ids))
    role_permission_service.delete(role, permissions)
    return Success(detail="permissions deleted successfully")


@router.delete("/{role_id}")
async def delete_role(
    role_id: UUID,
    current_user: UserPublic = Depends(get_authorized_user(Permission.DELETE_ROLE)),
    role_service: RoleService = Depends(get_role_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> Success:
    """Borrar rol.

    Arguments:
        role_id -- identificador de rol

    Returns:
        Mensaje de operación exitosa
    """
    user_roles = user_role_service.get_by(current_user)
    for user_role in user_roles:
        if user_role.role_id == role_id:
            raise RouterException(
                error_type=RouterException.Type.FORBIDDEN,
                message=f"cannot remove role {role_id}, is assigned to logged user",
            )
    role_service.delete(role_id)
    return Success(detail="role deleted successfully")

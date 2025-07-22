"""Router para endpoints de permisos."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_authorized_user,
    get_permission_service,
    get_role_permission_service,
    get_role_service,
)
from app.enums.permission import Permission as PermissionEnum
from app.schemas.permission import Permission
from app.schemas.role_permission import RolePermissionDetail
from app.services.permission import PermissionService
from app.services.role import RoleService
from app.services.role_permission import RolePermissionService

router = APIRouter(
    prefix="/permissions",
    tags=["permissionsvolumenes_test"],
)


@router.get(
    "/",
    dependencies=[Depends(get_authorized_user(PermissionEnum.GET_ALL_PERMISSIONS))],
)
async def get_permissions(
    permission_service: PermissionService = Depends(get_permission_service),
) -> List[Permission]:
    """Obtener lista de permisos existentes.

    Returns:
        Lista de permisos existentes
    """
    return permission_service.list()


@router.get(
    "/role/{role_id}",
    dependencies=[Depends(get_authorized_user(PermissionEnum.GET_ROLES))],
)
async def get_role_permissions(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
    role_permission_service: RolePermissionService = Depends(
        get_role_permission_service
    ),
) -> RolePermissionDetail:
    """Obtener permisos asignados a rol.

    Arguments:
        role_id -- identificador de rol

    Returns:
        Detalle de permisos de rol
    """
    role = role_service.get_by(role_id)
    role_permissions = role_permission_service.get_by(role)
    return RolePermissionDetail(
        role_name=role.role_name,
        permissions=[
            role_permission.permission for role_permission in role_permissions
        ],
    )

"""Dependencias."""
from typing import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from redbird.repos import SQLRepo
from sqlalchemy.orm import Session

from app.enums.permission import Permission as PermissionEnum
from app.models.permission import Permission as PermissionORM
from app.models.role import Role as RoleORM
from app.models.role_permission import RolePermission as RolePermissionORM
from app.models.user import User as UserORM
from app.models.user_role import UserRole as UserRoleORM
from app.repositories.sqlalchemy import get_session
from app.routers import RouterException
from app.schemas.permission import Permission
from app.schemas.role import Role
from app.schemas.role_permission import RolePermission
from app.schemas.token import Credentials
from app.schemas.user import UserPublic
from app.schemas.user_role import UserRole
from app.services.permission import PermissionService
from app.services.role import RoleService
from app.services.role_permission import RolePermissionService
from app.services.user import UserService
from app.services.user_role import UserRoleService

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")

DbSession = get_session()


def get_db_session() -> Session:
    """Generar session de base de datos DB.

    Returns:
        session de base de datos "DB"
    """
    return DbSession()


def get_role_service(session: Session = Depends(get_db_session)) -> RoleService:
    """Obtener servicio de roles.

    Returns:
        servicio de roles
    """
    return RoleService(
        repository=SQLRepo(
            model=Role,
            orm=RoleORM,
            id_field="id",
            session=session,
        )
    )


def get_permission_service(
    session: Session = Depends(get_db_session),
) -> PermissionService:
    """Obtener servicio de permisos.

    Returns:
        servicio de permisos
    """
    return PermissionService(
        repository=SQLRepo(
            model=Permission,
            orm=PermissionORM,
            id_field="id",
            session=session,
        ),
    )


def get_role_permission_service(
    session: Session = Depends(get_db_session),
) -> RolePermissionService:
    """Obtener servicio de relación de roles y permisos.

    Returns:
        servicio de relación de roles y permisos
    """
    return RolePermissionService(
        repository=SQLRepo(
            model=RolePermission,
            orm=RolePermissionORM,
            session=session,
        ),
    )


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    """Obtener servicio de usuarios.

    Returns:
        servicio de usuarios
    """
    return UserService(
        repository=SQLRepo(
            orm=UserORM,
            id_field="id",
            session=session,
        ),
    )


def get_user_role_service(
    session: Session = Depends(get_db_session),
) -> UserRoleService:
    """Obtener servicio de relación de usuarios y roles.

    Returns:
        servicio de relación de usuarios y roles
    """
    return UserRoleService(
        repository=SQLRepo(
            model=UserRole,
            orm=UserRoleORM,
            session=session,
        ),
    )


async def get_credentials(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Credentials:
    """Obtener credenciales desde el FormData de solicitud.

    Keyword Arguments:
        form_data -- FormData de solicitud
    Returns:
        Credenciales
    """
    return Credentials(username=form_data.username, password=form_data.password)


async def get_current_active_user(
    token: str = Depends(OAUTH2_SCHEME),
    user_service: UserService = Depends(get_user_service),
) -> UserPublic:
    """Obtener usuario en sesión a partir de token.

    Keyword Arguments:
        token -- token con la información codificada

    Raises:
        RouterException: FORBIDDEN si el usuario logueada está deshabilitado

    Returns:
        usuario logueado
    """
    current_user: UserPublic = user_service.get_by(token)
    if current_user.disabled:
        raise RouterException(
            error_type=RouterException.Type.FORBIDDEN, message="inactive user"
        )
    return current_user


def get_authorized_user(
    permission_id: PermissionEnum,
) -> Callable[[UserPublic], UserPublic]:
    """Obtener dependencia para autorizar usuario si tiene asignado permiso.

    Arguments:
        permission_id -- identificador de permiso a revisar

    Returns:
        Dependencia para autorizar si el usuario tiene permiso
    """

    def wrapper(
        user: UserPublic = Depends(get_current_active_user),
        user_role_service: UserRoleService = Depends(get_user_role_service),
        role_permission_service: RolePermissionService = Depends(
            get_role_permission_service
        ),
    ) -> UserPublic:
        """Autorizar si el usuario tiene permiso.

        Keyword Arguments:
            user -- usuario a autorizar (default: {Depends(get_current_active_user)})

        Raises:
            RouterException: FORBIDDEN si el usuario no tiene asignado el permiso

        Returns:
            usuario autorizado
        """
        user_roles = user_role_service.get_by(user)
        role_ids = [user_role.role_id for user_role in user_roles]
        role_permissions = role_permission_service.filter_by(role_ids, [permission_id])
        if role_permissions:
            return user
        raise RouterException(
            error_type=RouterException.Type.FORBIDDEN,
            message="user does not have permission",
        )

    return wrapper

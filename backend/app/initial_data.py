"""Insertar datos iniciales."""
from redbird.repos.sqlalchemy import SQLRepo
from sqlalchemy.orm import Session

from app.data.permissions import initial_permissions
from app.data.roles import initial_roles
from app.data.roles_permissions import initial_role_permissions
from app.data.users import initial_users
from app.data.users_roles import initial_users_roles
from app.models.permission import Permission as PermissionORM
from app.models.role import Role as RoleORM
from app.models.role_permission import RolePermission as RolePermissionORM
from app.models.user import User as UserORM
from app.models.user_role import UserRole as UserRoleORM
from app.repositories.sqlalchemy import get_session
from app.schemas.permission import Permission
from app.schemas.role import Role
from app.schemas.role_permission import RolePermissionBase
from app.schemas.user import NewUser
from app.schemas.user_role import UserRoleBase


def insert_permissions(session: Session) -> None:
    """Insertar permisos iniciales.

    Arguments:
        session -- Session de base de datos
    """
    repo = SQLRepo(
        model=Permission,
        orm=PermissionORM,
        id_field="id",
        session=session,
    )
    for permission in initial_permissions:
        if not repo.filter_by(id=permission["id"]).count():
            repo.add(Permission(**permission), if_exists="ignore")


def insert_roles(session: Session) -> None:
    """Insertar roles iniciales.

    Arguments:
        session -- Session de base de datos
    """
    repo = SQLRepo(
        model=Role,
        orm=RoleORM,
        id_field="id",
        session=session,
    )
    for role in initial_roles:
        if not repo.filter_by(id=role["id"]).count():
            repo.add(Role(**role), if_exists="ignore")


def insert_roles_permissions(session: Session) -> None:
    """Insertar relaciones de roles y permissions iniciales.

    Arguments:
        session -- Session de base de datos
    """
    repo = SQLRepo(
        model=RolePermissionBase,
        orm=RolePermissionORM,
        session=session,
    )
    for role_permission in initial_role_permissions:
        if not repo.filter_by(
            role_id=role_permission["role_id"],
            permission_id=role_permission["permission_id"],
        ).count():
            repo.add(RolePermissionBase(**role_permission), if_exists="ignore")


def insert_users(session: Session) -> None:
    """Insertar usuarios iniciales.

    Arguments:
        session -- Session de base de datos
    """
    repo = SQLRepo(
        model=NewUser,
        orm=UserORM,
        session=session,
    )
    for user in initial_users:
        if not repo.filter_by(id=user["id"]).count():
            repo.add(NewUser(**user), if_exists="ignore")


def insert_users_roles(session: Session) -> None:
    """Insertar relaciones de users y roles iniciales.

    Arguments:
        session -- Session de base de datos
    """
    repo = SQLRepo(
        model=UserRoleBase,
        orm=UserRoleORM,
        session=session,
    )
    for user_role in initial_users_roles:
        if not repo.filter_by(
            user_id=user_role["user_id"],
            role_id=user_role["role_id"],
        ).count():
            repo.add(UserRoleBase(**user_role), if_exists="ignore")


if __name__ == "__main__":
    DbSession = get_session()
    session = DbSession()
    insert_permissions(session)
    insert_roles(session)
    insert_roles_permissions(session)
    insert_users(session)
    insert_users_roles(session)

"""Servicio de relación de roles y sus permisos."""
from typing import List, Optional
from uuid import UUID

from redbird.oper import in_

from app.enums.permission import Permission as PermissionEnum
from app.schemas.permission import Permission
from app.schemas.role import Role
from app.schemas.role_permission import RolePermission, RolePermissionBase
from app.services import BaseService, ServiceException


class RolePermissionService(BaseService):
    """Servicio de relación de roles y sus permisos."""

    def insert(self, role: Role, permissions: List[Permission]) -> bool:
        """Agregar permisos a rol.

        Arguments:
            role -- rol donde agregar
            permissions -- permisos a agregar

        Returns:
            True si permisos fueron agregados, False en caso contrario
        """
        role_permissions = self.repository.filter_by(role_id=role.id).all()
        permission_ids = [
            role_permission.permission_id for role_permission in role_permissions
        ]

        new_role_permissions = [
            RolePermissionBase(role_id=role.id, permission_id=permission.id)
            for permission in permissions
            if permission.id not in permission_ids
        ]
        for new_role_permission in new_role_permissions:
            self.repository.insert(new_role_permission)
        return len(new_role_permissions) > 0

    def get_by(self, role: Role) -> List[RolePermission]:
        """Obtener permisos de rol.

        Arguments:
            role -- rol

        Returns:
            Lista de permisos de rol
        """
        return list(self.repository.filter_by(role_id=role.id).all())

    def filter_by(
        self, role_ids: List[UUID], permission_ids: Optional[List[PermissionEnum]]
    ) -> List[RolePermission]:
        """Filtrar relaciones de roles y sus permisos.

        Arguments:
            role_ids -- identificadores de roles
            permission_ids -- identificadores de permisos

        Returns:
            Lista de roles y sus permisos
        """
        if permission_ids:
            return list(
                self.repository.filter_by(
                    role_id=in_(role_ids),
                    permission_id=in_([id.value for id in permission_ids]),
                ).all()
            )
        return list(self.repository.filter_by(role_id=in_(role_ids)).all())

    def delete(self, role: Role, permissions: List[Permission]) -> None:
        """Borrar permisos de rol.

        Arguments:
            role -- rol donde borrar
            permissions -- permisos a borrar

        Raises:
            ServiceException: NOT_FOUND si algún identificador de permiso no es de rol
        """
        permission_ids = [permission.id for permission in permissions]

        assigned_role_permissions = self.repository.filter_by(
            role_id=role.id, permission_id=in_(permission_ids)
        ).all()
        assigned_permission_ids = {
            role_permission.permission_id
            for role_permission in assigned_role_permissions
        }

        unassigned_permissions_ids = [
            permission_id
            for permission_id in permission_ids
            if permission_id not in assigned_permission_ids
        ]
        if unassigned_permissions_ids:
            raise ServiceException(
                error_type=ServiceException.Type.NOT_FOUND,
                message="permissions not assigned to role: "
                + ", ".join(unassigned_permissions_ids),
            )
        self.repository.filter_by(
            role_id=role.id, permission_id=in_(permission_ids)
        ).delete()

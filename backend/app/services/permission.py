"""Servicio de permisos."""
from typing import List, Set

from redbird.oper import in_

from app.schemas.permission import Permission
from app.services import BaseService, ServiceException


class PermissionService(BaseService):
    """Servicio de permisos."""

    def list(self) -> List[Permission]:
        """Listar permisos disponibles.

        Returns:
            Lista de permisos
        """
        return list(self.repository)

    def filter_by(self, permission_ids: Set[str]) -> List[Permission]:
        """Filtrar permisos.

        Arguments:
            permission_ids -- identificadores de permisos

        Raises:
            ServiceException: INVALID_INPUT si la lista de permisos está vacía
            ServiceException: NOT_FOUND si algún identificador de permiso no existe

        Returns:
            Lista de permisos
        """
        if not permission_ids:
            raise ServiceException(
                error_type=ServiceException.Type.INVALID_INPUT,
                message="permission list is empty",
            )

        permissions = self.repository.filter_by(id=in_(permission_ids)).all()
        existing_permission_ids = {permission.id for permission in permissions}

        non_existing_permission_ids = [
            permission_id
            for permission_id in permission_ids
            if permission_id not in existing_permission_ids
        ]
        if non_existing_permission_ids:
            raise ServiceException(
                error_type=ServiceException.Type.NOT_FOUND,
                message="permissions not found: "
                + ", ".join(non_existing_permission_ids),
            )
        return list(permissions)

"""Servicio de relación de usuarios y sus roles."""
from typing import List

from multimethod import multimethod
from redbird.oper import in_

from app.schemas.role import Role
from app.schemas.user import UserPublic
from app.schemas.user_role import UserRole, UserRoleBase
from app.services import BaseService, ServiceException


class UserRoleService(BaseService):
    """Servicio de relación de usuarios y sus roles."""

    def insert(self, user: UserPublic, roles: List[Role]) -> bool:
        """Agregar roles a usuario.

        Arguments:
            user -- usuario donde agregar
            roles -- roles a agregar

        Returns:
            True si roles fueron agregados, False en caso contrario
        """
        user_roles = self.repository.filter_by(user_id=user.id).all()
        roles_ids = [user_role.role_id for user_role in user_roles]

        new_user_roles = [
            UserRoleBase(user_id=user.id, role_id=role.id)
            for role in roles
            if role.id not in roles_ids
        ]
        for new_user_role in new_user_roles:
            self.repository.insert(new_user_role)
        return len(new_user_roles) > 0

    @multimethod
    def get_by(self, user: UserPublic) -> List[UserRole]:
        """Obtener roles de usuario.

        Arguments:
            user -- usuario

        Returns:
            Lista de roles de usuario
        """
        return list(self.repository.filter_by(user_id=user.id).all())

    @get_by.register
    def _(self, role: Role) -> List[UserRole]:
        """Obtener usuarios de rol.

        Arguments:
            role -- rol

        Returns:
            Lista de usuarios de rol
        """
        return list(self.repository.filter_by(role_id=role.id).all())

    def delete(self, user: UserPublic, roles: List[Role]) -> None:
        """Borrar roles de usuario.

        Arguments:
            user -- usuario donde borrar
            roles -- roles a borrar

        Raises:
            ServiceException: NOT_FOUND si algún identificador de rol no es de usuario
        """
        role_ids = [role.id for role in roles]

        assigned_user_roles = self.repository.filter_by(
            user_id=user.id, role_id=in_(role_ids)
        ).all()
        assigned_role_ids = {user_role.role_id for user_role in assigned_user_roles}

        unassigned_roles_ids = [
            str(role_id) for role_id in role_ids if role_id not in assigned_role_ids
        ]
        if unassigned_roles_ids:
            raise ServiceException(
                error_type=ServiceException.Type.NOT_FOUND,
                message="roles not assigned to user: "
                + ", ".join(sorted(unassigned_roles_ids)),
            )
        self.repository.filter_by(user_id=user.id, role_id=in_(role_ids)).delete()

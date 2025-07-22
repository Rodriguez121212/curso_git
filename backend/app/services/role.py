"""Servicio de roles."""
import uuid
from typing import List

from multimethod import multimethod
from redbird.oper import in_, not_equal

from app.schemas.role import Role, RoleBase
from app.services import BaseService, ServiceException


class RoleService(BaseService):
    """Servicio de roles."""

    def insert(self, role_base: RoleBase) -> uuid.UUID:
        """Crear rol.

        Arguments:
            role_base -- informacion de rol

        Returns:
            identificador de rol creado
        """
        if self.repository.filter_by(role_name=role_base.role_name).count():
            raise ServiceException(
                error_type=ServiceException.Type.ALREADY_EXIST,
                message=f"role name {role_base.role_name} is already taken",
            )
        id = uuid.uuid4()
        role = Role(id=id, role_name=role_base.role_name)
        self.repository.insert(role)
        return id

    def list(self) -> List[Role]:
        """Listar roles disponibles.

        Returns:
            Lista de roles
        """
        return list(self.repository)

    @multimethod
    def get_by(self, role_id: uuid.UUID) -> Role:
        """Obtener rol.

        Arguments:
            role_id -- identificador de rol

        Raises:
            ServiceException: NOT FOUND si el rol no existe

        Returns:
            Rol
        """
        role: Role = self.repository.get_by(role_id).first()

        if not role:
            raise ServiceException(
                error_type=ServiceException.Type.NOT_FOUND,
                message=f"role {role_id} not found",
            )
        return role

    @get_by.register
    def _(self, role_name: str) -> Role:
        """Obtener rol.

        Arguments:
            role_name -- nombre de rol

        Raises:
            ServiceException: NOT FOUND si el rol no existe

        Returns:
            Rol
        """
        role: Role = self.repository.filter_by(role_name=role_name).first()

        if not role:
            raise ServiceException(
                error_type=ServiceException.Type.NOT_FOUND,
                message=f"role {role_name} not found",
            )
        return role

    def filter_by(self, role_ids: List[uuid.UUID]) -> List[Role]:
        """Filtrar roles.

        Arguments:
            role_ids -- identificadores de roles

        Raises:
            ServiceException: NOT_FOUND si algún identificador de rol no existe

        Returns:
            Lista de roles
        """
        if not role_ids:
            return []
        roles = self.repository.filter_by(id=in_(set(role_ids))).all()
        existing_role_ids = {role.id for role in roles}

        non_existing_role_ids = [
            str(role_id) for role_id in role_ids if role_id not in existing_role_ids
        ]
        if non_existing_role_ids:
            raise ServiceException(
                error_type=ServiceException.Type.NOT_FOUND,
                message="roles not found: " + ", ".join(non_existing_role_ids),
            )
        return list(roles)

    def update(self, role_id: uuid.UUID, role_base: RoleBase) -> None:
        """Actualizar rol.

        Arguments:
            role_id -- identificador de rol
            role_base -- información a actualizar de rol

        Raises:
            ServiceException: NOT_FOUND si el rol no existe
            ServiceException: ALREADY_EXIST si el nombre de rol pertenece a otro rol
        """
        self.get_by(role_id)
        if self.repository.filter_by(
            role_name=role_base.role_name, id=not_equal(role_id)
        ).count():
            raise ServiceException(
                error_type=ServiceException.Type.ALREADY_EXIST,
                message=f"role name {role_base.role_name} is already taken",
            )
        role_dict = role_base.model_dump(exclude_unset=True)
        self.repository.get_by(role_id).update(**role_dict)

    def delete(self, role_id: uuid.UUID) -> None:
        """Borrar rol.

        Arguments:
            role_id -- identificador de rol

        Raises:
            ServiceException: NOT_FOUND si el rol no existe
        """
        self.get_by(role_id)
        self.repository.get_by(role_id).delete()

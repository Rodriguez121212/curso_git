"""Módulo de servicios."""
from redbird.repos import SQLRepo

from app.exceptions import ExceptionBase


class ServiceException(ExceptionBase):
    """Clase de excepciones para errores en algun servicio."""


class BaseService:
    """Base de servicios."""

    repository: SQLRepo

    def __init__(
        self,
        repository: SQLRepo,
    ) -> None:
        """Crear instancia de servicio.

        Arguments:
            repository -- repositorio
        """
        self.repository = repository

    def __del__(self) -> None:
        """Cerrar la sesión asociado a repositorio."""
        self.repository.session.close()

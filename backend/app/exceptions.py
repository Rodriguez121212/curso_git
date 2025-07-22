"""Clase base de excepciones."""
from enum import Enum


class ExceptionBase(Exception):
    """Clase base de excepciones.

    Attributes:
        error_type -- Identificar el tipo de error.
        message -- Mensaje con información de error.
    """

    class Type(Enum):
        """Enumeración de tipo de excepción."""

        UNAUTHORIZED = 1
        FORBIDDEN = 2
        INVALID_INPUT = 3
        NOT_FOUND = 4
        ALREADY_EXIST = 5

    def __init__(self, error_type: Type, message: str = ""):
        """Inicializa la excepción.

        Arguments:
            error_type -- Identificar el tipo de error.

        Keyword Arguments:
            message -- Mensaje con información de error.
        """
        self.error_type = error_type
        self.message = message

        super().__init__(message)

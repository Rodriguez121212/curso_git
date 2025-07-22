"""Esquemas de token."""
from enum import Enum

from pydantic import BaseModel


class Token(BaseModel):
    """Esquema para access token."""

    class Type(Enum):
        """Enumeración de tipo de excepción."""

        BEARER = "bearer"

    access_token: str
    token_type: Type


class TokenData(BaseModel):
    """Esquema para datos en el token."""

    username: str


class Credentials(BaseModel):
    """Esquema para credenciales de login."""

    username: str
    password: str

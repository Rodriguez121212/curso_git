"""Esquemas generales."""
from pydantic import UUID4, BaseModel


class Success(BaseModel):
    """Esquema para respuesta exitosa."""

    detail: str


class Created(BaseModel):
    """Esquema para respuesta exitosa."""

    detail: str
    id: UUID4
